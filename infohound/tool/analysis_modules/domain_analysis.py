import json
import requests
import dns.resolver
from django.db import IntegrityError
from infohound.models import Emails,Subdomains
from urllib.parse import urlparse
from dns.resolver import Resolver, NXDOMAIN, NoNameservers, Timeout, NoAnswer


def getDMARCPolicy(domain):
	policy = None
	try:
		res = dns.resolver.resolve("_dmarc."+domain, "TXT")[0]
		if "reject" in str(res):
			policy = "Domain is NOT VULNERABLE"
		elif "quarantine" in str(res):
			policy = "Domain CAN BE VULNERABLE (email will be sent to spam)"
		else:
			policy = "Domain is VULNERABLE"

	except Exception as e:
		print("Domain does not have TXT records")
	return policy

def canBeSpoofed(domain_id):
	queryset = Emails.objects.filter(spoofable__isnull=True,domain_id=domain_id)
	for entry in queryset:
		domain = entry.email.split("@")[1]
		res = getDMARCPolicy(domain)
		if res and "NOT" not in res:
			entry.spoofable = True
			entry.save()

def subdomainTakeOverAnalysis(domain_id):
	queryset = Subdomains.objects.filter(takeover__isnull=True,domain_id=domain_id)
	for entry in queryset.iterator():
		subdomain = entry.subdomain
		result = False
		fingerprints = json.load(open("infohound/tool/analysis_modules/fingerprints.json"))

		try:
			cname = dns.resolver.resolve(subdomain, 'CNAME')
			for fingerprint in fingerprints:
				result = canBeTakenOver(subdomain, cname, fingerprint)

		except NoNameservers:
			print("[x] DNS No No nameservers: %s" % subdomain)
		except Timeout:
			print("[x] DNS Timeout: %s"  % subdomain)
		except NoAnswer:
			print("[x] DNS No Answer for CNAME: %s"  % subdomain)
		except NXDOMAIN:
			print("[x] DNS NXDOMAIN: %s"  % subdomain)

		if result:
			entry.takeover = True
		else:
			entry.takeover = False
		entry.save()

def canBeTakenOver(domain, cnames, fingerprint):
	takeover = False
	for rdata in cnames:
		for cname in fingerprint['cname']:
			if(cname and cname in str(rdata.target)):
				website = 'http://' + domain
				print("[.] Sending HTTP Request: %s" % domain)
				try:
				    request = requests.get(website)
				except requests.exceptions.ConnectionError:
				    print("[x] Connection Failed: %s" % domain)
				    return 
				if(fingerprint['fingerprint'] in request.text):
				    print("[+] %s matched for domain %s" % (fingerprint['service'], domain))
				    takeover = True
	return takeover