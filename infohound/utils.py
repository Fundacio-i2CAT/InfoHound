import os
import importlib
import infohound.tasks as tasks_list
from celery import group
from infohound.models import Domain, Dorks, Tasks
from django.db import IntegrityError
from django.utils import timezone



def load_tasks(domain_id):
    tasks = [
    # RETRIEVAL
    {"name_id":"getWhoisInfoTask","name":"Get Whois Information", "description":"Get relevant information from Whois register.", "type":"Retrieve"},
    {"name_id":"getDNSRecordsTask","name":"Get DNS Records", "description":"This task queries the DNS.", "type":"Retrieve"},
    {"name_id":"getSubdomainsTask","name":"Get Subdomains", "description":"This task uses Alienvault OTX API, CRT.sh and HackerTarget as data sources to discover cached subdomains.", "type":"Retrieve"},
    {"name_id":"getSubdomainsFromURLSTask","name":"Get Subdomains from URLs", "description":"Once some tasks have been performed, the URLs table will have a lot of entries. This task will check all the URLS in order to find new subdomains.", "type":"Retrieve"},
    {"name_id":"getURLsTask","name":"Get URLs", "description":"It searches all URLs cached by Wayback Machine and saves them into the database. This will later help to discover other data entities like files or subdomains.", "type":"Retrieve"},
    {"name_id":"getFilesFromURLsTask","name":"Get Files from URLs", "description":"It loops through the URLs database table in order to find files and store them to the Files database. The files that will be retrieved are: doc, docx, ppt, pptx, pps, ppsx, xls, xlsx, odt, ods, odg, odp, sxw, sxc, sxi, pdf, wpd, svg, indd, rdp, ica, zip, rar", "type":"Retrieve"},
    {"name_id":"findEmailsTask","name":"Find Emails", "description":"It looks for emails using queries to Google and Bing.", "type":"Retrieve"},
    {"name_id":"findSocialProfilesByEmailTask","name":"Find People from Emails", "description":"Once some emails have been found it can be useful to discover the person behind them. Also, it finds usernames from that people.", "type":"Retrieve"},
    {"name_id":"findEmailsFromURLsTask","name":"Find Emails From URLs", "description":"Sometimes, the discoverd URLs can contain sentive information. This tasks retrive all the emails from URL paths.", "type":"Retrieve"},
    {"name_id":"executeDorksTask","name":"Execute Dorks", "description":"It will execute the dorks defined in the dorks folder. Remember to grup the dorks by categories (filename) so you can later understand the objectives of the dorks.", "type":"Retrieve"},
    {"name_id":"findEmailsFromDorksTask","name":"Find Emails From Dorks", "description":"By default, InfoHound has some dorks defined in order to discover emails. This task will look for them in the results obtained by the execution of the dorks.", "type":"Retrieve"},
    {"name_id":"findPeopleFromGoogleTask","name":"Find People From Google", "description":"Uses the Google JSON API to find people who work in the company asociated to the domain.", "type":"Retrieve"},
    # ANALYSIS
    {"name_id":"subdomainTakeOverAnalysisTask","name":"Check Subdomains Take-Over", "description":"It performes some checks to determine if a subdomain can be taken over.", "type":"Analysis"},
    {"name_id":"canBeSpoofedTask","name":"Check If Domain Can Be Spoofed", "description":"It checks if a domain, from the emails InfoHound has discovered, can be spoofed. This could be used by attackers to impersonate a person and send emails as hime/her.", "type":"Analysis"},
    {"name_id":"getProfilesTask","name":"Get Profiles From Usernames", "description":"This task uses the discoverd usernames from each person in order to find profiles from services or social networks where that username exist. This is performed using Maigret tool. It is worth to be noted that, although a profile with the same username is found, it does not necessary mean it is from the person being analised.", "type":"Analysis"},
    {"name_id":"downloadAllFilesTask","name":"Download All Files", "description":"Once files have been stored in the Files database table, this task will download them in the download_files folder.", "type":"Analysis"},
    {"name_id":"getMetadataTask","name":"Get Metadata", "description":"Using exiftool this task will extract all the metadata from the downloaded files and save it to the database.", "type":"Analysis"},
    {"name_id":"getEmailsFromMetadataTask","name":"Get Emails From Metadata", "description":"As some metadata can contain emails, this will retrive all o them and save it to the database.", "type":"Analysis"},
    {"name_id":"getEmailsFromFilesContentTask","name":"Get Emails From Files Content", "description":"Usually emails can be included in corporate files so this task will retrive all the emails from the downloaded files content.", "type":"Analysis"},
    {"name_id":"findRegisteredSitesTask","name":"Find Registered Services using emails", "description":"It is possible to find services or social networks where an emaill has been used to create an account. This task will check if an email InfoHound has discovered has an account in: Twitter, Adobe, Facebook, Imgur, Mewe, Parler, Rumble, Snapchat, Wordpress and/or Duolingo", "type":"Analysis"},
    {"name_id":"checkBreachTask","name":"Check Breach", "description":"This task checks Firefox Monitor service to see if an email has been found in a data breach. Although it is a free service, it has a limitation of 10 queries per day. If Leak-Lookup API key is set, it also checks it.", "type":"Analysis"},
    {"name_id":"summarizeProfileTask","name":"AI-Powered Profile Analisys", "description":"You can use the profile analysis task to employ an AI-powered tool that examines the metadata and creates a description for you.", "type":"Analysis"},
    {"name_id":"getLeakedPasswordsTask","name":"Get leaked passwords", "description":"Using Proxy Nova's free service, InfoHound can detect and display passwords from usernames found that have been leaked in the past.", "type":"Analysis"}]
    for task in tasks:
        try:
            Tasks.objects.get_or_create(tid=task["name_id"], name=task["name"], description=task["description"], task_type=task["type"], custom=False, domain_id=domain_id)
        except IntegrityError as e:
            pass


