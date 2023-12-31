#!/usr/bin/env python3
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def readSecret(secretPath):
    with open(secretPath) as f:
        mySecret = f.readline().strip()
        return mySecret

api_url = "https://{}.console.ves.volterra.io/api/config/dns/namespaces/system/dns_zones".format(readSecret(".secrets/.consoleDomain"))
api_headers = {
    "Authorization" :   "APIToken {}".format(readSecret(".secrets/.apiToken")),
    "Accept"        :   "application/json"
}

response = requests.get(api_url, headers=api_headers, verify=False)
#print (response.json())

if response.status_code == 200:
   json = response.json()
   for item in json['items']:
       print(item['name'])
else:
   print(f"Request failed with status code: {response.status_code}")
