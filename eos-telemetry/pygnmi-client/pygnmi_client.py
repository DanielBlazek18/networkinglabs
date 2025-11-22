#!/usr/bin/env python


"""
Author: Daniel Blazek
Purpose: Pygnmi client used for connecting to EOS devices via gRPC.
         The data are parsed and sent to Logstash for further proccessing.
Status: In-progress
"""


import grpc
import threading
import ssl
import time
import concurrent.futures
import asyncio
import logging
import logstash
import sys
import json
from pygnmi.client import gNMIclient, telemetryParser


# Logstash Connector
host = 'logstash01'
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.TCPLogstashHandler(host, 5044, version=1))


# List of devices
devices = [
    {'host': 'eos1', 'port': 6030, 'username': 'admin', 'password': 'admin'},
    #{'host': 'eos2', 'port': 6030, 'username': 'cvpadmin', 'password': 'admincvp'},
]

# Output file path
#OUTPUT_FILE = "gnmi_output.log"
 
# Subscription paths (all interfaces counters)
subscription_paths = [
    'eos_native:/Smash/routing/vrf/status',
    'eos_native:/Smash/forwardingGen/unifiedStatus/fec'
    #eos_native:/Smash/tunnel/table/evpnVxlan/entry'
]
 
# TLS context (insecure for example)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
 
# Subscription request
subscription = {
    'subscription': [{'path': path, 'mode': 'on_change', 'sample_interval': 10000000000} for path in subscription_paths],
    'mode': 'stream',
    'encoding': 'json'
}


def collect_from_device(device):
    target = (device['host'], device['port'])
    try:
        with gNMIclient(target=target,
                        username=device['username'],
                        password=device['password'],
                        insecure=True,
                        ssl_context=ssl_context) as gc:
            for msg in gc.subscribe(subscribe=subscription):
                msg_parsed = telemetryParser(msg)
                msg_with_ip = {
                        'source_host': f"{device['host']}",
                        **msg_parsed}
                test_logger.info(msg_with_ip)
    except grpc.FutureTimeoutError:
        print(f"Timeout connecting to {target}")
    except Exception as e:
        print(f"Unexpected error with {target}: {e}")


async def main():
    async with asyncio.TaskGroup() as tg:
        for device in devices:
            tg.create_task(asyncio.to_thread(collect_from_device, device))


if __name__ == "__main__":
    asyncio.run(main())

