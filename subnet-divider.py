#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import math
import sys
import ipaddress

class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def power_log(x):
    """ Get smallest power of 2 greater than (or equal to) a given x. """
    return 2**(math.ceil(math.log(x, 2)))

def isqrt(n):
    """ Newton's method for calculating square roots. """
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

def subetter(input_cidr, parts, env):
    # Get the main network, to divide onto predefined parts
    pair = ipaddress.ip_network(input_cidr, strict=False)

    # Extracting netmask of the main network in CIDR
    prefix = pair.prefixlen

    # Awareness of subnets' prefix, to divide main network onto
    subnet_diff = isqrt(power_log(float(parts)))

    # Get subnets of the main network, as a list
    subnets = list(pair.subnets(prefixlen_diff=subnet_diff))

    for idx, subnet in enumerate(subnets):
        sub = str(subnet)

        # Get address string and CIDR string from command line
        (addr_string, cidr_string) = sub.split('/')

        # Split address into octets and turn CIDR into int
        addr = addr_string.split('.')
        cidr = int(cidr_string)

        # Initialize the netmask and calculate based on CIDR mask
        mask = [0, 0, 0, 0]
        for i in range(cidr):
            mask[i//8] = mask[i//8] + (1 << (7 - i % 8))

        # Initialize net and binary and netmask with addr to get network
        net = []
        for i in range(4):
            net.append(int(addr[i]) & mask[i])

        # Duplicate net into broad array, gather host bits, and generate broadcast
        broad = list(net)
        brange = 32 - cidr
        for i in range(brange):
            broad[3-i//8] = broad[3-i//8] + (1 << (i % 8))

        # Locate usable IPs
        hosts = {"first":list(net), "last":list(broad)}
        hosts["first"][3] += 1
        hosts["last"][3] -= 1

        # Locate network gateway
        gateway = hosts["first"]

        # Count the difference between first and last host IPs
        hosts["count"] = 0
        for i in range(4):
            hosts["count"] += (hosts["last"][i] - hosts["first"][i]) * 2**(8*(3-i))

        values[f"{env}_SN_{idx}"] = str(addr_string) + "/" + str(cidr)

        # Print information, mapping integer lists to strings for easy printing
        # print(("CIDR:       "), str(addr_string) + "/" + str(cidr))
        # print(("Netmask:    "), ".".join(map(str, mask)))
        # print(("Network:    "), ".".join(map(str, net)))
        # print(("Gateway:    "), ".".join(map(str, gateway)))
        # print(("Broadcast:  "), ".".join(map(str, broad)))
        # print(("Host Range: "), ".".join(mcap(str, hosts["first"])), "-", ".".join(map(str, hosts["last"])))
        # print(("Host Count: "), hosts["count"])

values = {
    "MGMT_CIDR": sys.argv[1],
    "PROD_CIDR": sys.argv[2],
    "AWS_CONFIG_ARN": sys.argv[3],
    "PREFIX": sys.argv[4]
}

# test if not valid CIDR block
ipaddress.ip_network(sys.argv[1])
ipaddress.ip_network(sys.argv[2])

subetter(sys.argv[1], 4, 'MGMT')
subetter(sys.argv[2], 2, 'PROD')

with open('parameters.json.tpl', 'r') as fr, open('parameters.json', 'w') as fw:
    data = fr.read()
    fw.write(data.format_map(SafeDict(values)))