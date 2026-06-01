#!/usr/bin/env python


"""
Author: Daniel Blazek
Purpose: Testing model-driven network automation by generating 
        IETF interface configuration with pyangbind and deploying 
        it to a network device via NETCONF.
Status: In-progress
"""


import json
from ncclient import manager
from lxml import etree
from pyangbind.lib.serialise import pybindIETFXMLEncoder
from binding import openconfig_interfaces


def edit_config(host_ip, config) -> str | None:
    try:
        with manager.connect(
            host=host_ip,
            port=830,
            username="admin",
            password="admin",
            timeout=90,
            hostkey_verify=False,
        ) as m:
            print(f"Successfully connected to {host_ip}")

            try:
                response = m.edit_config(target="running", config=config)
                if response.ok:
                    return "OK"
            except Exception as e:
                return f"Error has occured: {e}"

    except Exception as e:
        return f"An unexpected error occurred while connecting to {host}: {e}"


def main():
    interfaces = openconfig_interfaces()
    if_lo0 = interfaces.interfaces.interface.add("Loopback0")
    if_lo0.config.name = "Loopback0"
    if_lo0.config.description = "Create by Netconf & pyangbind"
    if_lo0.config.enabled = True
    if_lo0.config.type = "softwareLoopback"
    
    subif0 = if_lo0.subinterfaces.subinterface.add(0)
    subif0.config.index = 0
    subif0.config.enabled = True
    addr = subif0.ipv4.addresses.address.add("1.1.1.1")
    addr.config.ip = "1.1.1.1"
    addr.config.prefix_length = 32

    #print(json.dumps(interfaces.get(), indent=4))

    config_xml = pybindIETFXMLEncoder.serialise(interfaces.interfaces)
    config = etree.Element("config", xmlns="urn:ietf:params:xml:ns:netconf:base:1.0")
    config.append(etree.fromstring(config_xml))

    print("Intended config:")
    print(etree.tostring(config, pretty_print=True).decode())

    for device in ["cisco", "arista"]:
        result = edit_config(device, config)
        print(result)

if __name__ == "__main__":
    main()