def load_custom_tasks(domain_id):
    plugins_dir = 'infohound/tool/custom_modules'
    for filename in os.listdir(plugins_dir):
        if filename.endswith('.py'):
            module_name = filename[:-3]  # remove .py extension
            module_path = "infohound.tool.custom_modules."+module_name
            module = importlib.import_module(module_path)
            try:
                Tasks.objects.get_or_create(tid=module.MODULE_ID, name=module.MODULE_NAME, description=module.MODULE_DESCRIPTION, task_type=module.MODULE_TYPE, custom=True, domain_id=domain_id)
            except IntegrityError as e:
                pass

def load_dorks(domain_id):
    domain = Domain.objects.get(id=domain_id).domain

    dorks_dir = 'infohound/tool/dorks/'
    for filename in os.listdir(dorks_dir):
        with open(dorks_dir+filename, "r") as file:
            category = filename.split("/")[-1].split(".")[0]
            for line in file:
                if "<domain>" in line:
                    d = line.rstrip().replace("<domain>",domain)
                else:
                    d = line.rstrip()+'"'+domain+'"'
                try:
                    Dorks.objects.get_or_create(dork=d,category=category,domain_id=domain_id)
                except IntegrityError as e:
                    pass
    

def execute_initital(domain_id):
    tasks_name = ["getWhoisInfoTask","getDNSRecordsTask","getSubdomainsTask", "getURLsTask", "getSubdomainsFromURLSTask", 
                    "findEmailsTask", "findEmailsFromURLsTask", "findSocialProfilesByEmailTask"]
    job = group([
        # RETRIEVE
        tasks_list.getWhoisInfoTask.s(domain_id),
        tasks_list.getDNSRecordsTask.s(domain_id),
        tasks_list.getSubdomainsTask.s(domain_id),
        tasks_list.getURLsTask.s(domain_id),
        tasks_list.getSubdomainsFromURLSTask.s(domain_id),
        tasks_list.findEmailsTask.s(domain_id),
        tasks_list.findEmailsFromURLsTask.s(domain_id),
        tasks_list.findSocialProfilesByEmailTask.s(domain_id),
        ])
    result = job.apply_async()
    for i, t in enumerate(result.results):
        try:
            Tasks.objects.filter(tid=tasks_name[i], domain_id=domain_id).update(celery_id=t.id, last_execution=timezone.now())
        except IntegrityError as e:
            pass


async def init(domain_id):
    load_tasks(domain_id)
    load_custom_tasks(domain_id)
    execute_initital(domain_id)


