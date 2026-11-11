"""Offline DHCP input fixtures; no clients, commands, namespaces or live probes."""

from ipaddress import IPv4Address, IPv4Interface, IPv4Network
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lease_validation import (
    Address, LABEL, NATIVE, ROUTE_PROTOCOL, RejectedLease, Route,
    check_overlap, parse_grant,
)


def grant(**changes: str) -> dict[str, str]:
    environment = {
        "interface": NATIVE, "protocol": "dhcp", "reason": "BOUND",
        "if_configured": "false", "ifcarrier": "up",
        "new_ip_address": "10.49.9.53", "new_subnet_mask": "255.255.255.0",
        "new_routers": "10.49.9.1", "new_dhcp_server_identifier": "10.128.2.34",
        "new_dhcp_lease_time": "57600",
    }
    environment.update(changes)
    return environment


def route(prefix: str, interface: str = "wlan0", protocol: str = "dhcp",
          kind: str = "unicast", gateway: str | None = None, table: str = "main",
          metric: int = 0, source: str | None = None) -> Route:
    return Route(IPv4Network(prefix), interface, protocol, kind,
                 None if gateway is None else IPv4Address(gateway), table, metric,
                 None if source is None else IPv4Address(source))


class GrantTests(unittest.TestCase):
    def test_observed_school_grant(self):
        lease = parse_grant(grant())
        self.assertEqual(lease.address, IPv4Interface("10.49.9.53/24"))
        self.assertEqual(lease.lifetime, 57600)
        check_overlap(lease, [], [])

    def test_all_fresh_grant_reasons(self):
        for reason in ("BOUND", "RENEW", "REBIND", "REBOOT"):
            with self.subTest(reason=reason):
                self.assertEqual(parse_grant(grant(reason=reason)).lifetime, 57600)

    def test_cached_or_non_dhcp_events_never_create_grants(self):
        for reason in ("TIMEOUT", "STATIC", "INFORM", "RECONFIGURE", "NAK", "EXPIRE", ""):
            with self.subTest(reason=reason), self.assertRaises(RejectedLease):
                parse_grant(grant(reason=reason))

    def test_wrong_interface_or_configuration_mode(self):
        for changes in ({"interface": "wlan0"}, {"protocol": "ipv4ll"},
                        {"if_configured": "true"}, {"ifcarrier": "down"}):
            with self.subTest(changes=changes), self.assertRaises(RejectedLease):
                parse_grant(grant(**changes))

    def test_route_options_rejected_even_empty(self):
        for option in ("new_classless_static_routes", "new_ms_classless_static_routes",
                       "new_static_routes"):
            for value in ("", "0.0.0.0/0 10.49.9.1"):
                with self.subTest(option=option, value=value), self.assertRaises(RejectedLease):
                    parse_grant(grant(**{option: value}))

    def test_dns_domain_and_ntp_are_not_interpreted(self):
        ordinary = parse_grant(grant())
        self.assertEqual(ordinary, parse_grant(grant(
            new_domain_name="$(touch /do-not-execute)",
            new_domain_name_servers="127.0.0.1", new_ntp_servers="192.0.2.1")))

    def test_masks_reject_hostmask_noncontiguous_and_out_of_range(self):
        for mask in ("0.0.0.255", "255.0.255.0", "254.0.0.0", "255.255.255.254",
                     "255.255.255.255", "24", " 255.255.255.0", "::"):
            with self.subTest(mask=mask), self.assertRaises(RejectedLease):
                parse_grant(grant(new_subnet_mask=mask))

    def test_invalid_lease_addresses(self):
        for address in ("10.49.9.0", "10.49.9.255", "169.254.1.2", "127.0.0.2",
                        "224.1.2.3", "0.1.2.3", "240.1.2.3", "::1", "-4", "x" * 257):
            with self.subTest(address=address), self.assertRaises(RejectedLease):
                parse_grant(grant(new_ip_address=address))

    def test_gateway_must_be_single_usable_on_link_address(self):
        for routers in ("", "10.49.9.1 10.49.9.2", "10.49.8.1", "10.49.9.53",
                        "10.49.9.0", "10.49.9.255", "10.49.9.1;echo bad"):
            with self.subTest(routers=routers), self.assertRaises(RejectedLease):
                parse_grant(grant(new_routers=routers))

    def test_server_required_and_unicast(self):
        for server in ("", "0.0.0.0", "255.255.255.255", "169.254.1.1", "127.0.0.1",
                       "10.49.9.53", "10.49.9.0", "10.49.9.255"):
            with self.subTest(server=server), self.assertRaises(RejectedLease):
                parse_grant(grant(new_dhcp_server_identifier=server))

    def test_server_can_be_the_on_link_gateway(self):
        lease = parse_grant(grant(new_dhcp_server_identifier="10.49.9.1"))
        check_overlap(lease, [], [])

    def test_lifetimes_are_bounded_finite_decimal(self):
        for duration in ("0", "119", "86401", "4294967295", "infinity", "-1", "+120",
                         "120.0", "１２３", "120\n"):
            with self.subTest(duration=duration), self.assertRaises(RejectedLease):
                parse_grant(grant(new_dhcp_lease_time=duration))
        for duration in ("120", "86400"):
            self.assertEqual(parse_grant(grant(new_dhcp_lease_time=duration)).lifetime, int(duration))


