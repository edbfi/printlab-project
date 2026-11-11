"""Validated JSON boundaries and atomic boot-scoped native-uplink storage."""

from dataclasses import asdict
from ipaddress import IPv4Address, IPv4Interface, IPv4Network, IPv6Address
import json
import math
import os
from pathlib import Path
import re
import stat
import uuid

from lease_lifecycle import Identity, Ownership, Snapshot, State, UnsafeState
from lease_validation import Address, NATIVE, Route, endpoint_route, parse_grant

MAX_JSON = 2 * 1024 * 1024
MAC = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}")


def mapping(value):
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        raise UnsafeState("Expected an object with string keys")
    return value


def string(value):
    if not isinstance(value, str) or len(value) > 256:
        raise UnsafeState("Invalid string field")
    return value


def string_flags(value):
    if not isinstance(value, list) or not all(isinstance(flag, str) for flag in value):
        raise UnsafeState("Invalid link flags")
    return value


def integer(value, minimum=0, maximum=2**32 - 1):
    if type(value) is not int or not minimum <= value <= maximum:
        raise UnsafeState("Invalid integer field")
    return value


def boolean(value):
    if type(value) is not bool:
        raise UnsafeState("Invalid boolean field")
    return value


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise UnsafeState("Invalid clock field")
    return float(value)


def loads(raw):
    if len(raw) > MAX_JSON:
        raise UnsafeState("Oversized JSON input")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise UnsafeState("Duplicate JSON key")
            result[key] = value
        return result

    try:
        return json.loads(raw, object_pairs_hook=pairs)
    except (ValueError, RecursionError) as error:
        raise UnsafeState("Invalid JSON input") from error


def array(raw):
    values = loads(raw)
    if not isinstance(values, list):
        raise UnsafeState("Expected a JSON array")
    return [mapping(value) for value in values]


def identity(value):
    value = mapping(value)
    mac = string(value["mac"])
    if not MAC.fullmatch(mac):
        raise UnsafeState("Invalid interface MAC")
    return Identity(integer(value["index"], 1), mac)


def parse_snapshot(link_json, address_json, route_json):
    """Reject incomplete/unsupported resource shapes instead of omitting them."""
    links = array(link_json)
    names = [string(link["ifname"]) for link in links]
    if len(names) != len(set(names)):
        raise UnsafeState("Duplicate link names")
    native = [link for link in links if link["ifname"] == NATIVE]
    native_id = None
    carrier = False
    if native:
        link = native[0]
        native_id = identity({"index": link["ifindex"], "mac": link["address"]})
        flags = string_flags(link["flags"])
        # A down link is ineligible for grants, but cleanup must still work.
        carrier = "UP" in flags and "LOWER_UP" in flags
    addresses = []
    native_ipv6 = False
    address_names = set()
    for link in array(address_json):
        name = string(link["ifname"])
        if name not in names or name in address_names:
            raise UnsafeState("Address/link snapshots disagree")
        address_names.add(name)
        if integer(link["ifindex"], 1) != integer(links[names.index(name)]["ifindex"], 1):
            raise UnsafeState("Address interface identity changed during query")
        infos = link["addr_info"]
        if not isinstance(infos, list):
            raise UnsafeState("Missing address list")
        for value in infos:
            value = mapping(value)
            family = value["family"]
            local = string(value["local"])
            if "peer" in value or (family == "inet" and value.get("address", local) != local):
                raise UnsafeState("Peer address shapes are not supported")
            if family == "inet":
                prefix = integer(value["prefixlen"], 0, 32)
                addresses.append(Address(name, IPv4Interface(f"{local}/{prefix}"),
                                         string(value.get("label", ""))))
            elif family == "inet6":
                IPv6Address(local)
                integer(value["prefixlen"], 0, 128)
                native_ipv6 |= name == NATIVE
            else:
                raise UnsafeState("Unsupported address family")
    # The all-family ip-address command includes even addressless links.
    if address_names != set(names):
        raise UnsafeState("Incomplete all-family address snapshot")
    routes = []
    known = {"dst", "gateway", "dev", "protocol", "scope", "prefsrc", "metric",
             "flags", "type", "table"}
    for value in array(route_json):
        if set(value) - known:
            raise UnsafeState("Unsupported route attributes")
        flags = value.get("flags", [])
        if not isinstance(flags, list) or any(flag not in ("linkdown",) for flag in flags):
            raise UnsafeState("Unsupported route flags")
        destination = string(value["dst"])
        destination = "0.0.0.0/0" if destination == "default" else destination
        kind = string(value.get("type", "unicast"))
        if kind not in ("unicast", "local", "broadcast", "unreachable", "blackhole", "prohibit", "throw"):
            raise UnsafeState("Unsupported route kind")
        device = string(value.get("dev", ""))
        if device and device not in names:
            raise UnsafeState("Route refers to a missing interface")
        protocol = value.get("protocol", "boot")
        if type(protocol) is int:
            protocol = str(integer(protocol, 0, 255))
        protocol = string(protocol)
        table = value.get("table", "main")
        if type(table) is int:
            table = str(integer(table))
        table = {"254": "main", "255": "local", "253": "default"}.get(string(table), table)
        scope = string(value.get("scope", "global"))
        if scope not in ("global", "link", "host"):
            raise UnsafeState("Unsupported route scope")
        gateway = None if "gateway" not in value else IPv4Address(string(value["gateway"]))
        source = None if "prefsrc" not in value else IPv4Address(string(value["prefsrc"]))
        if device == NATIVE:
            expected_scope = "host" if kind == "local" else "link" if kind == "broadcast" or gateway is None else "global"
            if scope != expected_scope:
                raise UnsafeState("Unexpected native route scope")
        routes.append(Route(IPv4Network(destination, strict=True), device, protocol, kind,
                            gateway, table, integer(value.get("metric", 0)), source))
    return Snapshot(native_id, carrier, native_ipv6, tuple(addresses), tuple(routes))


