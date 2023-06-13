from infohound.tool.retriever_modules import domains,subdomains,urls,files,emails,people,dorks
from infohound.tool.analysis_modules import domain_analysis,email_analysis,files_analysis,usernames_analysis
from celery import shared_task
import trio
import importlib


@shared_task(bind=True, name="get_whois_info")
def getWhoisInfoTask(self, domain):
	domains.getWhoisInfo(domain)

@shared_task(bind=True, name="get_dns_records")
def getDNSRecordsTask(self, domain):
	domains.get_dns_records(domain)

@shared_task(bind=True, name="get_subdomains")
def getSubdomainsTask(self, domain):
	subdomains.getSubdomains(domain)

@shared_task(bind=True, name="get_subdomains_from_urls")
def getSubdomainsFromURLSTask(self, domain):
	subdomains.getSubdomainsFromURLS(domain)

@shared_task(bind=True, name="get_urls")
def getURLsTask(self, domain):
	urls.getURLs(domain)

@shared_task(bind=True, name="get_files_from_urls")
def getFilesFromURLsTask(self, domain):
	trio.run(files.get_files_from_urls, domain)

@shared_task(bind=True, name="find_emails")
def findEmailsTask(self, domain):
	emails.findEmails(domain)

@shared_task(bind=True, name="find_emails_from_urls")
def findEmailsFromURLsTask(self, domain):
	emails.findEmailsFromURLs(domain)

@shared_task(bind=True, name="find_social_profiles_by_email")
def findSocialProfilesByEmailTask(self, domain):
	people.findSocialProfilesByEmail(domain)

@shared_task(bind=True, name="execute_dorks")
def executeDorksTask(self, domain):
	dorks.executeDorks(domain)

@shared_task(bind=True, name="find_emails_from_dorks")
def findEmailsFromDorksTask(self, domain):
	emails.findEmailsFromDorks(domain)



# -------------ANALYSIS-------------
@shared_task(bind=True, name="subdomain_take_over_analysis")
def subdomainTakeOverAnalysisTask(self, domain):
	domain_analysis.subdomainTakeOverAnalysis(domain)

@shared_task(bind=True, name="can_be_spoofed")
def canBeSpoofedTask(self, domain):
	domain_analysis.canBeSpoofed(domain)

@shared_task(bind=True, name="get_profiles")
def getProfilesTask(self, domain):
	usernames_analysis.getProfiles(domain)

@shared_task(bind=True, name="download_all_files")
def downloadAllFilesTask(self, domain):
	trio.run(files_analysis.download_all_files,domain)

@shared_task(bind=True, name="get_metadata")
def getMetadataTask(self, domain):
	files_analysis.getMetadata(domain)

@shared_task(bind=True, name="get_emails_from_metadata")
def getEmailsFromMetadataTask(self, domain):
	files_analysis.getEmailsFromMetadata(domain)

@shared_task(bind=True, name="get_emails_from_content")
def getEmailsFromFilesContentTask(self, domain):
	files_analysis.getEmailsFromFilesContent(domain)

@shared_task(bind=True, name="find_registered_sites")
def findRegisteredSitesTask(self, domain):
	email_analysis.findRegisteredSites(domain)

@shared_task(bind=True, name="check_breach")
def checkBreachTask(self, domain):
	email_analysis.checkBreach(domain)

# --------------CUSTOM--------------

@shared_task(bind=True, name="custom_task")
def executeCustomTask(self, domain, module_path):
	module = importlib.import_module(module_path)
	module.custom_task(domain)

