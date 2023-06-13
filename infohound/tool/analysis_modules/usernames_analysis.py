import subprocess
import re
from infohound.models import Usernames
import infohound.infohound_config as config


def getProfiles(domain):
	queryset = Usernames.objects.filter(domain_id=domain)
	for entry in queryset.iterator():
		result = subprocess.run(["maigret",entry.username], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output = result.stdout.decode('utf-8')
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