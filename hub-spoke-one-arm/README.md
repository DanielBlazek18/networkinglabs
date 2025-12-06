# Overview
This lab demonstrates a One-Arm Hub-and-Spoke VPN using cEOS.
This feature requires configuration of per-CE (per-nexthop in Arista terminology) label allocation, which can only be applied to the default route. Label allocation for specific prefixes remains unchanged.

## LAB consists of following routers:
* `hub`
* `bb` (backbone)
* `spoke1`
* `spoke2`
* `service`

## Key protocols used:
* **SR-MPLS** with **IS-IS** between `hub`, `spokes` and `bb`.
* **BGP-VPNv4** between `hub` and `spokes`.

## Baseline Behavior
By default, traffic between the `CUST-A` prefix 192.168.1.0/24 and `CUST-B` prefix 192.168.2.0/24 **is not** routed through the `service` router (which would represent a firewall, load balancer, etc. in a real deployment).

Default route on `spoke1` is learned with label `116384`:
```
spoke1#sh bgp vpn-ipv4 0.0.0.0/0 detail
BGP routing table information for VRF default
Router identifier 100.64.0.3, local AS number 65000
BGP routing table entry for IPv4 prefix 0.0.0.0/0, Route Distinguisher: 100.64.0.1:1000
 Paths: 1 available
  Local
    100.64.0.1 from 100.64.0.1 (100.64.0.1)
      Origin INCOMPLETE, metric -, localpref 100, weight 0, tag 0, valid, internal, best
      Extended Community: Route-Target-AS:1000:1000
      Remote MPLS label: **116384**
```

Label `116384` is resolved to VRF `HUB` on `hub` router (per-vrf allocation):
```
hub#sh mpls lfib route 116384
[omitted]
 B3    116384   [0]
                via I, ipv4, vrf HUB
```
Ping between `spoke1` and `spoke2` works, but traffic is routed only through the `hub`, rather than the `service` router.

## Changing Label Allocation for Default Route
The following configuration allocates a dedicated label for the default route, pointing traffic to the `service` router interface (per-ce allocation):
```
hub(config)#router bgp 65000
hub(config-router-bgp)#vrf HUB
hub(config-router-bgp-vrf-HUB)#route-target export vpn-ipv4 label allocation nexthop default-route
```

The default route is now advertised with a different label than specific prefixes:
```
spoke1#sh bgp vpn-ipv4 0.0.0.0/0 detail
BGP routing table information for VRF default
Router identifier 100.64.0.3, local AS number 65000
BGP routing table entry for IPv4 prefix 0.0.0.0/0, Route Distinguisher: 100.64.0.1:1000
 Paths: 1 available
  Local
    100.64.0.1 from 100.64.0.1 (100.64.0.1)
      Origin INCOMPLETE, metric -, localpref 100, weight 0, tag 0, valid, internal, best
      Extended Community: Route-Target-AS:1000:1000
      Remote MPLS label: **116385**

spoke1#sh bgp vpn-ipv4 192.168.4.0/24 detail
BGP routing table information for VRF default
Router identifier 100.64.0.3, local AS number 65000
BGP routing table entry for IPv4 prefix 192.168.4.0/24, Route Distinguisher: 100.64.0.1:1000
 Paths: 1 available
  Local
    100.64.0.1 from 100.64.0.1 (100.64.0.1)
      Origin IGP, metric -, localpref 100, weight 0, tag 0, valid, internal, best
      Extended Community: Route-Target-AS:1000:1000
      Remote MPLS label: 116384
```

Label `116385` resolves to the `service` router interface:
```
hub#sh mpls lfib route 116385
[omitted]
 B3    116385   [0]
                via M, 172.16.0.1, pop
                 payload autoDecide, ttlMode uniform, dscpMode uniform, apply egress-acl
                 interface Ethernet2
```
*Specific prefixes continue to use the per-VRF label `116384`.*

Traceroute from `spoke1` now shows traffic passing through the `service` router (link subnet 172.16.0.0/31):
```
spoke1#traceroute vrf CUST-A 192.168.2.1 source 192.168.1.1
traceroute to 192.168.2.1 (192.168.2.1), 30 hops max, 60 byte packets
 1  * * *
 2  172.16.0.1 (172.16.0.1)  18.556 ms  19.074 ms  19.143 ms
 3  172.16.0.0 (172.16.0.0)  19.169 ms  19.721 ms  20.709 ms
 4  * * *
 5  * * *
 6  192.168.2.1 (192.168.2.1)  23.666 ms  5.731 ms  6.306 ms
```

A tcpdump on the `service` router confirms traffic transit:
```
service#bash tcpdump -i eth1 icmp
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on eth1, link-type EN10MB (Ethernet), snapshot length 262144 bytes
08:50:08.823514 aa:c1:ab:1b:44:c9 (oui Unknown) > aa:c1:ab:ee:89:4e (oui Unknown), ethertype IPv4 (0x0800), length 102: service > 192.168.1.1: ICMP time exceeded in-transit, length 68
08:50:08.824913 aa:c1:ab:1b:44:c9 (oui Unknown) > aa:c1:ab:ee:89:4e (oui Unknown), ethertype IPv4 (0x0800), length 102: service > 192.168.1.1: ICMP time exceeded in-transit, length 68
08:50:08.825063 aa:c1:ab:1b:44:c9 (oui Unknown) > aa:c1:ab:ee:89:4e (oui Unknown), ethertype IPv4 (0x0800), length 102: service > 192.168.1.1: ICMP time exceeded in-transit, length 68
08:50:08.829840 aa:c1:ab:ee:89:4e (oui Unknown) > aa:c1:ab:1b:44:c9 (oui Unknown), ethertype IPv4 (0x0800), length 102: 192.168.2.1 > 192.168.1.1: ICMP 192.168.2.1 udp port 33449 unreachable, length 68
08:50:08.829871 aa:c1:ab:ee:89:4e (oui Unknown) > aa:c1:ab:1b:44:c9 (oui Unknown), ethertype IPv4 (0x0800), length 102: 192.168.2.1 > 192.168.1.1: ICMP 192.168.2.1 udp port 33450 unreachable, length 68
08:50:08.829954 aa:c1:ab:1b:44:c9 (oui Unknown) > aa:c1:ab:ee:89:4e (oui Unknown), ethertype IPv4 (0x0800), length 102: 192.168.2.1 > 192.168.1.1: ICMP 192.168.2.1 udp port 33449 unreachable, length 68
08:50:08.830045 aa:c1:ab:1b:44:c9 (oui Unknown) > aa:c1:ab:ee:89:4e (oui Unknown), ethertype IPv4 (0x0800), length 102: 192.168.2.1 > 192.168.1.1: ICMP 192.168.2.1 udp port 33450 unreachable, length 68
[omitted]
```
