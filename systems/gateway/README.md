# Printer gateway

The gateway supplies the uplink, VPN, firewall, DHCP, and DNS for the printer network. The current host is a Radxa Dragon Q6A; its built-in Ethernet connects to the access point and school Wi-Fi supplies the uplink.

## Components

- [VPN policy](vpn-policy/README.md): country-priority recovery, scheduled maintenance, systemd templates, and deterministic tests.

Other gateway configuration is installed on the host and documented in [operations](../../documentation/operations/OPERATIONS.md). It is not yet provided here as deployable source. Add reviewed configuration components alongside `vpn-policy/` when brought into version control.

[Topology](../../documentation/network/TOPOLOGY.md) owns network behavior; [network hardware](../../documentation/network/HARDWARE.md) records the host and access point. Repository changes alone do not alter the running gateway.
