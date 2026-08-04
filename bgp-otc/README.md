# Overview
This lab demonstrates how to deploy and validate **BGP Roles**, as defined in **[RFC 9234](https://datatracker.ietf.org/doc/html/rfc9234)**.

> **Quick start:** [Launch](https://codespaces.new/DanielBlazek18/networkinglabs) this lab in GitHub Codespaces (no local setup required)
> 
> [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/DanielBlazek18/networkinglabs)
>
> Recommended Machine type: 2 vCPU · 8 GB RAM
>
> Pull the `FRR` container image: `docker pull quay.io/frrouting/frr:10.5.4`

## Lab consists of following devices:
* [`isp1`]()
* [`isp2`]()
* [`igw`]()
* [`customer`]()
* [`peer`]()

## Topology
![bgp-otc.png]()

## Implementation and Verification
All BGP peerings are configured with the appropriate `local-role`, as shown in the topology:
* Provider
* Customer
* Peer

Example BGP configuration with respective **BGP Roles** on the `igw` router:
```
igw# sh run bgp 
[omitted]
router bgp 65003
 bgp router-id 100.64.0.3
 neighbor 10.1.3.1 remote-as 65001
 neighbor 10.1.3.1 description isp1
 neighbor 10.1.3.1 local-role customer
 neighbor 10.2.3.2 remote-as 65002
 neighbor 10.2.3.2 description isp2
 neighbor 10.2.3.2 local-role customer
 neighbor 10.3.4.4 remote-as 65004
 neighbor 10.3.4.4 description customer
 neighbor 10.3.4.4 local-role provider
 neighbor 10.3.5.5 remote-as 65005
 neighbor 10.3.5.5 description peer
 neighbor 10.3.5.5 local-role peer
 !
 address-family ipv4 unicast
  network 192.168.3.0/24
  neighbor 10.1.3.1 route-map PASS in
  neighbor 10.1.3.1 route-map PASS out
  neighbor 10.2.3.2 route-map PASS in
  neighbor 10.2.3.2 route-map PASS out
  neighbor 10.3.4.4 route-map PASS in
  neighbor 10.3.4.4 route-map PASS out
  neighbor 10.3.5.5 route-map PASS in
  neighbor 10.3.5.5 route-map PASS out
 exit-address-family
```
_(A default permit-all route map is configured for each BGP session.)_

The roles are negotiated using the **BGP OPEN message** when a BGP session is established (BGP Role Capability, Code: 9). The respective **local** and **remote** roles can be observed using the BGP neighbor command:
```
igw# sh ip bgp neighbors 10.1.3.1
BGP neighbor is 10.1.3.1, remote AS 65001, local AS 65003, external link
  Local Role: customer
  Remote Role: provider
 Description: isp1
[omitted]

igw# sh ip bgp neighbors 10.2.3.2
BGP neighbor is 10.2.3.2, remote AS 65002, local AS 65003, external link
  Local Role: customer
  Remote Role: provider
 Description: isp2
[omitted]

igw# sh ip bgp neighbors 10.3.4.4
BGP neighbor is 10.3.4.4, remote AS 65004, local AS 65003, external link
  Local Role: provider
  Remote Role: customer
 Description: customer
[omitted]

igw# sh ip bgp neighbors 10.3.5.5
BGP neighbor is 10.3.5.5, remote AS 65005, local AS 65003, external link
  Local Role: peer
  Remote Role: peer
 Description: peer
[omitted]
```

The BGP **OTC attribute** (Code: 35) is sent to a peer along with a prefix in the **UPDATE** message. In the example below, the `isp1` router attaches the **OTC** attribute with a value of **65001** to the prefix **192.168.1.0/24** when advertising it to the `igw` router:
```
igw# sh bgp ipv4 unicast 192.168.1.0/24  
BGP routing table entry for 192.168.1.0/24, version 2
Paths: (1 available, best #1, table default)
  Advertised to peers:
  10.3.4.4
  65001
    10.1.3.1 from 10.1.3.1 (100.64.0.1)
      Origin IGP, metric 0, valid, external, otc 65001, best (First path received)
      Last update: Tue Aug  4 12:14:29 2026
```
_(As a result, the prefix will subsequently be sent only to customers.)_

Each router in this lab advertises a prefix **192.168.[ID].0/24** into BGP. The following output shows the routing table on each router, confirming that prefixes are advertised as intended with **BGP Role** enabled.

```
isp1# sh ip route 192.168.0.0/16 longer-prefixes 
[omitted]
IPv4 unicast VRF default:
S>* 192.168.1.0/24 [1/0] unreachable (blackhole), weight 1, 00:07:14
B>* 192.168.3.0/24 [20/0] via 10.1.3.3, eth1, weight 1, 00:07:09
B>* 192.168.4.0/24 [20/0] via 10.1.3.3, eth1, weight 1, 00:07:09

isp2# sh ip route 192.168.0.0/16 longer-prefixes
[omitted]
IPv4 unicast VRF default:
S>* 192.168.2.0/24 [1/0] unreachable (blackhole), weight 1, 00:08:00
B>* 192.168.3.0/24 [20/0] via 10.2.3.3, eth1, weight 1, 00:07:55
B>* 192.168.4.0/24 [20/0] via 10.2.3.3, eth1, weight 1, 00:07:55

igw# sh ip route 192.168.0.0/16 longer-prefixes 
[omitted]
IPv4 unicast VRF default:
B>* 192.168.1.0/24 [20/0] via 10.1.3.1, eth1, weight 1, 00:01:10
B>* 192.168.2.0/24 [20/0] via 10.2.3.2, eth2, weight 1, 00:01:10
S>* 192.168.3.0/24 [1/0] unreachable (blackhole), weight 1, 00:01:15
B>* 192.168.4.0/24 [20/0] via 10.3.4.4, eth3, weight 1, 00:01:10
B>* 192.168.5.0/24 [20/0] via 10.3.5.5, eth4, weight 1, 00:01:10

customer# sh ip route 192.168.0.0/16 longer-prefixes 
[omitted]
IPv4 unicast VRF default:
B>* 192.168.1.0/24 [20/0] via 10.3.4.3, eth1, weight 1, 00:08:42
B>* 192.168.2.0/24 [20/0] via 10.3.4.3, eth1, weight 1, 00:08:42
B>* 192.168.3.0/24 [20/0] via 10.3.4.3, eth1, weight 1, 00:08:42
S>* 192.168.4.0/24 [1/0] unreachable (blackhole), weight 1, 00:08:47
B>* 192.168.5.0/24 [20/0] via 10.3.4.3, eth1, weight 1, 00:08:42

peer# sh ip route 192.168.0.0/16 longer-prefixes
[omitted]
IPv4 unicast VRF default:
B>* 192.168.3.0/24 [20/0] via 10.3.5.3, eth1, weight 1, 00:09:24
B>* 192.168.4.0/24 [20/0] via 10.3.5.3, eth1, weight 1, 00:09:24
S>* 192.168.5.0/24 [1/0] unreachable (blackhole), weight 1, 00:09:29
```
* A prefix advertised by a **provider** is sent to and received by a **customer**, and is subsequently sent only to **customers** (OTC), not to another **provider** or a **peer**. In this lab example, a prefix from `isp1` is not sent to `isp2`, and vice versa.
* On the other hand, a prefix advertised by a **customer** is sent to and received by both a **provider** and a **peer**.
* Prefixes advertised by a **peer** are sent to and received by other **peers** and **customers**, but not to **providers**.