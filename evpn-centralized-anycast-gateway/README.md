# Overview
This lab demonstrates how to deploy a **Centralized Anycast Gateway** in an EVPN/VXLAN fabric built with an **IPv6 underlay** on Arista EOS.

> [!TIP]
> **Quick start:** [Launch](https://codespaces.new/DanielBlazek18/networkinglabs) this lab in GitHub Codespaces (no local setup required)
>
> [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/DanielBlazek18/networkinglabs)
> 
> Recommended Machine type: 4 vCPU · 16 GB RAM

### Motivation
This exercise was inspired by a recent series of blog posts on [EVPN Centralized Routing with Arista EOS](https://blog.ipspace.net/2026/06/arista-eos-evpn-central-routing/) by [Ivan Pepelnjak](https://www.linkedin.com/in/ivanpepelnjak/). While studying the topic, I came across an Arista [document](https://www.arista.com/en/support/toi/eos-4-23-2f/14453-evpn-centralized-anycast-gateway) describing how to implement an EVPN Centralized Anycast Gateway in fabrics using an **IPv4 underlay**.

In the Arista document, the solution relies on configuring a **secondary** IPv4 address on the VXLAN source loopback interface, commonly referred to as the `VARP VTEP`. While assigning a secondary IPv4 address to a loopback interface is straightforward, IPv6 does not provide an equivalent concept. By design, an IPv6 interface can have multiple addresses without requiring a secondary keyword.

Fortunately, Arista EOS provides an alternative mechanism that works with an **IPv6 underlay**. The command `redistribute router-mac virtual-ip next-hop vtep primary` under the MAC-VRF allows the **gateway IP** and **virtual router MAC address** to be advertised in **EVPN Route Type 2** (MAC/IP Advertisement) routes, enabling a centralized anycast gateway design without the need for a dedicated VARP VTEP address.

## Lab consists of following devices:
* [`spine1`](https://github.com/DanielBlazek18/networkinglabs/blob/main/evpn-centralized-anycast-gateway/clab-evpn-centralized-anycast-gateway/spine1/flash/startup-config)
* [`spine2`](https://github.com/DanielBlazek18/networkinglabs/blob/main/evpn-centralized-anycast-gateway/clab-evpn-centralized-anycast-gateway/spine2/flash/startup-config)
* [`leaf1`](https://github.com/DanielBlazek18/networkinglabs/blob/main/evpn-centralized-anycast-gateway/clab-evpn-centralized-anycast-gateway/leaf1/flash/startup-config)
* [`leaf2`](https://github.com/DanielBlazek18/networkinglabs/blob/main/evpn-centralized-anycast-gateway/clab-evpn-centralized-anycast-gateway/leaf2/flash/startup-config)
* [`leaf3`](https://github.com/DanielBlazek18/networkinglabs/blob/main/evpn-centralized-anycast-gateway/clab-evpn-centralized-anycast-gateway/leaf3/flash/startup-config)
* [`host1`](https://github.com/DanielBlazek18/networkinglabs/blob/main/evpn-centralized-anycast-gateway/clab-evpn-centralized-anycast-gateway/host1/flash/startup-config)
* [`host2`](https://github.com/DanielBlazek18/networkinglabs/blob/main/evpn-centralized-anycast-gateway/clab-evpn-centralized-anycast-gateway/host2/flash/startup-config)

> [!NOTE]
> In a centralized VXLAN routing design, the `spine` switches provide the Layer 3 gateway functionality by hosting the **IRB interfaces** and performing inter-subnet VXLAN routing. The `leaf` switches perform Layer 2 VXLAN bridging only and are therefore commonly referred to as **Bridged VTEPs**.

## Topology
![evpn-centralized-anycast-gateway.png](https://raw.githubusercontent.com/DanielBlazek18/networkinglabs/refs/heads/main/evpn-centralized-anycast-gateway/drawings/evpn-centralized-anycast-gateway.png)

## Implementation and Verification
The following is the minimal working configuration for the **MAC-VRFs** on the `spine` switches:
```
router bgp 4200000000
[omitted]
   !
   vlan 10
      rd 100.64.0.1:10
      route-target both 345:100010
      redistribute learned
      redistribute router-mac virtual-ip next-hop vtep primary
   !
   vlan 20
      rd 100.64.0.1:20
      route-target both 345:100020
      redistribute learned
      redistribute router-mac virtual-ip next-hop vtep primary
   !
[omitted]
```
_(Full configuration can be found in the Containerlab folder `clab-evpn-centralized-anycast-gateway`)._

The `redistribute router-mac virtual-ip next-hop vtep primary` configuration causes the spine switches to originate and advertise **EVPN Route Type 2 (MAC/IP Advertisement)** routes for the **anycast IP address** and **virtual MAC address** into the EVPN control plane:
```
spine1#sh bgp evpn route-type mac-ip
BGP routing table information for VRF default
Router identifier 100.64.0.1, local AS number 4200000000
Route status codes: * - valid, > - active, S - Stale, E - ECMP head, e - ECMP
                    c - Contributing to ECMP, % - Pending best path selection
Origin codes: i - IGP, e - EGP, ? - incomplete
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  LocPref Weight  Path
 * >      RD: 100.64.0.5:20 mac-ip 001c.7322.48bb
                                 2002::100:65:0:5      -       100     0       4200000005 i
 * >      RD: 100.64.0.3:10 mac-ip 001c.7352.8199
                                 2002::100:65:0:3      -       100     0       4200000003 i
 * >      RD: 100.64.0.1:10 mac-ip 0a00.cafe.0001 10.10.0.1
                                 -                     -       -       0       i
 * >      RD: 100.64.0.1:20 mac-ip 0a00.cafe.0001 10.20.0.1
                                 -                     -       -       0       i
```
> [!NOTE]
> Without this mechanism, the **Bridge VTEPs** (`leafs`) do not know where to send traffic with the destination MAC address of the DGW, and would send a copy to each VTEP participating in the **flood list** for a particular **MAC-VRF**.

ARP table output for clarity:
```
spine1#sh ip arp vrf vrf-01 
Address         Age (sec)  Hardware Addr   Interface
10.10.0.100       0:07:17  001c.7352.8199  Vlan10, Vxlan1
10.20.0.100       0:01:37  001c.7322.48bb  Vlan20, Vxlan1
```
