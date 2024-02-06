import re
import requests
import infohound.infohound_config as config
from django.db import IntegrityError
from infohound.tool.data_sources import google_data, bing_data
from infohound.models import Domain,People,Emails,Usernames


def findPeopleFromGoogle(domain_id):
	domain = Domain.objects.get(id=domain_id).domain
	company = domain.split(".")[0]
	query = f'intitle:"{company}" site:"linkedin.com"'
	results = google_data.discoverPeople(query)
	for result in results:
		try:
			People.objects.get_or_create(name=result[0], social_profiles=[result[1]], raw_metadata=result[2], url_img=result[3], source="Google", domain_id=domain_id)
		except IntegrityError as e:
			pass

def findSocialProfilesByEmail(domain_id):
	queryset = Emails.objects.filter(people_id__isnull=True, domain_id=domain_id)
	domain = Domain.objects.get(id=domain_id).domain
	for entry in queryset.iterator():
		usernames_data = []
		email = entry.email
		print("Testing: " + email)

		# TO-DO: check if Bing works
		#for l in bing_data.discoverSocialMedia(domain,email):
		#	if l not in data:
		#			data.append(l)

		results = google_data.discoverSocialMediaByDorks(domain,email)
		if results["links"] != []:
			for link in results["links"]:
				try:
					username = link.split("/")[-1]
					if "linkedin" in link:
						username = re.split('-\\d+', username)[0]
					u, created = Usernames.objects.get_or_create(username=username, source="Google", domain_id=domain_id)
					if created:
						usernames_data.append(username)	
				except IntegrityError as e:
					pass

			try:
				p, created = People.objects.get_or_create(name=results["name"], social_profiles=results["links"], source="Google", domain_id=domain_id)
			except IntegrityError as e:
				pass

			try:
				u, created = Usernames.objects.get_or_create(username=email.split("@")[0], source="Google", domain_id=domain_id)
				usernames_data.append(email.split("@")[0])	
			except IntegrityError as e:
				pass
			
			Emails.objects.filter(email=email, domain_id=domain_id).update(people=p)
			Usernames.objects.filter(username__in=usernames_data, domain_id=domain_id).update(people=p)


		
# LEGACY FUNCTION 
"""
def findSocialProfilesByEmail(domain_id):
	queryset = Emails.objects.filter(people_id__isnull=True, domain_id=domain_id)
	domain = Domain.objects.get(id=domain_id).domain
	for entry in queryset.iterator():
		usernames_data = []
		email = entry.email
		print("Testing: " + email)

		# TO-DO: check if Bing works
		#for l in bing_data.discoverSocialMedia(domain,email):
		#	if l not in data:
		#			data.append(l)

		results = google_data.discoverSocialMedia(domain,email)
		if results["links"] != []:
			for link in results["links"]:
				username = Usernames(username=link.split("/")[-1], source="Google", domain_id=domain_id)
				usernames_data.append(username)
			try:
				p, created = People.objects.get_or_create(name=results["name"], social_profiles=results["links"], source="Google", domain_id=domain_id)
			except IntegrityError as e:
				pass
			
			Emails.objects.filter(email=email).update(people=p)
			try:
				for cred in usernames_data:
					cred.people = p
				Usernames.objects.bulk_create(usernames_data)
			except IntegrityError as e:
				pass
"""