def check_rules(raw):
    expected = ((0, "local"), (32766, "main"), (32767, "default"))
    rows = array(raw)
    if len(rows) != 3:
        raise UnsafeState("Unexpected IPv4 policy rules")
    found = []
    for row in rows:
        if set(row) - {"priority", "src", "table", "protocol"} or row.get("src") != "all":
            raise UnsafeState("Unsupported policy rule")
        table = row.get("table")
        if type(table) is int:
            table = str(integer(table))
        table = string(table)
        table = {"255": "local", "254": "main", "253": "default"}.get(table, table)
        found.append((integer(row["priority"]), table))
    if tuple(sorted(found)) != expected:
        raise UnsafeState("Unexpected IPv4 policy rule order")


def encode_state(state):
    result = asdict(state)
    if state.owned is not None:
        lease = state.owned.lease
        result["owned"]["endpoint"] = None if state.owned.endpoint is None else str(state.owned.endpoint)
        result["owned"]["lease"] = {"address": str(lease.address), "gateway": str(lease.gateway),
                                    "server": str(lease.server), "lifetime": lease.lifetime}
    return result


def decode_state(value, boot):
    value = mapping(value)
    if set(value) != {"generation", "last_receipt", "owned", "active"}:
        raise UnsafeState("Unexpected state shape")
    generation = string(value["generation"])
    if generation and not re.fullmatch(re.escape(boot) + r":[0-9a-f]{32}", generation):
        raise UnsafeState("State belongs to another boot or invalid generation")
    active = boolean(value["active"])
    if not generation and (active or value["owned"] is not None):
        raise UnsafeState("Uninitialized generation owns resources")
    owned = None
    if value["owned"] is not None:
        data = mapping(value["owned"])
        if set(data) != {"lease", "identity", "expires", "ready", "endpoint"}:
            raise UnsafeState("Unexpected ownership shape")
        fields = mapping(data["lease"])
        if set(fields) != {"address", "gateway", "server", "lifetime"}:
            raise UnsafeState("Unexpected saved lease shape")
        address = IPv4Interface(string(fields["address"]))
        lease = parse_grant({
            "interface": NATIVE, "protocol": "dhcp", "reason": "BOUND",
            "if_configured": "false", "ifcarrier": "up", "new_ip_address": str(address.ip),
            "new_subnet_mask": str(address.netmask), "new_routers": string(fields["gateway"]),
            "new_dhcp_server_identifier": string(fields["server"]),
            "new_dhcp_lease_time": str(integer(fields["lifetime"], 120, 86400)),
        })
        endpoint = None if data["endpoint"] is None else IPv4Address(string(data["endpoint"]))
        endpoint_route(lease, endpoint)  # validate persisted deletion authority too
        owned = Ownership(lease, identity(data["identity"]), number(data["expires"]),
                          boolean(data["ready"]), endpoint)
    return State(generation, number(value["last_receipt"]), owned, active)


def secure_parents(path):
    """Production entry point checks fixed installation/config/runtime parents."""
    for parent in (path, *path.parents):
        info = parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise UnsafeState(f"Unsafe root-owned directory: {parent}")


def read_private(path, owner=0):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != owner or info.st_mode & 0o022:
            raise UnsafeState("Unsafe root-owned input file")
        raw = stream.read(MAX_JSON + 1)
    return loads(raw)


class StateStore:
    def __init__(self, directory: Path, boot: str, owner=0):
        self.directory = directory
        self.boot = boot
        self.owner = owner
        info = directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != owner or info.st_mode & 0o022:
            raise UnsafeState("Unsafe runtime directory")

    def read(self):
        try:
            return decode_state(read_private(self.directory / "state.json", self.owner), self.boot)
        except FileNotFoundError:
            return State("", 0)

    def atomic(self, name, value, mode):
        if name not in ("state.json", "eligible.json"):
            raise UnsafeState("Unexpected state filename")
        temporary = self.directory / f".{name}.{uuid.uuid4().hex}"
        try:
            descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, mode)
            with os.fdopen(descriptor, "w") as stream:
                os.fchmod(stream.fileno(), mode)
                json.dump(value, stream, allow_nan=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.directory / name)
            descriptor = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        finally:
            temporary.unlink(missing_ok=True)

    def write(self, state):
        # Validate our own serialization as well as subsequent reads.
        value = encode_state(state)
        decode_state(value, self.boot)
        self.atomic("state.json", value, 0o600)

    def invalidate(self):
        (self.directory / "eligible.json").unlink(missing_ok=True)
