# Overview
This lab demonstrates how to use the Ansible Network Collection – `Arista.Eos` to build and provision a Clos fabric along with tenant configurations on Arista EOS devices, following Infrastructure as Code (IaC) principles.

The fabric design is based on an **EVPN/VXLAN** architecture. IPv6 is used in the underlay and overlay.

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
* GitLab CI/CD pipeline for automated validation and deployment

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
├── prefix-set.j2
└── bgp.j2
    ├── rpl.j2
    ├── mac-vrf.j2
    └── bgp-vrf.j2
```

## Pipeline Overview:
The GitLab pipeline defined in `.gitlab-ci.yml` consists of three stages:
* Build
* Approve
* Deploy

When changes to the fabric are made by modifying host or group variables, the **Build** stage is triggered. This stage generates the device configurations and commits them back to the repository. These changes are expected to be made from a **feature branch**, not from the **main** branch.

After verification, the generated configurations should be **merged into the `main` branch**, which triggers the pipeline to run again. On the `main` branch, the **Approve** and **Deploy** stages are executed.

The **Approve** stage requires **manual confirmation** before the configurations are deployed to the network devices in the **Deploy** stage.

## Pipeline at Work:
In this example, a new **VLAN 30** is introduced into the fabric and added to the allowed VLAN list of the port profile `compute_servers_dc1`.

A new feature branch named `VLAN30` is created to implement the change:
```
networkinglabs$ git checkout -b VLAN30
Switched to a new branch 'VLAN30'
```

The VLAN definition is added to the file `DC1_TENANT_SERVICES.yml`, and **VLAN 30** is included in the allowed VLAN list of the `compute_servers_dc1 port` profile in the file `DC1_PORT_PROFILES.yml`. The following git diff shows the modifications:
```
networkinglabs$ git diff
diff --git a/eos-eapi/group_vars/DC1_PORT_PROFILES.yml b/eos-eapi/group_vars/DC1_PORT_PROFILES.yml
index 5d6cf3c..3ed1335 100644
--- a/eos-eapi/group_vars/DC1_PORT_PROFILES.yml
+++ b/eos-eapi/group_vars/DC1_PORT_PROFILES.yml
@@ -1,7 +1,7 @@
 port_profiles:
     compute_servers_dc1:
         mode: trunk
-        allowed_vlans: 10,20
+        allowed_vlans: 10,20,30
         native_vlan: 1000
     baremetal:
         mode: access
diff --git a/eos-eapi/group_vars/DC1_TENANT_SERVICES.yml b/eos-eapi/group_vars/DC1_TENANT_SERVICES.yml
index 4317dfb..2457a01 100644
--- a/eos-eapi/group_vars/DC1_TENANT_SERVICES.yml
+++ b/eos-eapi/group_vars/DC1_TENANT_SERVICES.yml
@@ -3,6 +3,8 @@ vlans:
     id: 10
   L2_VLAN_20:
     id: 20
+  L2_VLAN_30:
+    id: 30
   L2_VLAN_3000:
     id: 3000
```

The changes are then staged and committed to the feature branch:
```
networkinglabs$ git add .
networkinglabs$ git commit -am "Adding VLAN30"
[VLAN30 9565a17] Adding VLAN30
 2 files changed, 3 insertions(+), 1 deletion(-)
```

Once committed, the changes can be pushed to the **remote repository**, which triggers the **GitLab CI pipeline** for the feature branch.
```
networkinglabs$ git push origin VLAN30
Enter passphrase for key '/home/danielblazek/.ssh/id_rsa': 
Enumerating objects: 11, done.
Counting objects: 100% (11/11), done.
Delta compression using up to 10 threads
Compressing objects: 100% (6/6), done.
Writing objects: 100% (6/6), 538 bytes | 538.00 KiB/s, done.
Total 6 (delta 4), reused 0 (delta 0), pack-reused 0
remote: 
remote: To create a merge request for VLAN30, visit:
remote:   https://gitlab.com/DanielBlazek18/networkinglabs/-/merge_requests/new?merge_request%5Bsource_branch%5D=VLAN30
remote: 
To gitlab.com:DanielBlazek18/networkinglabs.git
 * [new branch]      VLAN30 -> VLAN30
```

GitLab output to be added...