import psycopg2
from django.db import IntegrityError
import infohound.infohound_config as config
from infohound.tool.data_sources import alienvault, shodan
from urllib.parse import urlparse
from infohound.models import Domain,Subdomains,URLs

def getSubdomains(domain_id):
	data = []
	domain = Domain.objects.get(id=domain_id).domain
	subdomains = alienvault.getDNSRecords(domain)
	#shodan.getSubdomains(domain)
	#subdomains += shodan.getSubdomains(domain)
	for sub in subdomains:
		subdomain = Subdomains(subdomain=sub,source="Alienvault",domain_id=domain_id)
		data.append(subdomain)
	try:
		Subdomains.objects.bulk_create(data)
	except IntegrityError as e:
		pass

def getSubdomainsFromURLS(domain_id):
	data = []
	queryset = URLs.objects.filter(domain_id=domain_id)
	for entry in queryset.iterator():
		loc = urlparse(entry.url).netloc
		sub = loc.split(":")[0]
		subdomain = Subdomains(subdomain=sub,source=entry.source,domain_id=domain_id)
		data.append(subdomain)
	try:
		Subdomains.objects.bulk_create(data)
	except IntegrityError as e:
		pass