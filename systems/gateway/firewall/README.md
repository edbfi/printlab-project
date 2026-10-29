# Gateway firewall

`gateway.nft` is the `inet printer_gateway` table, installed as `/etc/printing-station/gateway.nft` and loaded by `printing-gateway.service` through `gateway-control`. It forwards printer-LAN traffic only through `tun0`, restricts management input, and its `dns_guard` chain keeps resolver traffic on loopback or `tun0`. [Topology](../../../documentation/network/TOPOLOGY.md) owns forwarding and isolation behavior.

Validate with `sudo nft -c -f gateway.nft` before installing. `systemctl reload printing-gateway` validates and loads the installed file.
