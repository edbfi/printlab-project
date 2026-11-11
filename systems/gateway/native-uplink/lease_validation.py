"""Pure pre-assignment checks for the native DHCP hook.

No command execution or networking lives here. Passing these checks does not
authorize installation: the caller must also establish callback freshness,
identity, serialization, remaining lifetime, and safe address/route ownership.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Interface, IPv4Network

NATIVE = "enp1s0"
LABEL = "enp1s0:uplink"
ROUTE_PROTOCOL = "242"
GRANT_REASONS = frozenset({"BOUND", "RENEW", "REBIND", "REBOOT"})
# Protect established resources even while their interfaces are temporarily absent.
FIXED_PROTECTED = tuple(IPv4Network(value) for value in (
    "127.0.0.0/8", "10.113.128.0/20", "10.136.44.0/22",
    "10.255.255.0/24", "192.168.77.0/24", "172.17.0.0/16",
))
FORBIDDEN = tuple(IPv4Network(value) for value in (
    "0.0.0.0/8", "127.0.0.0/8", "169.254.0.0/16", "224.0.0.0/4", "240.0.0.0/4",
))
VPN_CATCHALLS = frozenset({IPv4Network("0.0.0.0/1"), IPv4Network("128.0.0.0/1")})


class RejectedLease(ValueError):
    """Input does not establish an eligible lease; do not assign or extend it."""


@dataclass(frozen=True)
class Lease:
    address: IPv4Interface
    gateway: IPv4Address
    server: IPv4Address
    lifetime: int


@dataclass(frozen=True)
class Address:
    interface: str
    address: IPv4Interface
    label: str


@dataclass(frozen=True)
class Route:
    destination: IPv4Network
    interface: str
    protocol: str
    kind: str = "unicast"
    gateway: IPv4Address | None = None
    table: str = "main"
    metric: int = 0
    preferred_source: IPv4Address | None = None


def _field(environment: Mapping[str, str], name: str) -> str:
    value = environment.get(name, "")
    if not value or len(value) > 256 or value != value.strip():
        raise RejectedLease(f"Missing, oversized or padded field: {name}")
    return value


def _unicast(address: IPv4Address) -> bool:
    return not any(address in prefix for prefix in FORBIDDEN)


def parse_grant(environment: Mapping[str, str]) -> Lease:
    """Parse only a native, nonconfiguring DHCP grant; ignore DNS/host settings."""
    if (environment.get("interface") != NATIVE
            or environment.get("protocol") != "dhcp"
            or environment.get("if_configured") != "false"
            or environment.get("ifcarrier") != "up"
            or environment.get("reason") not in GRANT_REASONS):
        raise RejectedLease("Not an eligible nonconfiguring native DHCP callback")
    for option in ("new_classless_static_routes", "new_ms_classless_static_routes",
                   "new_static_routes"):
        # Presence, even an empty value, is not silently interpreted as absent.
        if option in environment:
            raise RejectedLease(f"Unsupported DHCP route option: {option}")
    try:
        ip = IPv4Address(_field(environment, "new_ip_address"))
        mask = _field(environment, "new_subnet_mask")
        # Require a dotted netmask; IPv4Network otherwise also accepts host masks.
        mask_number = int(IPv4Address(mask))
        prefix = mask_number.bit_count()
        contiguous_mask = ((2**32 - 1) << (32 - prefix)) & (2**32 - 1)
        if not 8 <= prefix <= 30 or mask_number != contiguous_mask:
            raise RejectedLease("Netmask must be contiguous and between /8 and /30")
        address = IPv4Interface(f"{ip}/{prefix}")
        routers = _field(environment, "new_routers").split()
        if len(routers) != 1:
            raise RejectedLease("Exactly one DHCP router is required")
        gateway = IPv4Address(routers[0])
        server = IPv4Address(_field(environment, "new_dhcp_server_identifier"))
        duration = _field(environment, "new_dhcp_lease_time")
        if not duration.isascii() or not duration.isdecimal():
            raise RejectedLease("Lease duration must be an unsigned decimal integer")
        lifetime = int(duration)
    except RejectedLease:
        raise
    except ValueError as error:
        raise RejectedLease(str(error)) from error
    if not 120 <= lifetime <= 86400:
        raise RejectedLease("Lease duration must be finite, between 120 and 86400 seconds")
    network = address.network
    if (any(network.overlaps(prefix) for prefix in FORBIDDEN)
            or ip in (network.network_address, network.broadcast_address)
            or gateway not in network
            or gateway in (ip, network.network_address, network.broadcast_address)
            or not _unicast(server) or server == ip):
        raise RejectedLease("Invalid lease address, subnet, gateway or server")
    if server in (network.network_address, network.broadcast_address):
        raise RejectedLease("DHCP server is a subnet boundary address")
    return Lease(address, gateway, server, lifetime)


def public_endpoint(endpoint: object) -> bool:
    """ipaddress.is_global alone also accepts multicast; require public unicast."""
    return (isinstance(endpoint, IPv4Address) and endpoint.is_global
            and not endpoint.is_multicast)


def endpoint_route(lease: Lease, endpoint: IPv4Address | None) -> Route | None:
    """Exact optional Windscribe pin authorized by root config, never DHCP data.

    Only the observed boot-protocol, main-table /32 through this lease's gateway
    is recognized. It has no preferred source or metric. A different shape is
    deliberately rejected until separately inspected and authorized.
    """
    if endpoint is None:
        return None
    if not public_endpoint(endpoint):
        raise RejectedLease("VPN endpoint must be a public IPv4 address")
    if endpoint in lease.address.network or endpoint == lease.server:
        raise RejectedLease("VPN endpoint conflicts with lease subnet or DHCP server")
    return Route(IPv4Network(f"{endpoint}/32"), NATIVE, "boot", gateway=lease.gateway)


def _owned_route(route: Route, owned: Lease | None) -> bool:
    if owned is None or route.interface != NATIVE:
        return False
    if route.protocol == "kernel" and route.table == "local":
        if route.kind == "local":
            return route.destination == IPv4Network(f"{owned.address.ip}/32")
        if route.kind == "broadcast":
            return route.destination in (
                IPv4Network(f"{owned.address.network.network_address}/32"),
                IPv4Network(f"{owned.address.network.broadcast_address}/32"),
            )
    if route.protocol != ROUTE_PROTOCOL or route.table != "main" or route.kind != "unicast":
        return False
    if route.destination.prefixlen == 0:
        return (route.gateway == owned.gateway and route.metric == 100
                and route.preferred_source == owned.address.ip)
    if route.destination == owned.address.network:
        return route.gateway is None
    if route.destination == IPv4Network(f"{owned.server}/32"):
        return route.gateway == owned.gateway
    return False


def check_overlap(lease: Lease, addresses: Sequence[Address], routes: Sequence[Route],
                  owned: Lease | None = None, endpoint: IPv4Address | None = None) -> None:
    """Reject overlap using complete live address and all-table route snapshots.

    ``owned`` must come from trusted ownership established by the caller, never
    DHCP's old_* variables. Exactly one owned native IPv4 address is permitted.
    An unrecognized native address invalidates the kernel-expiry assumption.
    A different address/prefix requires withdrawal followed by a fresh check
    with no owned lease; this function never authorizes overlapping replacement.
    """
    if owned is not None and lease.address != owned.address:
        raise RejectedLease("Withdraw the old lease before accepting a different address or prefix")
    # Authorizing a pin never permits its /32 to overlap an offered subnet/server.
    endpoint_route(lease, endpoint)
    pin = None if owned is None else endpoint_route(owned, endpoint)
    protected = set(FIXED_PROTECTED)
    if endpoint is not None:
        protected.add(IPv4Network(f"{endpoint}/32"))
    native_count = 0
    for address in addresses:
        if address.interface == NATIVE:
            native_count += 1
            if (owned is None or address.address != owned.address
                    or address.label != LABEL or native_count > 1):
                raise RejectedLease("Unexpected IPv4 address on native Ethernet")
            continue
        protected.add(address.address.network)
    for route in routes:
        if route.interface == NATIVE:
            if not _owned_route(route, owned) and route != pin:
                raise RejectedLease("Unexpected IPv4 route on native Ethernet")
            continue
        if route.destination.prefixlen == 0:
            continue
        if (route.interface == "tun0" and route.table == "main"
                and route.kind == "unicast" and route.destination in VPN_CATCHALLS):
            continue
        protected.add(route.destination)
    for prefix in sorted(protected):
        if lease.address.network.overlaps(prefix):
            raise RejectedLease(f"Offered subnet overlaps protected prefix {prefix}")
        # A future explicit DHCP-server route must not displace a protected resource.
        if lease.server in prefix:
            raise RejectedLease(f"DHCP server overlaps protected prefix {prefix}")
