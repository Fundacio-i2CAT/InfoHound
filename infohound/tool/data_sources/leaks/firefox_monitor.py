import re
import requests

def isLeaked(email):
	url = "https://monitor.firefox.com/scan"
	client = requests.Session()
	response = client.get(url)
	csrf = re.findall('data-csrf-token="(\\d.+)"', response.text)
	if len(csrf) == 0:
		raise Exception("CSRF")
	client.headers.update({"x-csrf-token":csrf[0], 'Content-Type': 'application/json'})
	res = client.post('https://monitor.firefox.com/api/v1/scan/',  json={'email': email}).json()
	print(res)
	return len(res["breaches"]) > 0