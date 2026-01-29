# Overview
This lab demonstrates BGP FlowSpec implementation on Arista EOS.

## Learning Objectives:
* Configured BGP FlowSpec with different actions (discard, redirect).

## Lab consists of following devices:
* `igw`
* `isp`
* `customer`
* `scrubber`
* `exabgp`

## Key protocols used:
* BGP IPv4 unicast address family between `customer`, `igw` and `isp`
* BGP FlowSpec address family between `igw` and `exabgp`

## Lab exercices:
* [Lab #1 - FlowSpec discard action](https://github.com/DanielBlazek18/networkinglabs/blob/main/flowspec/README.md#lab-1---flowspec-discard-action)
* [Lab #2 - FlowSpec redirect to a VRF](https://github.com/DanielBlazek18/networkinglabs/blob/main/flowspec#lab-2---flowspec-redirect-to-a-vrf)

## Lab #1 - FlowSpec discard action
* The `exabgp` is configured to advertise an **IPv4 FlowSpec route** that matches the source prefix **9.0.0.9/32** with **discard** action.
* FlowSpec is enabled on the `igw` router interface `Ethernet1`.
* Traffic tests are initiated from the `isp` router:
  * ICMP traffic sourced from **8.0.0.8** toward **203.0.113.0/24** on the `customer` router is forwarded successfully.
  * ICMP traffic sourced from **9.0.0.9** toward the same destination is dropped by the `igw` router as dictated by the FlowSpec policy.

![flowscpec.png](https://github.com/DanielBlazek18/networkinglabs/blob/main/flowspec/drawings/flowspec.png)

Complate ExaBGP configuration on `exabgp` including the **IPv4 FlowSpec route**:
```
template {
   neighbor as-65001 {
        local-as 65005;
        peer-as 65001;
        router-id 100.64.0.5;
        local-address 10.1.5.5;
        flow {
            route {
                match {
                    source 9.0.0.9/32;
                    }
                    then {
                        discard;
                    }
                }
            }
        family {
            ipv4 unicast;
            ipv6 unicast;
            ipv4 flow;
        }
        capability {
            route-refresh;
            graceful-restart;
            add-path send/receive;
        }
    }
}

neighbor 10.1.5.1 {
        inherit as-65001;
}
```

The following output confirms that the **IPv4 FlowSpec route** advertised by `exabgp` has been successfully received and accepted by the `igw` router:
```
igw#sh bgp flow-spec ipv4 summary 
BGP summary information for VRF default
Router identifier 100.64.0.1, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   RulesRcd RulesAcc RulesAdv
  10.1.5.5 4 65005              4         5    0    0 00:00:52 Estab   1      1      0
```

Detailed output of the **IPv4 FlowSpec route** on `igw` router:
```
igw#sh bgp flow-spec ipv4 detail 
BGP Flow Specification rules for VRF default
Router identifier 100.64.0.1, local AS number 65001
BGP Flow Specification Matching Rule for *;9.0.0.9/32;
 Rule identifier: 3706191936
 Matching Rule:
   Destination Prefix: *
   Source Prefix: 9.0.0.9/32
 Paths: 1 available
 65005
    from 10.1.5.5 (100.64.0.5)
      Origin IGP, metric -, localpref 100, weight 0, valid, external, best
      Actions: Drop
```

FlowSpec must be explicitly enabled on the interface where rules are applied to **incoming** traffic (`Ethernet1` on the `igw` router in this example):
```
igw#sh run int e1
interface Ethernet1
   description isp_Ethernet1
   no switchport
   flow-spec ipv4 ipv6
   ip address 10.1.2.1/24
```

The FlowSpec rule is successfully **installed in hardware** on the `igw` router and applied to the ingress interface `Ethernet1`:
```
igw#sh flow-spec ipv4 rule identifier 3706191936 
Flow specification rules for VRF default
Configured on: Ethernet1
Applied on: Ethernet1
  Flow-spec rule: *;9.0.0.9/32;
    Rule identifier: 3706191936
    Matches:
      Source prefix: 9.0.0.9/32
    Actions:
      Drop
    Status:
      Installed: yes
      Counter: 0 packets, 0 bytes
```

Data plane verification **allowed** traffic - ping sourced from **8.0.0.8** toward detination **203.0.113.1** is forwarded successfully: 
```
isp#ping 203.0.113.1 source 8.0.0.8
PING 203.0.113.1 (203.0.113.1) from 8.0.0.8 : 72(100) bytes of data.
80 bytes from 203.0.113.1: icmp_seq=1 ttl=63 time=1.51 ms
80 bytes from 203.0.113.1: icmp_seq=2 ttl=63 time=0.796 ms
80 bytes from 203.0.113.1: icmp_seq=3 ttl=63 time=0.736 ms
80 bytes from 203.0.113.1: icmp_seq=4 ttl=63 time=0.705 ms
80 bytes from 203.0.113.1: icmp_seq=5 ttl=63 time=0.631 ms

--- 203.0.113.1 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 5ms
rtt min/avg/max/mdev = 0.631/0.875/1.508/0.320 ms, ipg/ewma 1.251/1.177 ms
```

Data plane verification for **blocked** traffic - ping sourced from **9.0.0.9** toward the same destination is dropped by the `igw` router:
```
isp#ping 203.0.113.1 source 9.0.0.9
PING 203.0.113.1 (203.0.113.1) from 9.0.0.9 : 72(100) bytes of data.

--- 203.0.113.1 ping statistics ---
5 packets transmitted, 0 received, 100% packet loss, time 41ms
```

## Lab #2 - FlowSpec redirect to a VRF
* The `exabgp` is configured to advertise an **IPv4 FlowSpec route** that matches the source prefix **9.0.0.9/32** with **redirect 666:666** (redirect to a VRF) action.
* FlowSpec is enabled on the `igw` router interface `Ethernet1`.
* Traffic tests are initiated from the `isp` router:
  * ICMP traffic sourced from **8.0.0.8** toward **203.0.113.0/24** on the `customer` router is forwarded successfully.
  * ICMP traffic sourced from **9.0.0.9** toward the same destination is redirected by the `igw` router into the **DIRTY** VRF (**666:666**) as dictated by the FlowSpec policy.

Complate `exabgp` configuration for the Lab #2. The BGP FlowSpec route is modified to use the `redirect 666:666` action (VRF redirection) instead of `discard`:
```
template {
   neighbor as-65001 {
        local-as 65005;
        peer-as 65001;
        router-id 100.64.0.5;
        local-address 10.1.5.5;
        flow {
            route {
                match {
                    source 9.0.0.9/32;
                    }
                    then {
                        redirect 666:666;
                    }
                }
            }
        family {
            ipv4 unicast;
            ipv6 unicast;
            ipv4 flow;
        }
        capability {
            route-refresh;
            graceful-restart;
            add-path send/receive;
        }
    }
}

neighbor 10.1.5.1 {
        inherit as-65001;
}
```

A new VRF instance **DIRTY** is defined on the `igw`:
```
vrf instance DIRTY
ip routing vrf DIRTY
!
interface Ethernet4.10
   encapsulation dot1q vlan 10
   vrf DIRTY
   ip address 10.1.4.1/24
!
ip route vrf DIRTY 0.0.0.0/0 Ethernet4.10 10.1.4.4 name to_scrubber
!
router bgp 65001
   vrf DIRTY
      rd 666:666
      route-target import vpn-ipv4 666:666
      route-target export vpn-ipv4 666:666
```

The updated **IPv4 FlowSpec route** with a **redirect** action to the **DIRTY** VRF (**666:666**) is successfully received and accepted by the `igw` router:
```
igw#sh bgp flow-spec ipv4
BGP Flow Specification rules for VRF default
Router identifier 100.64.0.1, local AS number 65001
Rule status codes: # - not installed, M - received from multiple peers
                   I - has interface-set community

    Matching Rule                                                Actions
    *;9.0.0.9/32;                                                Redirect-VRF:666:666 (DIRTY)
```

The following output shows detailed information for the **IPv4 FlowSpec route** on `igw` router:
```
igw#sh bgp flow-spec ipv4 detail 
BGP Flow Specification rules for VRF default
Router identifier 100.64.0.1, local AS number 65001
BGP Flow Specification Matching Rule for *;9.0.0.9/32;
 Rule identifier: 3559129152
 Matching Rule:
   Destination Prefix: *
   Source Prefix: 9.0.0.9/32
 Paths: 1 available
 65005
    from 10.1.5.5 (100.64.0.5)
      Origin IGP, metric -, localpref 100, weight 0, valid, external, best
      Actions: Redirect-VRF:666:666 (DIRTY)
```

The FlowSpec rule is successfully **installed in hardware** on the `igw` router and applied to the ingress interface `Ethernet1`:
```
igw#sh flow-spec ipv4 rule identifier 3559129152 
Flow specification rules for VRF default
Configured on: Ethernet1
Applied on: Ethernet1
  Flow-spec rule: *;9.0.0.9/32;
    Rule identifier: 3559129152
    Matches:
      Source prefix: 9.0.0.9/32
    Actions:
      Redirect: VRF DIRTY
                Route via next hop 0.0.0.0
    Status:
      Installed: yes
      Counter: 0 packets, 0 bytes

```

Traceroute initiated from **8.0.0.8** toward destination **203.0.113.1** is forwarded **directly** to the `customer` router without any redirection:
```
isp#traceroute 203.0.113.1 source lo1
traceroute to 203.0.113.1 (203.0.113.1), 30 hops max, 60 byte packets
 1  10.1.2.1 (10.1.2.1)  0.068 ms  0.011 ms  0.010 ms
 2  203.0.113.1 (203.0.113.1)  3.167 ms  3.285 ms  4.282 ms
```

In contrast, traceroute initiated from **9.0.0.9** toward the same destination is **redirected** via the `scrubber` router before reaching the `customer`:
```
isp#traceroute 203.0.113.1 source lo2
traceroute to 203.0.113.1 (203.0.113.1), 30 hops max, 60 byte packets
 1  10.1.2.1 (10.1.2.1)  0.070 ms  0.015 ms  0.013 ms
 2  * * *
 3  10.11.44.11 (10.11.44.11)  2.716 ms  3.533 ms  4.397 ms
 4  203.0.113.1 (203.0.113.1)  7.190 ms  7.265 ms  7.907 ms
```

A tcpdump capture on the `scrubber` confirms that the **redirected** traffic is forwarded as intended:
```
scrubber#bash tcpdump -i eth1
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on eth1, link-type EN10MB (Ethernet), snapshot length 262144 bytes
22:39:09.581249 aa:c1:ab:c5:25:bd (oui Unknown) > aa:c1:ab:f2:1a:db (oui Unknown), ethertype 802.1Q (0x8100), length 78: vlan 10, p 0, ethertype IPv4 (0x0800), 9.0.0.9.55088 > 203.0.113.1.33437: UDP, length 32
22:39:09.581366 aa:c1:ab:c5:25:bd (oui Unknown) > aa:c1:ab:f2:1a:db (oui Unknown), ethertype 802.1Q (0x8100), length 78: vlan 10, p 0, ethertype IPv4 (0x0800), 9.0.0.9.45723 > 203.0.113.1.33438: UDP, length 32
22:39:09.581857 aa:c1:ab:c5:25:bd (oui Unknown) > aa:c1:ab:f2:1a:db (oui Unknown), ethertype 802.1Q (0x8100), length 78: vlan 10, p 0, ethertype IPv4 (0x0800), 9.0.0.9.57537 > 203.0.113.1.33439: UDP, length 32
22:39:09.581942 aa:c1:ab:c5:25:bd (oui Unknown) > aa:c1:ab:f2:1a:db (oui Unknown), ethertype 802.1Q (0x8100), length 78: vlan 10, p 0, ethertype IPv4 (0x0800), 9.0.0.9.41871 > 203.0.113.1.33440: UDP, length 32
22:39:09.582439 aa:c1:ab:c5:25:bd (oui Unknown) > aa:c1:ab:f2:1a:db (oui Unknown), ethertype 802.1Q (0x8100), length 78: vlan 10, p 0, ethertype IPv4 (0x0800), 9.0.0.9.60361 > 203.0.113.1.33441: UDP, length 32
22:39:09.582465 aa:c1:ab:f2:1a:db (oui Unknown) > aa:c1:ab:c5:25:bd (oui Unknown), ethertype 802.1Q (0x8100), length 78: vlan 20, p 0, ethertype IPv4 (0x0800), 9.0.0.9.41871 > 203.0.113.1.33440: UDP, length 32
[omitted]
```