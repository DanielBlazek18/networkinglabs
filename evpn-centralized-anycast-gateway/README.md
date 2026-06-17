# Overview
This lab demonstrates how to deploy a **Centralized Anycast Gateway** in an EVPN/VXLAN fabric built with an **IPv6 underlay** on Arista EOS.

### Motivation
This exercise was inspired by a recent series of blog posts on [EVPN Centralized Routing with Arista EOS](https://blog.ipspace.net/2026/06/arista-eos-evpn-central-routing/) by [Ivan Pepelnjak](https://www.linkedin.com/in/ivanpepelnjak/). While studying the topic, I came across an Arista [document](https://www.arista.com/en/support/toi/eos-4-23-2f/14453-evpn-centralized-anycast-gateway) describing how to implement an EVPN Centralized Anycast Gateway in fabrics using an **IPv4 underlay**.

In the Arista document, the solution relies on configuring a **secondary** IPv4 address on the VXLAN source loopback interface, commonly referred to as the `VARP VTEP`. While assigning a secondary IPv4 address to a loopback interface is straightforward, IPv6 does not provide an equivalent concept. By design, an IPv6 interface can have multiple addresses without requiring a secondary keyword.

Fortunately, Arista EOS provides an alternative mechanism that works with an **IPv6 underlay**. The command `redistribute router-mac virtual-ip next-hop vtep primary` under the MAC-VRF allows the **gateway IP** and **virtual router MAC address** to be advertised in **EVPN Route Type 2** (MAC/IP Advertisement) routes, enabling a centralized anycast gateway design without the need for a dedicated VARP VTEP address.

## Lab consists of following devices:
* `spine1`
* `spine2`
* `leaf1`
* `leaf2`
* `leaf3`
* `host1`
* `host2`

> [!NOTE]
> In a centralized VXLAN routing design, the `spine` switches provide the Layer 3 gateway functionality by hosting the **IRB interfaces** and performing inter-subnet VXLAN routing. The `leaf` switches perform Layer 2 VXLAN bridging only and are therefore commonly referred to as **Bridged VTEPs**.

## Topology
![evpn-centralized-anycast-gateway.png](https://raw.githubusercontent.com/DanielBlazek18/networkinglabs/refs/heads/evpn-centralized-gateway/evpn-centralized-anycast-gateway/drawings/evpn-centralized-anycast-gateway.png)

## Implementation and verification

The minimalistic working configuration of the MAC-VRFs on the `spine` switches:
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
      rd 100.64.0.2:20
      route-target both 345:100020
      redistribute learned
      redistribute router-mac virtual-ip next-hop vtep primary
   !
[omitted]
```