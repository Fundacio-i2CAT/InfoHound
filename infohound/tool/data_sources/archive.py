import requests
import json
import httpx
from urllib.parse import urlparse

path = "https://web.archive.org/cdx/search/cdx" \
	   "?matchType=domain&fl=original&output=json&collapse=urlkey&url="

def getSubdomains(domain,subd=[]):
	url = path + domain
	r = requests.get(url)
	data = json.loads(r.text)
	for entry in data:
		loc = urlparse(entry[0]).netloc
		s = loc.split(":")[0]
		if s not in subd:
			subd.append(s)
	return subd

def getAllUrls(domain):
	print("Getting all URLs from Web Archive...")
	url_list = []
	url = path + domain
	r = requests.get(url)
	data = json.loads(r.text)
	for entry in data:
		url_list.append(entry[0])
	return url_list

def getDownloadURL(file):
	url = "https://web.archive.org/web/"+file
	res = requests.head(url, allow_redirects=False)
	access_url = ""
	if "location" in res.headers:
		access_url = res.headers["location"]
	print(access_url)
	download_url = access_url[0:42]+"if_"+access_url[42:]
	return download_url

async def get_download_url(file): 
	url = "https://web.archive.org/web/" + file
	async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
		res = await client.head(url)
	download_url = ""
	if "location" in res.headers:
		access_url = res.headers["location"]
		download_url = access_url[0:42] + "if_" + access_url[42:]
	return download_url
