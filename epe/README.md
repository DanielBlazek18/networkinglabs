# Overview
This LAB demostrate Egress Peer Engineering Using BGP-LU on cEOS.

## LAB consist of following routers:
* `ingress-pe`
* `bb` (backbone)
* `egress-pe`
* `peer1`
* `peer2`

## Key protocols used:
* **SR-MPLS** with **IS-IS** between pe routers and bb
* **BGP-LU** between pe routers. BGP next-hops origination for peers must be explicitly configured.
* **BGP Add-Path** (send from `egress-pe`, recived on `ingress-pe`)

## Baseline Behavior
* Prefix 192.168.1.0/24 is advertised by both peers.
* Initial best path is via **10.4.3.4**, label **116386**, resolved to **Ethernet3** (`peer1`) on `egress-pe`.
```
ingress-pe#sh ip bgp 192.168.1.0/24
BGP routing table information for VRF default
Router identifier 100.64.0.1, local AS number 65000
BGP routing table entry for 192.168.1.0/24
 Paths: 3 available
  65004
    10.4.3.4 from 100.64.0.3 (100.64.0.3)
      Origin IGP, metric 0, localpref 100, IGP metric 0, weight 0, tag 0
      Received 00:21:34 ago, valid, internal, best
      Rx path id: 0x1
      Rx SAFI: Unicast
      Tunnel RIB eligible
  65005
    10.3.5.5 from 100.64.0.3 (100.64.0.3)
      Origin IGP, metric 0, localpref 100, IGP metric 0, weight 0, tag 0
      Received 00:21:34 ago, valid, internal
      Rx path id: 0x2
      Rx SAFI: Unicast
      Tunnel RIB eligible
  65004
    10.3.4.4 from 100.64.0.3 (100.64.0.3)
      Origin IGP, metric 0, localpref 100, IGP metric 0, weight 0, tag 0
      Received 00:21:33 ago, valid, internal
      Rx path id: 0x3
      Rx SAFI: Unicast
      Tunnel RIB eligible

ingress-pe#sh ip route 192.168.1.0/24
[omitted]
 B I      192.168.1.0/24 [200/0]
           via BGP LU Forwarding tunnel index 24
              via IS-IS SR tunnel index 2, label 116386
                 via 10.1.2.2, Ethernet1, label 900003

ingress-pe#ping 192.168.1.1 source lo1
PING 192.168.1.1 (192.168.1.1) from 192.168.0.1 : 72(100) bytes of data.
80 bytes from 192.168.1.1: icmp_seq=1 ttl=62 time=2.69 ms
80 bytes from 192.168.1.1: icmp_seq=2 ttl=62 time=1.67 ms
80 bytes from 192.168.1.1: icmp_seq=3 ttl=62 time=1.45 ms
80 bytes from 192.168.1.1: icmp_seq=4 ttl=62 time=1.36 ms
80 bytes from 192.168.1.1: icmp_seq=5 ttl=62 time=1.37 ms

bb#bash tcpdump -i eth1
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on eth1, link-type EN10MB (Ethernet), snapshot length 262144 bytes
[omitted]
17:03:13.570158 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116386, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 22, seq 1, length 80
17:03:13.571991 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 22, seq 1, length 80
17:03:13.572680 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116386, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 22, seq 2, length 80
17:03:13.574027 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 22, seq 2, length 80
17:03:13.574659 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116386, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 22, seq 3, length 80
17:03:13.575782 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 22, seq 3, length 80
17:03:13.576646 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116386, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 22, seq 4, length 80
17:03:13.577765 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 22, seq 4, length 80
17:03:13.578642 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116386, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 22, seq 5, length 80
17:03:13.579741 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 22, seq 5, length 80
[omitted]

egress-pe#sh mpls lfib route 116386
[omitted]
 BL    116386   [1], 10.4.3.4/32
                via M, 10.4.3.4, pop
                 payload autoDecide, ttlMode uniform, apply egress-acl
                 interface Ethernet3
```

