# Overview
This LAB demonstrate direct interface BGP neighbors established over IPv6 link-local addresses. The IPv4 address family is enabled to exchange prefixes.

## LAB consists of following routers:
* `rtr`
* `peer1`
* `peer2`

## Key protocols used:
* BGP (important feature [rfc8950](https://datatracker.ietf.org/doc/html/rfc8950))

## BGP config on `rtr`

```
rtr#sh run sec bgp
router bgp 65001
   router-id 100.64.0.1
   neighbor EBGP-D-INTF peer group
   neighbor interface Et1 peer-group EBGP-D-INTF remote-as 65002
   neighbor interface Et2 peer-group EBGP-D-INTF remote-as 65003
   !
   address-family ipv4
      neighbor EBGP-D-INTF activate
      neighbor EBGP-D-INTF next-hop address-family ipv6 originate
```

## Outputs of BGP peers and BGP tables + ping tests

BGP peerings:
```
rtr#sh bgp ipv4 unicast summary
BGP summary information for VRF default
Router identifier 100.64.0.1, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor                      V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc PfxAdv
  fe80::a8c1:abff:fe20:ecef%Et2 4 65003              5         5    0    0 00:00:08 Estab   1      1      1
  fe80::a8c1:abff:fe6b:9009%Et1 4 65002              5         5    0    0 00:00:07 Estab   1      1      1
```

BGP table + detail:
```
rtr#sh bgp ipv4 unicast
BGP routing table information for VRF default
Router identifier 100.64.0.1, local AS number 65001
Route status codes: s - suppressed contributor, * - valid, > - active, E - ECMP head, e - ECMP
                    S - Stale, c - Contributing to ECMP, b - backup, L - labeled-unicast, q - Pending FIB install
                    % - Pending best path selection
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI Origin Validation codes: V - valid, I - invalid, U - unknown
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      192.168.0.0/24         fe80::a8c1:abff:fe6b:9009%Et1 0       -          100     0       65002 i
 * >      192.168.1.0/24         fe80::a8c1:abff:fe20:ecef%Et2 0       -          100     0       65003 i
```
```
rtr#sh bgp ipv4 unicast detail
BGP routing table information for VRF default
Router identifier 100.64.0.1, local AS number 65001
BGP routing table entry for 192.168.0.0/24
 Paths: 1 available
  65002
    fe80::a8c1:abff:fe6b:9009%Et1 from fe80::a8c1:abff:fe6b:9009%Et1 (100.64.0.2)
      Origin IGP, metric 0, localpref 100, IGP metric 1, weight 0, tag 0
      Received 00:01:07 ago, valid, external, best
      Rx SAFI: Unicast
BGP routing table entry for 192.168.1.0/24
 Paths: 1 available
  65003
    fe80::a8c1:abff:fe20:ecef%Et2 from fe80::a8c1:abff:fe20:ecef%Et2 (100.64.0.3)
      Origin IGP, metric 0, localpref 100, IGP metric 1, weight 0, tag 0
      Received 00:01:08 ago, valid, external, best
      Rx SAFI: Unicast

```

Ping tests (it's imported to have configured **ip routing ipv6 interfaces** on `rtr`):
```
peer1#sh ip route 192.168.1.0/24
[omitted]
 B E      192.168.1.0/24 [200/0]
           via fe80::a8c1:abff:fe08:f876, Ethernet1

peer1#ping 192.168.1.1 source lo1
PING 192.168.1.1 (192.168.1.1) from 192.168.0.1 : 72(100) bytes of data.
80 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=27.1 ms
80 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=13.4 ms
80 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=2.31 ms
80 bytes from 192.168.1.1: icmp_seq=4 ttl=64 time=0.736 ms
80 bytes from 192.168.1.1: icmp_seq=5 ttl=64 time=0.405 ms

--- 192.168.1.1 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 73ms
rtt min/avg/max/mdev = 0.405/8.790/27.051/10.318 ms, pipe 3, ipg/ewma 18.314/17.335 ms
```
