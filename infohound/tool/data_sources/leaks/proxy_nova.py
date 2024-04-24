import re
import requests

def getEmailsFromLeaks(domain):
	emails = []
	res = requests.get(f"https://api.proxynova.com/comb?query={domain}")
	if res.status_code == 200:
		data = res.json()
		entries = data.get("lines", [])
		print(entries)

		if entries:
			# Loop through each entry in the response
			for entry in entries:
				email = entry.split(":")[0]
				if '@' in email:
					email_domain = email.split("@")[1]
					if email_domain == domain:
						emails.append(email)

	return emails

def checkEmailLeaked(email):
	leaked = False
	res = requests.get(f"https://api.proxynova.com/comb?query={email}")

	if res.status_code == 200:
		data = res.json()
		entries = data.get("lines", [])
		if entries:
			# Loop through each entry in the response
			for entry in entries:
				leaked_email = entry.split(":")[0]
				if leaked_email == email:
					leaked = True

	return leaked


def getPassword(username):
	password = ""
	res = requests.get(f"https://api.proxynova.com/comb?query={username}")

	if res.status_code == 200:
		data = res.json()
		entries = data.get("lines", [])

		if entries:
			# Loop through each entry in the response
			for entry in entries:
				username_found = entry.split(":")[0]
				if '@' in username_found:
					username_found = username_found.split("@")[0]
				if username_found == username:
					if len(entry.split(":"))==2:
						password = entry.split(":")[1]
						break

	return password