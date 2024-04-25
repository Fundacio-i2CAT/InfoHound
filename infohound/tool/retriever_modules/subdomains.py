import psycopg2
from django.db import IntegrityError
import infohound.infohound_config as config
from infohound.tool.data_sources import alienvault, shodan, crtsh, hacker_target
from urllib.parse import urlparse
from infohound.models import Domain,Subdomains,URLs

def save_dubdomain(subdomain,source, domain_id):
	try:
		obj, created = Subdomains.objects.get_or_create(subdomain=subdomain,domain_id=domain_id)
		if created:
			obj.source = source
			obj.save()
	except IntegrityError as e:
		pass


def getSubdomains(domain_id):
	domain = Domain.objects.get(id=domain_id).domain
	subdomains = alienvault.getDNSRecords(domain)
	for sub in subdomains:
		save_dubdomain(sub,"Alienvault",domain_id)
	subdomains = crtsh.get_subdomains(domain)
	for sub in subdomains:
		save_dubdomain(sub,"Crt.sh",domain_id)
	subdomains = hacker_target.get_subdomains(domain)
	for sub in subdomains:
		save_dubdomain(sub,"HackerTarget",domain_id)

def getSubdomainsFromURLS(domain_id):
	domain = Domain.objects.get(id=domain_id).domain
	queryset = URLs.objects.filter(domain_id=domain_id)
	for entry in queryset.iterator():
		loc = urlparse(entry.url).netloc
		sub = loc.split(":")[0]
		if domain in sub:
			save_dubdomain(sub,entry.source,domain_id)
		
