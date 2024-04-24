import subprocess
import re
import os
import time
from infohound.models import Usernames
from infohound.tool.data_sources.leaks import proxy_nova
import infohound.infohound_config as config


#TO-DO: maigret can also discover usernames related to the username searched. 
def getProfiles(domain):
	queryset = Usernames.objects.filter(domain_id=domain)
	for entry in queryset.iterator():
		output = esult=os.popen("maigret "+entry.username).read()
		lines = output.split('\n')
		data = entry.profiles
		for line in lines:
			match = re.match(r'\[\+\] (\S.*): (.+)', line.strip())
			print(match)
			if match:
				app_name = match.group(1)
				link = match.group(2)
				service = {"service":app_name, "link":link}
				print(service)
				if service not in data:
					data.append({"service":app_name, "link":link})
		entry.profiles = data
		print(data)
		print("---------------")
		entry.save()


def getLeakedPasswords(domain_id):
	queryset = Usernames.objects.filter(password__isnull=True,domain_id=domain_id)
	for entry in queryset.iterator():
		pwd = proxy_nova.getPassword(entry.username)
		if pwd:
			entry.password = pwd
			entry.is_leaked = True
			entry.save()
		time.sleep(0.2)
		
