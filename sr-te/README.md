# Overview
This lab demonstrate Segment Routing Traffic Engineering (SR-TE) on cEOS. It explores various use cases across multiple lab scenarios, highlighting how SR-TE can be applied to steer traffic, optimize paths, and validate traffic engineering behaviors.

## LAB consists of following routers:
* `pe1`
* `pe2`
* `pe3`
* `pe4`
* `p1`
* `p2`
* `ce1`
* `ce2`

## Key protocols used:
* **SR-MPLS** with **IS-IS** in the core. All adjacencies are established over IPv4 unnumbered interfaces and IPv6 link-local addresses.
* **BGP VPNv4** between **PE** routers.

## Lab exercises:
* [Lab #1 - Explicit SR-TE path policy on `pe1` for traffic to a VPNv4 prefix advertised by `pe3`](https://github.com/DanielBlazek18/networkinglabs/blob/main/sr-te/README.md#lab-1---explicit-sr-te-path-policy-on-pe1-for-traffic-to-a-vpnv4-prefix-advertised-by-pe3)
* [Lab #2 - Explicit (backup) SR-TE path policy on `pe1` for traffic to a VPNv4 prefix advertised by `pe4`](https://github.com/DanielBlazek18/networkinglabs/blob/main/sr-te/README.md#lab-2---explicit-backup-sr-te-path-policy-on-pe1-for-traffic-to-a-vpnv4-prefix-advertised-by-pe4)
* Lab #3 - Enable Seamless Bidirectional Forwarding Detection (SBFD) for SR-TE path policies
* Lab #4 - Remove the requirement for a Binding-SID (BSID)

## Lab #1 - Explicit SR-TE path policy on `pe1` for traffic to a VPNv4 prefix advertised by `pe3`:
* The VPNv4 prefix **8.0.0.0/24** is advertised by `pe3`.
* BGP Color Extended Community is used to steer traffic (automated steering) into an SR-TE policy; color value **30** is attached to the VPNv4 prefix **8.0.0.0/24**.
* SR-TE policy with label stack **965537 900012 900004 900003** is configured to forward traffic along the path `pe1` -> `pe2` -> `p2` -> `pe4` -> `pe3`.
* Label **965537** has been explicitly configured as an adjacency label on the `pe1` `Ethernet3` interface.

![sr-te-lab-exercise-1.png](https://github.com/DanielBlazek18/networkinglabs/blob/main/sr-te/drawings/sr-te-lab-exercise-1.png)

Prefix-list, route-map and BGP VRF configuration:
```
pe3#sh ip prefix-list SET-COLOR
ip prefix-list SET-COLOR seq 10 permit 8.0.0.0/24

pe3#sh route-map SET-COLOR
route-map SET-COLOR permit 10
  Description:
  Match clauses:
    match ip address prefix-list SET-COLOR
  SubRouteMap:
  Set clauses:
    set extcommunity color 30

sh run sec bgp | b VRF-1
   vrf LAB-VRF-1
      rd 100.64.0.3:10
      route-target import vpn-ipv4 10:10
      route-target export vpn-ipv4 10:10
      network 8.0.0.0/24 route-map SET-COLOR
```

Verification - Color Extended Community with value **30** added as expected:
```
pe3#sh bgp vpn-ipv4 8.0.0.0/24 detail 
BGP routing table information for VRF default
Router identifier 100.64.0.3, local AS number 65000
BGP routing table entry for IPv4 prefix 8.0.0.0/24, Route Distinguisher: 100.64.0.3:10
 Paths: 1 available
  Local
    - from - (0.0.0.0)
      Origin INCOMPLETE, metric -, localpref -, weight 0, tag 0, valid, local, best, redistributed (Static)
      Extended Community: Route-Target-AS:10:10 Color:CO(00):30
      Local MPLS label (VRF based): 116384
```

SR-TE policy configuration on `pe1`:
```
router traffic-engineering
   segment-routing
      rib system-colored-tunnel-rib
      !
      policy endpoint 100.64.0.3 color 30
         binding-sid 1000003
         !
         path-group preference 100
            segment-list label-stack 965537 900012 900004 900003
```

Adjacency label explicitly setup on `pe1` interface `Ethernet3`:
```
pe1#sh run int e3 | i label
   adjacency-segment ipv4 p2p label 965537
```

SR-TE policy verification:
```
pe1#sh traffic-engineering segment-routing policy endpoint 100.64.0.3 color 30
Endpoint 100.64.0.3 Color 30, Counters: not available
        Path group: State: active (for 01:49:56), modified: 00:39:30 ago
                Protocol: Static
                Endpoint provisioning: Static
                Originator: 0.0.0.0(AS0)
                Discriminator: 32769
                Preference: 100
                IGP metric: 0 (static)
                Binding SID: 1000003
                Path computation: Configured
                Explicit null label policy: IPv6 (system default)
                Segment List: State: Valid, ID: 3, Counters: not available
                Protected: No, Reason: The top label is not protected
                        Label Stack: [965537 900012 900004 900003], Weight: 1
                        Resolved Label Stack: [900012 900004 900003], Next hop: 100.64.0.2, Interface: Ethernet3
```

IP route for the VPNv4 prefix 8.0.0.0/24 on `pe1`:
```
pe1#sh ip route vrf LAB-TEST-1 8.0.0.0/24

VRF: LAB-TEST-1
[omitted]
 B I      8.0.0.0/24 [200/0]
           via SR-TE Policy 100.64.0.3, color 30, label 116384
              via SR-TE tunnel index 3, weight 1
                 via 100.64.0.2, Ethernet3, label 900012 900004 900003
```

Ping verification from `ce1` to `ce2` (8.0.0.8):
```
ce1#ping 8.0.0.8 source lo0
PING 8.0.0.8 (8.0.0.8) from 7.0.0.7 : 72(100) bytes of data.
80 bytes from 8.0.0.8: icmp_seq=1 ttl=62 time=4.21 ms
80 bytes from 8.0.0.8: icmp_seq=2 ttl=62 time=2.84 ms
80 bytes from 8.0.0.8: icmp_seq=3 ttl=62 time=2.48 ms
80 bytes from 8.0.0.8: icmp_seq=4 ttl=62 time=2.61 ms
80 bytes from 8.0.0.8: icmp_seq=5 ttl=62 time=2.56 ms

--- 8.0.0.8 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 16ms
rtt min/avg/max/mdev = 2.481/2.940/4.213/0.647 ms, ipg/ewma 4.079/3.550 ms
```

Tcpdump on `pe2` interface `Ethernet3`:
```
pe2#bash tcpdump -i eth3
19:59:42.162774 aa:c1:ab:aa:11:6a (oui Unknown) > aa:c1:ab:72:5c:34 (oui Unknown), ethertype MPLS unicast (0x8847), length 130: MPLS (label 900012, tc 0, ttl 63) (label 900004, tc 0, ttl 63) (label 900003, tc 0, ttl 63) (label 116384, tc 0, [S], ttl 63) 7.0.0.7 > 8.0.0.8: ICMP echo request, id 9, seq 2, length 80
19:59:42.166787 aa:c1:ab:aa:11:6a (oui Unknown) > aa:c1:ab:72:5c:34 (oui Unknown), ethertype MPLS unicast (0x8847), length 130: MPLS (label 900012, tc 0, ttl 63) (label 900004, tc 0, ttl 63) (label 900003, tc 0, ttl 63) (label 116384, tc 0, [S], ttl 63) 7.0.0.7 > 8.0.0.8: ICMP echo request, id 9, seq 3, length 80
19:59:42.170729 aa:c1:ab:aa:11:6a (oui Unknown) > aa:c1:ab:72:5c:34 (oui Unknown), ethertype MPLS unicast (0x8847), length 130: MPLS (label 900012, tc 0, ttl 63) (label 900004, tc 0, ttl 63) (label 900003, tc 0, ttl 63) (label 116384, tc 0, [S], ttl 63) 7.0.0.7 > 8.0.0.8: ICMP echo request, id 9, seq 4, length 80
19:59:42.174718 aa:c1:ab:aa:11:6a (oui Unknown) > aa:c1:ab:72:5c:34 (oui Unknown), ethertype MPLS unicast (0x8847), length 130: MPLS (label 900012, tc 0, ttl 63) (label 900004, tc 0, ttl 63) (label 900003, tc 0, ttl 63) (label 116384, tc 0, [S], ttl 63) 7.0.0.7 > 8.0.0.8: ICMP echo request, id 9, seq 5, length 80
```
Observations:
* Label stack observed: **900012 900004 900003 116384** in tcpdump.
* Adjacency label **965537** is popped by `pe1` before sending to `pe2`.
* Label **116384** corresponds VPNv4 label advertised by `pe3`.
* Traffic flows along the SR-TE path as intended.

## Lab #2 - Explicit (backup) SR-TE path policy on `pe1` for traffic to a VPNv4 prefix advertised by `pe4`:
* The `ce2` router is now dual-homed to both `pe3` and `pe4`, and the VPNv4 prefix **8.0.0.0/24** is advertised by `pe4`.
* BGP Color Extended Community is used to steer traffic (automated steering) into an SR-TE policy; color value **40** is attached to the VPNv4 prefix **8.0.0.0/24** advertised by `pe4`.
* SR-TE policy with label stack **965537 900012 900004** is configured to forward traffic along the path `pe1` -> `pe2` -> `p2` -> `pe4`.
* An IGP preference of **115** with **dynamic** cost calculation is configured globally under SR-TE, affecting all policies. The SR-TE policy toward `pe3` (color **30**) is preferred over the policy toward `pe4` (color **40**).
* All other configuration elements remain unchanged from **Lab #1**.

![sr-te-lab-exercise-2.png](https://github.com/DanielBlazek18/networkinglabs/blob/main/sr-te/drawings/sr-te-lab-exercise-2.png)

to be continued ...
