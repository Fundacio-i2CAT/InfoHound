import re
import requests

def isLeaked(email):
	retry = 4
	found = False
	while(retry>0 and not found):
		url = "https://monitor.firefox.com/scan"
		client = requests.Session()
		response = client.get(url)
		csrf = re.findall('data-csrf-token="(\\d.+)"', response.text)
		if len(csrf) == 0:
			retry -= 1
			continue
		client.headers.update({"x-csrf-token":csrf[0], 'Content-Type': 'application/json'})
		res = client.post('https://monitor.firefox.com/api/v1/scan/',  json={'email': email}).json()
		found = len(res["breaches"]) > 0

	return found
