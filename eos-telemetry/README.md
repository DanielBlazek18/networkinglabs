# gNMI streaming telemetry Lab with Arista EOS and ELK Stack

## Overview

This lab demonstrates streaming telemetry from Arista EOS devices. Subscriptions to telemetry paths are done using gRPC Network Management Interface (gNMI) client `pygnmi-client`. The telemetry data is further visualized in an ELK (Elasticsearch, Logstash, Kibana) stack. The lab is built using **Containerlab (CLab)** with two Arista EOS hosts (`eos1` and `eos2`).

Telemetry data is streamed from the following gNMI paths:

- `eos_native:/Smash/routing/vrf/status`
- `eos_native:/Smash/forwardingGen/unifiedStatus/fec`

`Logstash` processes telemetry messages from the `pygnmi-client` and stores them in Elasticsearch. **Kibana**, the web-based GUI, is used to visualize the data.

- Prerequisites
- Setup
- Verification

---

## Prerequisites

- Docker & Docker Compose  
- Containerlab (`clab`)  
- Python 3.9+ with `pygnmi` installed
- ELK stack

---

## Setup

Fist step is to install ELK stack with `docker compose`.
```
bnetadmin@bnet-containerlab:~/labs/eos-telemetry/elk$ docker compose up -d
[+] Running 36/36
 ✔ kibana Pulled                                                                                                                                                                                                  68.1s 
   ✔ c7cb1a43d65b Pull complete                                                                                                                                                                                    1.8s 
   ✔ 401408895e91 Pull complete                                                                                                                                                                                    5.3s 
   ✔ d92e9ec6f80f Pull complete                                                                                                                                                                                   64.5s 
   ✔ bb37fd0eba92 Pull complete                                                                                                                                                                                   64.6s 
   ✔ 5cc3a1dd73ce Pull complete                                                                                                                                                                                   64.9s 
   ✔ 775791441b8b Pull complete                                                                                                                                                                                   65.1s 
   ✔ 4ca545ee6d5d Pull complete                                                                                                                                                                                   65.1s 
   ✔ 19597474842e Pull complete                                                                                                                                                                                   65.2s 
   ✔ d9ba32b546e6 Pull complete                                                                                                                                                                                   65.3s 
   ✔ b6d6751d409a Pull complete                                                                                                                                                                                   65.4s 
   ✔ 1acf4da5a66e Pull complete                                                                                                                                                                                   65.5s 
   ✔ 4ea3cc57a23b Pull complete                                                                                                                                                                                   65.6s 
   ✔ 7f81751ab56a Pull complete                                                                                                                                                                                   65.8s 
 ✔ logstash01 Pulled                                                                                                                                                                                              64.6s 
   ✔ c2d8b817afd6 Already exists                                                                                                                                                                                   0.0s 
   ✔ 9656c00b5b1a Pull complete                                                                                                                                                                                   20.5s 
   ✔ 715d4a72c0bd Pull complete                                                                                                                                                                                   24.6s 
   ✔ 0b45a46b59c9 Pull complete                                                                                                                                                                                   59.5s 
   ✔ 3f8dc87f7b6d Pull complete                                                                                                                                                                                   60.1s 
   ✔ ea6a697beeae Pull complete                                                                                                                                                                                   60.4s 
   ✔ eee98c7f45b9 Pull complete                                                                                                                                                                                   60.5s 
   ✔ 1a41c5b3674e Pull complete                                                                                                                                                                                   60.8s 
   ✔ 4db2214fdc5b Pull complete                                                                                                                                                                                   61.2s 
   ✔ b55b6f0e1c59 Pull complete                                                                                                                                                                                   61.6s 
   ✔ 831c9b64832d Pull complete                                                                                                                                                                                   61.9s 
 ✔ setup Pulled                                                                                                                                                                                                   63.2s 
   ✔ 36784a6c1818 Pull complete                                                                                                                                                                                    7.4s 
   ✔ 482347291b6d Pull complete                                                                                                                                                                                    8.9s 
   ✔ f40682440917 Pull complete                                                                                                                                                                                   57.5s 
   ✔ 09bca7b2ff3f Pull complete                                                                                                                                                                                   59.6s 
   ✔ f7e835da9bd8 Pull complete                                                                                                                                                                                   60.0s 
   ✔ b55c73faafcb Pull complete                                                                                                                                                                                   60.4s 
   ✔ c2da01c2e921 Pull complete                                                                                                                                                                                   60.6s 
   ✔ a2eb9f9311a2 Pull complete                                                                                                                                                                                   60.9s 
 ✔ es01 Pulled                                                                                                                                                                                                    63.2s 
[+] Running 5/5
 ✔ Network elastic             Created                                                                                                                                                                             0.1s 
 ✔ Container elk-setup-1       Healthy                                                                                                                                                                             2.7s 
 ✔ Container elk-es01-1        Healthy                                                                                                                                                                            34.5s 
 ✔ Container elk-kibana-1      Healthy                                                                                                                                                                            62.4s 
 ✔ Container elk-logstash01-1  Started                                                                                                                                                                            63.9s 
```
Check status of containers.
```
bnetadmin@bnet-containerlab:~/labs/eos-telemetry/elk$ docker ps
CONTAINER ID   IMAGE                                                  COMMAND                  CREATED         STATUS                   PORTS                                                 NAMES
ce95da40467d   docker.elastic.co/logstash/logstash:8.18.3             "/usr/local/bin/dock…"   4 minutes ago   Up 3 minutes             0.0.0.0:5044->5044/tcp, :::5044->5044/tcp, 9600/tcp   elk-logstash01-1
945a402b48b7   docker.elastic.co/kibana/kibana:8.18.3                 "/bin/tini -- /usr/l…"   4 minutes ago   Up 4 minutes (healthy)   0.0.0.0:5601->5601/tcp, :::5601->5601/tcp             elk-kibana-1
f85690a58c87   docker.elastic.co/elasticsearch/elasticsearch:8.18.3   "/bin/tini -- /usr/l…"   4 minutes ago   Up 4 minutes (healthy)   0.0.0.0:9200->9200/tcp, :::9200->9200/tcp, 9300/tcp   elk-es01-1
```
Container `elk-setup-1` should exit after ELK setup is done.
```
bnetadmin@bnet-containerlab:~/labs/eos-telemetry/elk$ docker logs -n10 elk-setup-1
Setting file permissions
Waiting for Elasticsearch availability
Setting kibana_system password
All done!
```
Next, we can deploy our Containerlab topology. You can adjust the topology file as needed. I’ll be running only two cEOS devices and subscribing to EOS1 from a pyGNMI client for simplicity.
```
bnetadmin@bnet-containerlab:~/labs/eos-telemetry$ clab deploy -t topology.yaml 
12:39:06 INFO Containerlab started version=0.71.1
12:39:06 INFO Parsing & checking topology file=topology.yaml
12:39:06 INFO Creating docker network name=clab IPv4 subnet=172.20.20.0/24 IPv6 subnet=3fff:172:20:20::/64 MTU=0
12:39:06 INFO Creating lab directory path=/home/bnetadmin/labs/eos-telemetry/clab-eos-telemetry
12:39:06 INFO Creating container name=eos1
12:39:06 INFO Creating container name=eos2
12:39:07 INFO Running postdeploy actions for Arista cEOS 'eos1' node
12:39:07 INFO Created link: eos1:eth1 ▪┄┄▪ eos2:eth1
12:39:07 INFO Running postdeploy actions for Arista cEOS 'eos2' node
12:40:00 INFO Adding host entries path=/etc/hosts
12:40:00 INFO Adding SSH config for nodes path=/etc/ssh/ssh_config.d/clab-eos-telemetry.conf
You are on the latest version (0.71.1)
╭──────┬──────────────┬─────────┬───────────────────╮
│ Name │  Kind/Image  │  State  │   IPv4/6 Address  │
├──────┼──────────────┼─────────┼───────────────────┤
│ eos1 │ ceos         │ running │ 172.20.20.3       │
│      │ ceos:4.35.0F │         │ 3fff:172:20:20::3 │
├──────┼──────────────┼─────────┼───────────────────┤
│ eos2 │ ceos         │ running │ 172.20.20.2       │
│      │ ceos:4.35.0F │         │ 3fff:172:20:20::2 │
╰──────┴──────────────┴─────────┴───────────────────╯
```
The final piece is to deploy our pyGNMI client.
```
bnetadmin@bnet-containerlab:~/labs/eos-telemetry/pygnmi-client$ ./build.sh 
Building Docker image: bnet/pygnmi-client
[+] Building 5.2s (12/12) FINISHED                                                                                                                                                                       docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                                               0.0s
 => => transferring dockerfile: 293B                                                                                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.12                                                                                                                                                     0.9s
 => [internal] load .dockerignore                                                                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                                                                    0.0s
 => [internal] load build context                                                                                                                                                                                  0.0s
 => => transferring context: 2.56kB                                                                                                                                                                                0.0s
 => [1/7] FROM docker.io/library/python:3.12@sha256:01f36278bcca9fb4a5bdda7edc85be44218190a9371f642d8f852f36ad9fa23d                                                                                               0.1s
 => => resolve docker.io/library/python:3.12@sha256:01f36278bcca9fb4a5bdda7edc85be44218190a9371f642d8f852f36ad9fa23d                                                                                               0.1s
 => CACHED [2/7] WORKDIR /pygnmi-client                                                                                                                                                                            0.0s
 => CACHED [3/7] COPY requirements.txt ./                                                                                                                                                                          0.0s
 => CACHED [4/7] RUN pip install --upgrade pip                                                                                                                                                                     0.0s
 => CACHED [5/7] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                                                0.0s
 => CACHED [6/7] RUN pip install python-logstash                                                                                                                                                                   0.0s
 => [7/7] COPY pygnmi_client.py /pygnmi-client                                                                                                                                                                     0.1s
 => exporting to image                                                                                                                                                                                             3.8s
 => => exporting layers                                                                                                                                                                                            3.7s
 => => writing image sha256:22c6d46097127a388dd63fafc8c5070d32fe66d4e318cb91ab8aea7ca2c7d945                                                                                                                       0.0s
 => => naming to docker.io/bnet/pygnmi-client                                                                                                                                                                      0.0s
Running container: pygnmi-client
ccecdd5fdc188bf941e5fc58f1a1a0d7b87d1e495fa65c77fd4cacc5b21fd64f
```
Verify that the `pygnmi-client` container is running.
```
bnetadmin@bnet-containerlab:~/labs/eos-telemetry/pygnmi-client$ docker ps | grep pygnmi
ccecdd5fdc18   bnet/pygnmi-client                                     "python ./pygnmi_cli…"   About a minute ago   Up About a minute                                                               pygnmi-client
```
`ELS stack` and `pygnmi-client` containers must be on the same network.
```
bnetadmin@bnet-containerlab:~/labs/eos-telemetry/pygnmi-client$ docker network inspect elastic  | egrep "Name|IPv4|Containers"
        "Name": "elastic",
        "Containers": {
                "Name": "elk-kibana-1",
                "IPv4Address": "172.19.0.4/16",
                "Name": "pygnmi-client",
                "IPv4Address": "172.19.0.5/16",
                "Name": "elk-logstash01-1",
                "IPv4Address": "172.19.0.2/16",
                "Name": "elk-es01-1",
                "IPv4Address": "172.19.0.3/16",
```

