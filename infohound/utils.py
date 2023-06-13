import os
import importlib
import infohound.tasks as tasks_list
from celery import group
from infohound.models import Domain, Dorks, Tasks
from django.db import IntegrityError
from django.utils import timezone

def load_tasks(domain_id):
    tasks = [
    {"name_id":"getWhoisInfoTask","name":"Get Whois Info", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"getDNSRecordsTask","name":"Get DNS Records", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"getSubdomainsTask","name":"Get Subdomains", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"getSubdomainsFromURLSTask","name":"Get Subdomains From URLs", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"getURLsTask","name":"Get URLs", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"getFilesFromURLsTask","name":"Get Files from URLs", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"findEmailsTask","name":"Find Email", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"findSocialProfilesByEmailTask","name":"Find social profiles", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"findEmailsFromURLsTask","name":"Find Emails From Urls", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"executeDorksTask","name":"Execute dorks", "description":"TO-DO", "type":"Retrieve"},
    {"name_id":"findEmailsFromDorksTask","name":"Find Emails From Dorks", "description":"TO-DO", "type":"Retrieve"},
    # ANALYSIS
    {"name_id":"subdomainTakeOverAnalysisTask","name":"Check Subdomains Take-Over", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"canBeSpoofedTask","name":"Check If Domain Can Be Spoofed", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"getProfilesTask","name":"Get Profiles From Usernames", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"downloadAllFilesTask","name":"Download All Files", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"getMetadataTask","name":"Get Metadata", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"getEmailsFromMetadataTask","name":"Get Emails From Metadata", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"getEmailsFromFilesContentTask","name":"Get Emails From Files Content", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"findRegisteredSitesHoleheTask","name":"Execute Holehe", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"findRegisteredSitesTask","name":"Find Registered Services", "description":"TO-DO", "type":"Analysis"},
    {"name_id":"checkBreachTask","name":"Check Breach", "description":"TO-DO", "type":"Analysis"}]
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


