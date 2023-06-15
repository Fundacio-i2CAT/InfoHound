import requests

def get_subdomains(domain):
	url = "https://api.hackertarget.com/hostsearch/?q="+domain

	subd = []
	res = requests.get(url)
	for line in res.text.split("\n"):
		subd.append(line.split(",")[0])

	return subd