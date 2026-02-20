# Overview
This LAB demonstrates how to use the Ansible Network Collection – `Arista.Eos` to build and provision a Clos fabric along with tenant configurations on Arista EOS devices, following Infrastructure as Code (IaC) principles.

The fabric design is based on an EVPN/VXLAN architecture.

## LAB consists of following devices:
* `spine1`
* `spine2`
* `leaf1`
* `leaf2`
* `leaf3`
* `leaf4`

## Key components used:
* Ansible Network Collection for Arista EOS devices - `Arista.Eos`
* Jinja2 templating
* GitLab CI/CD pipeline for automated validation and deployment