import requests
import infohound.infohound_config as config

API_KEY = config.LEAK_LOOKUP_KEY

def isLeaked(email):
	url = "https://leak-lookup.com/api/search"
	data = {"key":API_KEY, "type":"email_address", "query":email}
	res = requests.post(url,data=data)
	msg = res.json()["message"]
	err = res.json()["error"]
	if err == "false":
		leaked = len(msg) > 0
	else:
		raise Exception("Limit reached")
	return leaked