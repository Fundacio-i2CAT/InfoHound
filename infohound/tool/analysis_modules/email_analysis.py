import re
import requests
import httpx
import infohound.infohound_config as config
from holehe import core
from django.db import IntegrityError
from infohound.models import Emails
from infohound.tool.data_sources.services import adobe,duolingo,imgur,mewe,parler,rumble,snapchat,twitter,wordpress
from infohound.tool.data_sources.leaks import leak_lookup

def checkBreach(domain_id):
	queryset = Emails.objects.filter(is_leaked__isnull=True,domain_id=domain_id)
	for entry in queryset.iterator():
		email = entry.email
		try:
			entry.is_leaked = leak_lookup.isLeaked(email)
			entry.save()
		except Exception as e:
			print(e)
			break

def findRegisteredSites(domain_id):
	data = []
	queryset = Emails.objects.filter(domain_id=domain_id)
	for entry in queryset.iterator():
		email = entry.email
		print(email)
		services = entry.registered_services

		if services is None:
			services = []

		if "twitter" not in services and twitter.twitter_email(email):
			services.append("twitter")
		if "adobe" not in services and adobe.adobe_email(email):
			services.append("adobe")
		if "facebook" not in services and adobe.adobe_facebook_email(email):
			services.append("facebook")
		if "imgur" not in services and imgur.imgur_email(email):
			services.append("imgur")
		if "mewe" not in services and mewe.mewe_email(email):
			services.append("mewe")
		if "parler" not in services and parler.parler_email(email):
			services.append("parler")
		if "rumble" not in services and rumble.rumble_email(email):
			services.append("rumble")
		if "snapchat" not in services and snapchat.snapchat_email(email):
			services.append("snapchat")
		if "wordpress" not in services and wordpress.wordpress_email(email):
			services.append("wordpress")
		if "duolingo" not in services and duolingo.duolingo_email(email):
			services.append("duolingo")

		entry.registered_services = services
		print(services)
		entry.save()
