# Overview
This lab demonstrates how to use the Ansible Network Collection – `Arista.Eos` to build and provision a Clos fabric along with tenant configurations on Arista EOS devices, following Infrastructure as Code (IaC) principles.

The fabric design is based on an **EVPN/VXLAN** architecture.

## Lab consists of following devices:
* DC1 fabric:
    * `spine1`
    * `spine2`
    * `leaf1`
    * `leaf2`
    * `leaf3`
    * `leaf4`
* Hosts:
    * `host1`
    * `host2`
    * `host3`
* Peers:
    * `isp-router1`
    * `isp-router2`

## Key components used:
* Ansible Network Collection for Arista EOS devices - `Arista.Eos`
* Jinja2 templating
* GitLab CI/CD pipeline for automated validation and 

## Automation architecture:
Ansible inventory hierarchy:
```
all
└── arista
    └── DC1
        ├── leaf
        │   ├── leaf1
        │   ├── leaf2
        │   ├── leaf3
        │   └── leaf4
        │
        ├── spine
        │   ├── spine1
        │   └── spine2
        │
        ├── DC1_PORT_PROFILES
        │   └── leaf
        │       ├── leaf1
        │       ├── leaf2
        │       ├── leaf3
        │       └── leaf4
        │
        └── DC1_TENANT_SERVICES
            └── leaf
                ├── leaf1
                ├── leaf2
                ├── leaf3
                └── leaf4
```

Jinja2 template hierarchy:
```
base.j2
├── vlan.j2
├── vrf.j2
├── vxlan.j2
├── intf.j2
│   └── svi.j2
└── bgp.j2
    ├── prefix-set.j2
    ├── rpl.j2
    ├── mac-vrf.j2
    └── bgp-vrf.j2
```
