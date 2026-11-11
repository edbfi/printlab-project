"""Lease transactions independent of subprocesses, files and DHCP transport.

This is not an executable hook. The privileged adapter must supply a bounded
lock, atomic boot-scoped state writes in /run, complete snapshots, and trusted grant
deadlines. No deadline is reconstructed from a saved lease or wall clock here.
State survives process/service crashes, but must never survive a reboot.
"""

from collections.abc import Mapping
from contextlib import AbstractContextManager
from dataclasses import dataclass, replace
from ipaddress import IPv4Address, IPv4Network
import math
from typing import Protocol

from lease_validation import (
    Address, LABEL, Lease, NATIVE, ROUTE_PROTOCOL, RejectedLease, Route,
    check_overlap, endpoint_route, parse_grant,
)


class UnsafeState(RuntimeError):
    """State cannot safely authorize a mutation or positive eligibility."""


class StaleReceipt(UnsafeState):
    """A validly shaped but obsolete callback is an intentional no-op."""


@dataclass(frozen=True)
class Identity:
    index: int
    mac: str


@dataclass(frozen=True)
class Snapshot:
    identity: Identity | None
    carrier: bool
    native_ipv6: bool
    addresses: tuple[Address, ...]
    routes: tuple[Route, ...]


@dataclass(frozen=True)
class Ownership:
    lease: Lease
    identity: Identity
    expires: float
    ready: bool = False
    endpoint: IPv4Address | None = None


@dataclass(frozen=True)
class State:
    # Generation is created by the service launcher, never DHCP input. It must
    # include the boot identity and change on every client restart.
    generation: str
    last_receipt: float
    owned: Ownership | None = None
    active: bool = False


@dataclass(frozen=True)
class Receipt:
    generation: str
    received: float
    # Conservative absolute CLOCK_BOOTTIME expiry established by the caller.
    # In particular, hook-entry time + raw DHCP duration is NOT proof of this.
    expires: float


class Port(Protocol):
    def lock(self) -> AbstractContextManager[None]: ...
    def now(self) -> float: ...
    def read(self) -> State: ...
    def write(self, state: State) -> None: ...
    def publish(self, owned: Ownership | None) -> None: ...
    def snapshot(self) -> Snapshot: ...
    def address(self, lease: Lease, lifetime: int) -> None: ...
    def add_route(self, route: Route) -> None: ...
    def delete_route(self, route: Route) -> None: ...
    def delete_address(self, address: Address) -> None: ...


def routes_for(lease: Lease) -> tuple[Route, ...]:
    routes = [Route(lease.address.network, NATIVE, ROUTE_PROTOCOL,
                    preferred_source=lease.address.ip)]
    if lease.server not in lease.address.network:
        routes.append(Route(IPv4Network(f"{lease.server}/32"), NATIVE, ROUTE_PROTOCOL,
                            gateway=lease.gateway, preferred_source=lease.address.ip))
    routes.append(Route(IPv4Network("0.0.0.0/0"), NATIVE, ROUTE_PROTOCOL,
                        gateway=lease.gateway, metric=100,
                        preferred_source=lease.address.ip))
    return tuple(routes)


def cleanup_routes(owned: Ownership) -> tuple[Route, ...]:
    """Deletion order: default, authorized VPN pin, DHCP server and subnet."""
    routes = list(reversed(routes_for(owned.lease)))
    pin = endpoint_route(owned.lease, owned.endpoint)
    if pin is not None:
        routes.insert(1, pin)
    return tuple(routes)


def local_route(route: Route, lease: Lease) -> bool:
    """Only kernel address bookkeeping may disappear with the last address."""
    if (route.interface != NATIVE or route.protocol != "kernel"
            or route.table != "local" or route.gateway is not None
            or route.metric != 0 or route.preferred_source != lease.address.ip):
        return False
    if route.kind == "local":
        return route.destination == IPv4Network(f"{lease.address.ip}/32")
    return route.kind == "broadcast" and route.destination in (
        IPv4Network(f"{lease.address.network.network_address}/32"),
        IPv4Network(f"{lease.address.network.broadcast_address}/32"),
    )


def native_addresses(snapshot: Snapshot) -> tuple[Address, ...]:
    return tuple(address for address in snapshot.addresses if address.interface == NATIVE)


def verify_owned(snapshot: Snapshot, owned: Ownership) -> None:
    """Allow missing resources after expiry, but never adopt foreign resources."""
    verify_identity(snapshot, owned)
    if snapshot.identity is None:
        return
    addresses = native_addresses(snapshot)
    if addresses not in ((), (Address(NATIVE, owned.lease.address, LABEL),)):
        raise UnsafeState("Native IPv4 resources are not exclusively owned")
    allowed = cleanup_routes(owned)
    if any(route.interface == NATIVE and route not in allowed
           and not local_route(route, owned.lease) for route in snapshot.routes):
        raise UnsafeState("Refusing cleanup that could delete an unowned native route")


def verify_identity(snapshot: Snapshot, owned: Ownership) -> None:
    if snapshot.identity is not None and snapshot.identity != owned.identity:
        raise UnsafeState("Native interface identity changed")
    if snapshot.identity is None and (
        native_addresses(snapshot) or any(r.interface == NATIVE for r in snapshot.routes)
    ):
        raise UnsafeState("Missing interface has inconsistent resource snapshot")


