# Overview

`BNET networkinglabs` is a repository containing practical networking lab exercises focused on Arista EOS, SONiC and other platforms. Python, Ansible, Docker and additional automation tools are frequently used throughout the examples.

---

List of the existing LABs and short description:
* **d-intf-bgp**: Interface-based BGP neighbors established over IPv6 link-local addresses. The IPv4 address family is enabled to exchange prefixes.
* **flowspec**: BGP FlowSpec address family used to test and demonstrate <ins>drop</ins> and <ins>redirect to VRF</ins> actions.
  * Action drop has been tested in the LAB.
  * Action redirect to VRF has not been tested yet.
  * Other actions to be added on the list.
* **eos-telemetry**: Arista EOS telemetry streaming via gNMI (gRPC). Components used in the lab:
  * Arista cEOS
  * pyGNMI: Python gNMI client
  * ELK stack (Elasticsearch, Logstash, and Kibana)
