import requests
import json

#https://otx.alienvault.com/api
path = "https://otx.alienvault.com/api/v1/indicators/domain/"

def getDNSRecords(domain):
	print("Getting subdomains from AlienVault...")
	subd = []
	url = path + domain + "/passive_dns"
	res = requests.get(url)
	data = json.loads(res.text)
	for entry in data["passive_dns"]:
		if entry["hostname"] not in subd:
			subd.append(entry["hostname"])
	return subd

def getWhois(domain):
	url = path + domain + "/whois"
	res = requests.get(url)
	info = {}
	data = json.loads(res.text)
	for item in data["data"]:
		info[item["key"]] = item["value"]
	return info