---

## Verification

I disabled/enabled loobpack0 interface to generate some data to a `pygnmi-client`.
```
eos1#sh run int lo0
interface Loopback0
   vrf eos-telemetry-vrf-01
   ip address 8.8.8.8/32
eos1#conf t
eos1(config)#int lo0
eos1(config-if-Lo0)#shutdown 
eos1(config-if-Lo0)#no shutdown 
eos1(config-if-Lo0)#end
```

See logs from `elk-logstash01-1`, or log in to Elastic at http://[yourip]:5601. From there, you can review the indexes, set up data views, and continue working with the data.
```
bnetadmin@bnet-containerlab:~/labs/eos-telemetry$ docker logs -n30 elk-logstash01-1
[omitted]
{
     "event_type" => "prefix_delete",
         "prefix" => "8.8.8.8/32",
       "vrf_name" => "eos-telemetry-vrf-01",
     "@timestamp" => 2025-11-25T12:53:35.868Z,
    "source_host" => "eos1"
}
{
     "event_type" => "fecId_delete",
          "fecId" => "1297036696977670145",
     "@timestamp" => 2025-11-25T12:53:35.868Z,
    "source_host" => "eos1"
}
{
     "event_type" => "fecId_update",
         "intfId" => "Loopback0",
          "fecId" => "1297036696977670153",
     "@timestamp" => 2025-11-25T12:53:39.962Z,
    "source_host" => "eos1"
}
{
     "event_type" => "prefix_update",
         "prefix" => "8.8.8.8/32",
       "vrf_name" => "eos-telemetry-vrf-01",
          "fecId" => "1297036696977670153",
     "@timestamp" => 2025-11-25T12:53:39.961Z,
    "source_host" => "eos1"
}
```
