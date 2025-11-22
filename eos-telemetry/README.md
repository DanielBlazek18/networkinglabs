# gNMI streaming telemetry Lab with Arista EOS and ELK Stack

## Overview

This lab demonstrates streaming telemetry from Arista EOS devices. Subscriptions to telemetry paths are done using gRPC Network Management Interface (gNMI) client `pygnmi-client`. The telemetry data is further visualized in an ELK (Elasticsearch, Logstash, Kibana) stack. The lab is built using **Containerlab (CLab)** with two Arista EOS hosts (`eos1` and `eos2`).

Telemetry data is streamed from the following gNMI paths:

- `eos_native:/Smash/routing/vrf/status`
- `eos_native:/Smash/forwardingGen/unifiedStatus/fec`

`Logstash` processes telemetry messages from the `pygnmi-client` and stores them in Elasticsearch. **Kibana**, the web-based GUI, is used to visualize the data.

---

## Prerequisites

- Docker & Docker Compose  
- Containerlab (`clab`)  
- Python 3.9+ with `pygnmi` installed
- ELK stack

---


