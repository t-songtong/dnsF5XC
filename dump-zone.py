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

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Dumps zone from provided dns server to screen.") 
    parser.add_argument("domain", type=str, help="Domain to dump")
    parser.add_argument("dns_server", type=str, help="Server to query")
    
    args = parser.parse_args()

    pubIP = requests.get("https://api.ipify.org", verify=False).content.decode("utf8")
    print("Please ensure zone transfers are allowed from: {}".format(pubIP))

    soa_answer = dns.resolver.resolve(args.domain, "SOA")
    master_answer = dns.resolver.resolve(soa_answer[0].mname, "A")

    z = dns.zone.from_xfr(dns.query.xfr(args.dns_server, args.domain))
    for n in sorted(z.nodes.keys()):
        print(z[n].to_text(n))

if __name__ == "__main__":
    main()

