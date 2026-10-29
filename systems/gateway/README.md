# Printer gateway

The gateway supplies the uplink, VPN, firewall, DHCP, and DNS for the printer network. The current host is a Radxa Dragon Q6A; its built-in Ethernet connects to the access point and school Wi-Fi supplies the uplink.

## Components

- [DNS](dns/README.md): unbound resolver for the printer LAN and Radxa, end-to-end DNS check, and tests.
- [Firewall](firewall/README.md): the `inet printer_gateway` nftables table.
- [VPN policy](vpn-policy/README.md): static-IP-first recovery with country fallback, scheduled maintenance, systemd templates, and deterministic tests.

Other gateway configuration is installed on the host and documented in [operations](../../documentation/operations/OPERATIONS.md). It is not yet provided here as deployable source. Add reviewed configuration components alongside these when brought into version control.

[Topology](../../documentation/network/TOPOLOGY.md) owns network behavior; [network hardware](../../documentation/network/HARDWARE.md) records the host and access point. Repository changes alone do not alter the running gateway.
