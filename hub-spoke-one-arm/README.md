# Overview
This LAB demonstrate One-Arm Hub-and-Spoke VPN on cEOS. 
This feature requires configuration of per-ce (per-nexthop in Arista terminology) label allocation, which can be configured for default route only. Label allocation for specific prefixes remains the same.

## LAB consists of following routers:
* `hub`
* `bb` (backbone)
* `spoke1`
* `spoke2`
* `service`

## Key protocols used:
* **SR-MPLS** with **IS-IS** between hub, spoke routers and bb
* **BGP-VPNv4** between hub and spoke routers.

## Baseline Behavior
to be added..

## Label allocation for default route changed
to be added..
