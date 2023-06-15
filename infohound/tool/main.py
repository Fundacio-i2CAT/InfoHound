#from retriever_modules import files_search, dns_data, dorks, whois_data,subdomains,urls,files,emails,people
#from analysis_modules import files_analysis, email_analysis

import os.path
import sqlite3
import trio
import psycopg2
import infohound_config as config
import django
import os
import sys


BASE_DIR = os.path.dirname("/home/xavi/Documents/TFM/django_site/")
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_site.settings')
django.setup()
from retriever_modules import domains,subdomains,urls,emails,files,people,ips
from analysis_modules import files_analysis, email_analysis



def main():
	domain = "i2cat.net"

	# Phase 1 - Retrieve Information
	#domains.getWhoisInfo(domain)
	#domains.get_dns_records(domain)
	##domains.get_ip_address(domain)
	##domains.get_hosting_info("104.26.5.20")




	#print("Getting dns_data.getSubdomains")
	##dork_url = dorks.getDorks(domain)
	#print("Getting whois_data.getWhoisInfo")
	
	#print("Getting subdomains.getSubdomains")
	#subdomains.getSubdomains(domain)
	#urls.getURLs(domain)
	##dorks.loadDorksFromFile(domain,"dorks/custom_dorks.txt", "custom")
	##dorks.executeDorks()
	#print("Getting subdomains.getSubdomainsFromURLS()")
	#subdomains.getSubdomainsFromURLS()
	#trio.run(files.get_files_from_urls)
	#print("Getting emails.findEmails")
	#emails.findEmails(domain)
	#emails.findEmailsFromURL(domain)
	#print("Getting people.findSocialNetworksByEmail")
	#people.findSocialProfilesByEmail(domain)
	#ips.getInfoFromShodan("172.67.70.27")

	


	# Phase 2 - Analyze Information
	#trio.run(files_analysis.download_all_files)
	#files_analysis.getMetadata()
	#files_analysis.getEmailsFromMetadata()
	#files_analysis.getEmailsFromContent()
	#trio.run(email_analysis.findRegisteredSitesHolehe)
	#email_analysis.findRegisteredSites()
	#email_analysis.checkBreach()


main()