## Applying Local Preference to Prefer `peer2` (10.3.5.5)
* To prefer the path via **10.3.5.5**, apply a route-map to the inbound BGP session on `ingress-pe`.
```
ingress-pe#conf t
ingress-pe(config)#router bgp 65000 
ingress-pe(config-router-bgp)#address-family ipv4 
ingress-pe(config-router-bgp-af)#neighbor 100.64.0.3 route-map EPE-NHOP-SET-PREFERENCE in
ingress-pe(config-router-bgp-af)#end
ingress-pe#
ingress-pe#sh route-map EPE-NHOP-SET-PREFERENCE
route-map EPE-NHOP-SET-PREFERENCE permit 10
  Description:
  Match clauses:
    match ip next-hop prefix-list EPE-NHOP-10.3.5.5
  SubRouteMap:
  Set clauses:
    set local-preference 120
route-map EPE-NHOP-SET-PREFERENCE permit 65535
  Description:
  Match clauses:
  SubRouteMap:
  Set clauses:

ingress-pe#sh ip bgp 192.168.1.0/24
BGP routing table information for VRF default
Router identifier 100.64.0.1, local AS number 65000
BGP routing table entry for 192.168.1.0/24
 Paths: 3 available
  65005
    10.3.5.5 from 100.64.0.3 (100.64.0.3)
      Origin IGP, metric 0, localpref 120, IGP metric 0, weight 0, tag 0
      Received 00:23:10 ago, valid, internal, best
      Rx path id: 0x2
      Rx SAFI: Unicast
      Tunnel RIB eligible
  65004
    10.4.3.4 from 100.64.0.3 (100.64.0.3)
      Origin IGP, metric 0, localpref 100, IGP metric 0, weight 0, tag 0
      Received 00:23:10 ago, valid, internal
      Rx path id: 0x1
      Rx SAFI: Unicast
      Tunnel RIB eligible
  65004
    10.3.4.4 from 100.64.0.3 (100.64.0.3)
      Origin IGP, metric 0, localpref 100, IGP metric 0, weight 0, tag 0
      Received 00:23:09 ago, valid, internal
      Rx path id: 0x3
      Rx SAFI: Unicast
      Tunnel RIB eligible

ingress-pe#sh ip route 192.168.1.0/24
[omitted]
 B I      192.168.1.0/24 [200/0]
           via BGP LU Forwarding tunnel index 23
              via IS-IS SR tunnel index 2, label 116385
                 via 10.1.2.2, Ethernet1, label 900003

ingress-pe#ping 192.168.1.1 source lo1
PING 192.168.1.1 (192.168.1.1) from 192.168.0.1 : 72(100) bytes of data.
80 bytes from 192.168.1.1: icmp_seq=1 ttl=62 time=2.80 ms
80 bytes from 192.168.1.1: icmp_seq=2 ttl=62 time=1.89 ms
80 bytes from 192.168.1.1: icmp_seq=3 ttl=62 time=2.03 ms
80 bytes from 192.168.1.1: icmp_seq=4 ttl=62 time=1.80 ms
80 bytes from 192.168.1.1: icmp_seq=5 ttl=62 time=1.78 ms


bb#bash tcpdump -i eth1
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on eth1, link-type EN10MB (Ethernet), snapshot length 262144 bytes
17:04:18.822416 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116385, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 23, seq 1, length 80
17:04:18.824297 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 23, seq 1, length 80
17:04:18.824996 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116385, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 23, seq 2, length 80
17:04:18.826391 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 23, seq 2, length 80
17:04:18.827897 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116385, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 23, seq 3, length 80
17:04:18.829535 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 23, seq 3, length 80
17:04:18.830825 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116385, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 23, seq 4, length 80
17:04:18.832297 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 23, seq 4, length 80
17:04:18.833776 aa:c1:ab:3c:ec:95 (oui Unknown) > aa:c1:ab:f8:b7:cc (oui Unknown), ethertype MPLS unicast (0x8847), length 122: MPLS (label 900003, tc 0, ttl 65) (label 116385, tc 0, [S], ttl 65) 192.168.0.1 > 192.168.1.1: ICMP echo request, id 23, seq 5, length 80
17:04:18.835281 aa:c1:ab:f8:b7:cc (oui Unknown) > aa:c1:ab:3c:ec:95 (oui Unknown), ethertype IPv4 (0x0800), length 114: 192.168.1.1 > 192.168.0.1: ICMP echo reply, id 23, seq 5, length 80

egress-pe#sh mpls lfib route 116385 
[omitted]
 BL    116385   [1], 10.3.5.5/32
                via M, 10.3.5.5, pop
                 payload autoDecide, ttlMode uniform, apply egress-acl
                 interface Ethernet4

```

