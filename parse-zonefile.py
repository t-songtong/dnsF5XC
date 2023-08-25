#!/usr/bin/env python3
import requests
import dns.rdataset
import dns.zonefile
import dns.zone
import os, glob
import json
import re
from tools.helpers import *
from tools.f5 import *

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    api_url = "https://{}.console.ves.volterra.io/api/config/dns/namespaces/system/dns_zones".format(readSecret(".secrets/.consoleDomain"))

    api_headers = {
        "Authorization" :   "APIToken {}".format(readSecret(".secrets/.apiToken")),
        "Accept"        :   "application/json"
    }

    path = 'zones/'
    for filename in glob.glob(os.path.join(path, '*.zf')):
        #print("filename :"+os.path.join(os.getcwd()+"/"+filename))
        #if to use with block, must indent covering untill jBody block
        #with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode #always failed
        #with open(os.path.join(os.getcwd()+"/"+filename), 'r') as f: # open in readonly mode #always failed
        zoneName = re.sub('\.zf', '', os.path.basename(filename))
        try:
           dnsZone = dns.zone.from_file(os.path.join(os.getcwd()+"/"+filename),zoneName)
           #failed if not specified origin argument (default=none, and read from $ORIGIN value), or even send '.' as origin, failed too.
           #dnsZone = dns.zone.from_file(f,filename)
           #dnsZone = dns.zone.from_file(f,filename+'.')
        except Exception as e:
           print("An error occurred:", e)
        defaultRR = ZoneNodesToF5Json(dnsZone)
        print("Processing Zone {}".format(zoneName))

        jBody = {
            "metadata": {
                "name": zoneName,
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
                    "default_rr_set_group": defaultRR
                }
            }
        }
        #print(json.dumps(jBody, indent=4))
        print("Attempting to create zone {} at:\n{}".format(zoneName, api_url))
        createZone = requests.post(api_url, verify=False, headers=api_headers, json=jBody)

        print(createZone.json())

if __name__ == "__main__":
    main()