class Controller:
    def __init__(self, port: Port, expected_mac: str, endpoint: IPv4Address | None = None):
        self.port = port
        self.expected_mac = expected_mac
        self.endpoint = endpoint

    def _withdraw(self, state: State) -> State:
        self.port.publish(None)
        if state.owned is None:
            return state
        # Retain intent until every deletion has been verified. A process dying
        # after a command can therefore be reconciled by ExecStopPost.
        owned = replace(state.owned, ready=False)
        state = replace(state, owned=owned)
        self.port.write(state)
        snapshot = self.port.snapshot()
        verify_identity(snapshot, owned)
        # Default first. Remove exact known entries only, never flush a table.
        for route in cleanup_routes(owned):
            snapshot = self.port.snapshot()
            verify_identity(snapshot, owned)
            if route in snapshot.routes:
                self.port.delete_route(route)
        snapshot = self.port.snapshot()
        verify_owned(snapshot, owned)
        if native_addresses(snapshot):
            self.port.delete_address(Address(NATIVE, owned.lease.address, LABEL))
        snapshot = self.port.snapshot()
        verify_owned(snapshot, owned)
        if native_addresses(snapshot) or any(r.interface == NATIVE for r in snapshot.routes):
            raise UnsafeState("Owned resources remain after withdrawal")
        state = replace(state, owned=None)
        self.port.write(state)
        return state

    def _consume(self, state: State, receipt: Receipt) -> State:
        if (not receipt.generation or not math.isfinite(receipt.received)
                or receipt.received < 0
                or receipt.received > self.port.now()):
            raise UnsafeState("Malformed or future callback receipt")
        if (not state.active or receipt.generation != state.generation
                or receipt.received <= state.last_receipt):
            raise StaleReceipt("Stopped, stale or replayed callback receipt")
        return replace(state, last_receipt=receipt.received)

    def withdraw(self, receipt: Receipt | None = None) -> None:
        """A stale callback cannot withdraw a newer client's lease.

        Receipt.expires is irrelevant for withdrawal; receipt ordering is not.
        The privileged service stop path uses receipt=None, after the entire
        client cgroup has stopped. Callers must not hold this lock while waiting
        for dhcpcd: a final callback may itself need the lock.
        """
        with self.port.lock():
            state = self.port.read()
            if receipt is None:
                state = replace(state, active=False,
                                last_receipt=max(state.last_receipt, self.port.now()))
            else:
                state = self._consume(state, receipt)
            # Persist retirement/order even if there are no owned resources or
            # cleanup later fails. Late work must not recreate the old lease.
            self.port.write(state)
            self._withdraw(state)

    def begin(self, generation: str) -> None:
        """Launcher-only operation after the preceding client has stopped."""
        if not generation:
            raise UnsafeState("Empty client generation")
        with self.port.lock():
            state = self.port.read()
            if state.generation == generation:
                raise UnsafeState("A client generation cannot be reused")
            state = replace(state, active=False)
            self.port.write(state)
            self._withdraw(state)
            self.port.write(State(generation, self.port.now(), active=True))

    def grant(self, environment: Mapping[str, str], receipt: Receipt) -> None:
        with self.port.lock():
            state = self.port.read()
            # These checks precede invalidation: stale work must not disrupt
            # a newer generation or replay an already processed callback.
            state = self._consume(state, receipt)
            self.port.publish(None)
            self.port.write(state)
            try:
                lease = parse_grant(environment)
                if (not math.isfinite(receipt.expires)
                        or receipt.expires > receipt.received + lease.lifetime
                        or receipt.expires < self.port.now() + 2):
                    raise RejectedLease("No defensible remaining grant lifetime")
                old = state.owned
                if old is not None and (
                    not old.ready or old.expires <= self.port.now()
                    or old.endpoint != self.endpoint
                    or (old.lease.address, old.lease.gateway, old.lease.server)
                    != (lease.address, lease.gateway, lease.server)
                ):
                    state = self._withdraw(state)
                    old = None
                snapshot = self.port.snapshot()
                if (snapshot.identity is None or snapshot.identity.mac != self.expected_mac
                        or not snapshot.carrier or snapshot.native_ipv6):
                    raise UnsafeState("Native link is not eligible for an IPv4 grant")
                if old is not None:
                    verify_owned(snapshot, old)
                check_overlap(lease, snapshot.addresses, snapshot.routes,
                              None if old is None else old.lease, self.endpoint)
                # Account for all time spent waiting/validating, with a one-second
                # margin. Adapter must issue this single bounded operation now.
                assigned_at = self.port.now()
                lifetime = math.floor(receipt.expires - assigned_at) - 1
                if lifetime < 1:
                    raise RejectedLease("Grant expired before address assignment")
                # Publish no later expiry than this conservative kernel deadline.
                owned = Ownership(lease, snapshot.identity, assigned_at + lifetime,
                                  endpoint=self.endpoint)
                state = replace(state, owned=owned)
                self.port.write(state)  # ownership intent BEFORE first mutation
                self.port.address(lease, lifetime)
                for route in routes_for(lease):
                    snapshot = self.port.snapshot()
                    verify_owned(snapshot, owned)
                    if route not in snapshot.routes:
                        self.port.add_route(route)
                snapshot = self.port.snapshot()
                verify_owned(snapshot, owned)
                check_overlap(lease, snapshot.addresses, snapshot.routes, lease, owned.endpoint)
                if (not snapshot.carrier or snapshot.native_ipv6
                        or native_addresses(snapshot) != (Address(NATIVE, lease.address, LABEL),)
                        or not all(route in snapshot.routes for route in routes_for(lease))
                        or self.port.now() >= owned.expires):
                    raise UnsafeState("Grant did not converge to eligible kernel state")
                state = replace(state, owned=replace(owned, ready=True))
                self.port.write(state)
                self.port.publish(state.owned)
            except Exception:
                # Failure is still reported if cleanup succeeds. If cleanup
                # fails, retained non-ready intent is the recovery record.
                self._withdraw(state)
                raise
