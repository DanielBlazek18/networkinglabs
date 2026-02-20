# Overview

`Networkinglabs` is a repository that contains practical networking lab exercises built with `containerlab`. Most labs are created using Arista `cEOS`, with `SONiC`, Cisco `c8000v`, and other network operating systems included when needed. Some labs also require additional simulation tools, such as `ExaBGP` and `Routinator`. Python, Ansible, Docker, and other automation tools are frequently used throughout the examples.

---

List of the existing LABs with a short description:
* **d-intf-bgp**: Interface-based BGP neighbors established over IPv6 link-local addresses. The IPv4 address family is enabled to exchange prefixes.
* **eos-eapi**: IaC to provision and configure Clos fabric with `Arista.Eos` Ansible collection.
* **eos-telemetry**: Arista EOS telemetry streaming via gNMI (gRPC). Components used in the lab:
  * Arista cEOS
  * pyGNMI: Python gNMI client
  * ELK stack (Elasticsearch, Logstash, and Kibana)
* **epe**: Egress Peer Engineering Using BGP-LU
* **flowspec**: BGP FlowSpec address family used to test and demonstrate <ins>drop</ins> and <ins>redirect to VRF</ins> actions. ExaBGP used to advertise traffic flow specifications (flow routes) throughout a network.
  * Action drop has been tested in the LAB.
  * Action redirect to VRF has not been tested yet.
  * Other actions to be added on the list.
* **hub-spoke-one-arm**: One-Arm Hub-and-Spoke VPN, enabling inter-spoke traffic to pass through a service router when the label allocation mode for the default route is changed.
* **rpki**: Implements BGP RPKI validation using Routinator as the Relying Party (RP). Route policies on Internet routers are enforced using standard route-maps along with the Routing Control Function (RCF).
* **sr-te**: Multiple lab exercises to explore Segment Routing Traffic Engineering (SR-TE) on cEOS.
