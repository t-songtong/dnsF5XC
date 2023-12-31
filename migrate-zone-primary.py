#!/usr/bin/env python3
import requests
import dns.rdataset
import dns.zonefile
import dns.zone
import dns.resolver
import dns.query
import re
import sys
import argparse
import json
from typing import cast, Union, Any
from tools.helpers import *
from tools.f5 import *

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Argument Parser") 
    parser.add_argument("domain", type=str, help="Domain to migrate")
    parser.add_argument("dns_server", type=str, help="DNS Server to request AXFR from")
    args = parser.parse_args()

    api_url = "https://{}.console.ves.volterra.io/api/config/dns/namespaces/system/dns_zones".format(readSecret(".secrets/.consoleDomain"))

    api_headers = {
        "Authorization" :   "APIToken {}".format(readSecret(".secrets/.apiToken")),
        "Accept"        :   "application/json"
    }

    pubIP = requests.get("https://api.ipify.org", verify=False).content.decode("utf8")
    print("Please ensure zone transfers are allowed from: {}".format(pubIP))

    #soa_answer = dns.resolver.resolve(args.domain, "SOA")
    #master_answer = dns.resolver.resolve(soa_answer[0].mname, "A")

    zone = dns.zone.from_xfr(dns.query.xfr(args.dns_server, args.domain))
    _defaultRrSet = ZoneNodesToF5Json(zone)

    jBody = {
        "metadata": {
            "name": args.domain,
            "namespace": "system",
            "labels": {},
            "annotations": {},
            "disable": False
        },
        "spec": {
            "primary": {
                "default_soa_parameters": {},
                "dnssec_mode": {
                    "disable": {}
                },
                "rr_set_group": [],
                "default_rr_set_group": _defaultRrSet
            }
        }
    }

    #print(json.dumps(jBody))

    print("Attempting to create zone at:\n{}".format(api_url))
    createZone = requests.post(api_url, verify=False, headers=api_headers, json=jBody)

    print(createZone.json())

############################ GLOBALS ###############################


if __name__ == "__main__":
    main()

