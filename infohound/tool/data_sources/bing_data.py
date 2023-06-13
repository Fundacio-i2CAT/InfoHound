import requests
import html
import urllib.parse
import infohound.tool.infohound_utils as infohound_utils
from random import randint

def discoverEmails(domain):
	bing_count = 50
	total = 350
	emails = []
	url = f"https://www.bing.com/search?q=inbody:'@{domain}'&count={bing_count}"
	try:
		count = 0
		iter_count = int(total/bing_count)
		if (total%bing_count) != 0:
			iter_count +=1
		while count < iter_count:
			this_count = count*bing_count + 1
			new_url = url + f"&first={this_count}&FORM=PERE"
			user_agent = infohound_utils.getUserAgents() 
			response = requests.get(new_url,
				headers=user_agent[randint(0, len(user_agent)-1)],
				timeout=5,
				proxies=None
			)
			escaped_text = response.text.encode('utf-8').decode('unicode_escape')
			text = urllib.parse.unquote(html.unescape(escaped_text))

			text = text.replace('<strong>', '')
			print(infohound_utils.extractEmails(domain, text))
			for e in infohound_utils.extractEmails(domain, text):
				if e not in emails:
					emails.append(e)
			count += 1
	except Exception as ex:
		pass
	return emails

def discoverSocialMedia(domain, email):
	bing_count = 50
	total = 350
	username = email.split("@")[0]
	scope = domain.split(".")[0]

	data = []
	url = f"https://www.bing.com/search?q='{username}' {scope}&count={bing_count}"
	try:
		count = 0
		iter_count = int(total/bing_count)
		if (total%bing_count) != 0:
			iter_count +=1
		while count < iter_count:
			this_count = count*bing_count + 1
			new_url = url + f"&first={this_count}&FORM=PERE"
			user_agent = infohound_utils.getUserAgents() 
			response = requests.get(new_url,
				headers=user_agent[randint(0, len(user_agent)-1)],
				timeout=5,
				proxies=None
			)
			text = response.text
			break
			count += 1
	except Exception as ex:
		print(ex)
		pass
	return data