class OverlapTests(unittest.TestCase):
    def setUp(self):
        self.lease = parse_grant(grant())

    def test_default_and_identified_vpn_split_defaults_are_ignored(self):
        check_overlap(self.lease, [], [route("0.0.0.0/0"),
                                      route("0.0.0.0/1", "tun0"),
                                      route("128.0.0.0/1", "tun0")])

    def test_other_half_default_is_protected(self):
        for candidate in (route("0.0.0.0/1", "wlan0"),
                          route("0.0.0.0/1", "tun0", table="10490")):
            with self.subTest(candidate=candidate), self.assertRaises(RejectedLease):
                check_overlap(self.lease, [], [candidate])

    def test_noprefixroute_address_is_still_protected(self):
        with self.assertRaisesRegex(RejectedLease, "overlaps protected"):
            check_overlap(self.lease, [Address("resource0", IPv4Interface("10.49.9.99/24"), "")], [])

    def test_host_route_in_any_table_is_protected(self):
        with self.assertRaises(RejectedLease):
            check_overlap(self.lease, [], [route("10.49.9.99/32", "tun0", table="200")])

    def test_dhcp_server_route_must_not_displace_resource(self):
        with self.assertRaisesRegex(RejectedLease, "DHCP server overlaps"):
            check_overlap(self.lease, [], [route("10.128.2.34/32", "tun0")])

    def test_fixed_resource_stays_protected_without_live_interface(self):
        for address, gateway in (("10.113.128.53", "10.113.128.1"),
                                 ("10.136.44.53", "10.136.44.1"),
                                 ("10.255.255.53", "10.255.255.1"),
                                 ("192.168.77.53", "192.168.77.1"),
                                 ("172.17.0.53", "172.17.0.1")):
            with self.subTest(address=address), self.assertRaises(RejectedLease):
                check_overlap(parse_grant(grant(new_ip_address=address, new_routers=gateway)), [], [])

    def test_exact_owned_address_and_routes_allow_revalidation(self):
        check_overlap(self.lease, [Address(NATIVE, self.lease.address, LABEL)], [
            route("10.49.9.0/24", NATIVE, ROUTE_PROTOCOL),
            route("10.128.2.34/32", NATIVE, ROUTE_PROTOCOL, gateway="10.49.9.1"),
            route("10.49.9.53/32", NATIVE, "kernel", "local", table="local"),
            route("10.49.9.0/32", NATIVE, "kernel", "broadcast", table="local"),
            route("10.49.9.255/32", NATIVE, "kernel", "broadcast", table="local"),
            route("0.0.0.0/0", NATIVE, ROUTE_PROTOCOL, gateway="10.49.9.1",
                  metric=100, source="10.49.9.53"),
        ], self.lease)

    def test_changed_address_or_prefix_requires_prior_withdrawal(self):
        for address, gateway in (("10.49.9.60", "10.49.9.1"), ("10.49.10.60", "10.49.10.1")):
            replacement = parse_grant(grant(new_ip_address=address, new_routers=gateway,
                                           new_dhcp_server_identifier="10.128.2.35"))
            with self.subTest(address=address), self.assertRaisesRegex(RejectedLease, "Withdraw"):
                check_overlap(replacement, [Address(NATIVE, self.lease.address, LABEL)], [], self.lease)
            # Even a stale trusted record cannot authorize two simultaneous addresses.
            with self.assertRaises(RejectedLease):
                check_overlap(replacement, [], [], self.lease)
            check_overlap(replacement, [], [], None)
            with self.assertRaises(RejectedLease):
                check_overlap(replacement, [], [route(f"{address}/32", "resource0")], None)

    def test_server_change_revalidates_resources_with_trusted_old_lease(self):
        replacement = parse_grant(grant(new_dhcp_server_identifier="10.128.2.35"))
        addresses = [Address(NATIVE, self.lease.address, LABEL)]
        old_routes = [route("10.49.9.0/24", NATIVE, ROUTE_PROTOCOL),
                      route("10.128.2.34/32", NATIVE, ROUTE_PROTOCOL, gateway="10.49.9.1")]
        check_overlap(replacement, addresses, old_routes, self.lease)
        with self.assertRaises(RejectedLease):
            check_overlap(replacement, addresses,
                          [*old_routes, route("10.128.2.35/32", "resource0")], self.lease)

    def test_unowned_native_routes_rejected_before_catchall_exclusion(self):
        candidates = [route("0.0.0.0/0", NATIVE, gateway="10.49.9.1"),
                      route("0.0.0.0/0", NATIVE, "static", table="10490"),
                      route("198.51.100.0/24", NATIVE, "static"),
                      route("10.49.9.0/24", NATIVE, ROUTE_PROTOCOL),
                      route("10.49.9.53/32", NATIVE, "kernel", "local", table="local"),
                      route("10.49.9.255/32", NATIVE, "kernel", "broadcast", table="local")]
        for candidate in candidates:
            with self.subTest(candidate=candidate), self.assertRaisesRegex(RejectedLease, "Unexpected IPv4 route"):
                check_overlap(self.lease, [], [candidate])

    def test_owned_shaped_native_routes_need_exact_table_gateway_and_address(self):
        candidates = [route("10.49.9.0/24", NATIVE, ROUTE_PROTOCOL, table="200"),
                      route("10.49.9.0/24", NATIVE, ROUTE_PROTOCOL, gateway="10.49.9.1"),
                      route("10.49.9.99/32", NATIVE, "kernel", "local", table="local"),
                      route("0.0.0.0/0", NATIVE, ROUTE_PROTOCOL, gateway="10.49.9.1",
                            metric=101, source="10.49.9.53"),
                      route("0.0.0.0/0", NATIVE, ROUTE_PROTOCOL, gateway="10.49.9.1", metric=100),
                      route("0.0.0.0/0", NATIVE, ROUTE_PROTOCOL, gateway="10.49.9.2",
                            metric=100, source="10.49.9.53")]
        for candidate in candidates:
            with self.subTest(candidate=candidate), self.assertRaisesRegex(RejectedLease, "Unexpected IPv4 route"):
                check_overlap(self.lease, [], [candidate], self.lease)

    def test_native_route_is_not_ignored_just_for_its_interface(self):
        for candidate in (route("10.49.9.0/24", NATIVE, "dhcp"),
                          route("10.49.9.99/32", NATIVE, ROUTE_PROTOCOL),
                          route("10.128.2.34/32", NATIVE, ROUTE_PROTOCOL, gateway="10.49.9.2")):
            with self.subTest(candidate=candidate), self.assertRaises(RejectedLease):
                check_overlap(self.lease, [], [candidate], self.lease)

    def test_unknown_native_address_is_rejected_even_if_nonoverlapping(self):
        with self.assertRaisesRegex(RejectedLease, "Unexpected IPv4"):
            check_overlap(self.lease, [Address(NATIVE, IPv4Interface("192.0.2.1/24"), "")], [])

    def test_two_native_addresses_invalidate_kernel_expiry_assumption(self):
        own = Address(NATIVE, self.lease.address, LABEL)
        with self.assertRaisesRegex(RejectedLease, "Unexpected IPv4"):
            check_overlap(self.lease, [own, own], [], self.lease)

    def test_wrong_label_cannot_claim_ownership(self):
        with self.assertRaises(RejectedLease):
            check_overlap(self.lease, [Address(NATIVE, self.lease.address, NATIVE)], [], self.lease)


if __name__ == "__main__":
    unittest.main()
