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
* Lab #2 - FlowSpec redirect to a VRF

## Lab #1 - FlowSpec discard action
* The `exabgp` is configured to advertise an **IPv4 FlowSpec rule** that matches the source prefix **9.0.0.9/32** with **discard** action.
* FlowSpec is enabled on the `igw` router interface `Ethernet1`.
* Traffic tests are initiated from the `isp` router:
  * ICMP traffic sourced from **8.0.0.8** toward **203.0.113.0/24** on the `customer` router is forwarded successfully.
  * ICMP traffic sourced from **9.0.0.9** toward the same destination is dropped by the `igw` router as dictated by the FlowSpec policy.

![flowscpec.png](https://github.com/DanielBlazek18/networkinglabs/blob/main/flowspec/drawings/flowspec.png)

Complate ExaBGP configuration on `exabgp` including the **IPv4 FlowSpec rule**:
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

The following output confirms that the **IPv4 FlowSpec** rule advertised by `exabgp` has been successfully received and accepted by the `igw` router:
```
igw#sh bgp flow-spec ipv4 summary 
BGP summary information for VRF default
Router identifier 100.64.0.1, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   RulesRcd RulesAcc RulesAdv
  10.1.5.5 4 65005              4         5    0    0 00:00:52 Estab   1      1      0
```

Detailed output of the **IPv4 FlowSpec rule** on `igw` router:
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
To be added ...
