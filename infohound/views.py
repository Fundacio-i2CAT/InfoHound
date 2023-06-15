import os
import trio
import importlib
from datetime import datetime
from celery.result import AsyncResult
from django.shortcuts import render
from django.http import JsonResponse
from infohound.models import Domain, People, Files, Emails, Subdomains, URLs, Dorks, Results, Usernames, Tasks
import infohound.tasks
import infohound.utils
from django.utils import timezone
import infohound.tool.retriever_modules.dorks as dorks
from django.db import IntegrityError
from django.utils.safestring import mark_safe

def index(request):
    return render(request, 'index.html')

def add_domain(request):
    domain_name = request.GET['domain']
    full_passive = False if request.GET['full_passive'] == "false" else True
    print(full_passive)
    if Domain.objects.filter(domain=domain_name).exists():
        data = {'error': "Invalid domain"}
    else:
        d = Domain.objects.create(domain=domain_name,full_passive=full_passive)
        trio.run(infohound.utils.init, d.id)
        data = {'msg': "Domain correctly added"}
    return JsonResponse(data)

def get_general_view(request):
    return render(request, 'tabs_content/general.html')

def get_subdomains_view(request):
    return render(request, 'tabs_content/subdomains.html')

def get_people_view(request):
    return render(request, 'tabs_content/people.html')

def get_emails_view(request):
    return render(request, 'tabs_content/emails.html')

def get_tasks_view(request):
    return render(request, 'tabs_content/tasks.html')

def get_dorks_view(request):
    return render(request, 'tabs_content/dorks.html')

def get_domains(request):
    data = []
    domain = Domain.objects.all().order_by("id")
    for entry in domain.iterator():
        data.append({"id":entry.id, "domain":entry.domain})
    return JsonResponse(data, safe=False)

def domain_info(request, domain_id):
    domain = Domain.objects.get(id=domain_id)
    print(domain.dns_records)
    if domain.whois_data or domain.dns_records:
        data = {'whois': domain.whois_data, 'dns': domain.dns_records}
    else:
        data = {'error': "Add a domain"}
    return JsonResponse(data)


def people_view(request):
    domain_id = request.GET['domain_id']
    people_data = list(People.objects.filter(domain_id=domain_id).values())
    return JsonResponse(people_data, safe=False)

def people_all(request):
    data = []
    domain_id = request.GET['domain_id']
    people_data = People.objects.filter(domain_id=domain_id)
    for entry in people_data.iterator():
        p = {}
        p["id"] = entry.id
        p["name"] = entry.name
        p["phones"] = len(entry.phones)
        p["accounts"] = 0
        user = Usernames.objects.filter(people=entry, domain_id=domain_id)
        emails = Emails.objects.filter(people=entry, domain_id=domain_id)
        for em in user.iterator():
            p["accounts"] += len(em.profiles)
        p["emails"] = len(emails)
        p["keys"] = Usernames.objects.filter(people=entry, domain_id=domain_id).count()
        for profile in entry.social_profiles:
            if "linkedin" in profile:
                p["linkedin"] = profile
            elif "facebook" in profile:
                p["facebook"] = profile
            elif "twitter" in profile:
                p["twitter"] = profile
        data.append(p)

    return JsonResponse(data, safe=False)

def get_subdomains(request):
    data = []
    domain_id = request.GET['domain_id']
    subdomains = Subdomains.objects.filter(domain_id=domain_id)
    for entry in subdomains.iterator():
        data.append({"subdomain":entry.subdomain,"is_active":entry.is_active,"takeover":entry.takeover, "source":entry.source})
    return JsonResponse(data, safe=False)

def get_person_details(request, person_id):
    data = {}
    domain_id = request.GET['domain_id']
    person = People.objects.get(id=person_id, domain_id=domain_id)
    emails = Emails.objects.filter(people=person, domain_id=domain_id)
    data["name"] = person.name
    data["emails"] = []
    for entry in emails.iterator():
        data["emails"].append({"email":entry.email, "services":entry.registered_services})

    data["usernames"] = []
    usernames = Usernames.objects.filter(people=person, domain_id=domain_id)
    for entry in usernames.iterator():
        password = entry.password if entry.password is not None else "-"
        data["usernames"].append({"username":entry.username, "leaked":False, "password":password, "profiles": entry.profiles})
        
    return JsonResponse(data, safe=False)

def emails_view(request, domain_id):
    data = []
    emails_data = Emails.objects.filter(domain_id=domain_id).select_related('people').all()
    for entry in emails_data.iterator():
        person = "Unknown" if entry.people is None else entry.people.name
        services = "Unknown" if len(entry.registered_services) == 0 else entry.registered_services
        leak = "Unknown" if entry.is_leaked is None else entry.is_leaked
        spoofable = "Unknown" if entry.spoofable is None else entry.spoofable
        item = {
        "email":entry.email,
        "person":person,
        "leak":leak,
        "spoofable":spoofable,
        "source": entry.source}
        data.append(item)
    return JsonResponse(data, safe=False)

def people_count(request, domain_id):
    people_count = People.objects.filter(domain_id=domain_id).count()
    data = {"count":people_count}
    return JsonResponse(data)

def files_count(request, domain_id):
    files_count = Files.objects.filter(domain_id=domain_id).count()
    data = {"count":files_count}
    return JsonResponse(data)

def subdomains_count(request, domain_id):
    subdomains_count = Subdomains.objects.filter(domain_id=domain_id).count()
    data = {"count":subdomains_count}
    return JsonResponse(data)

def emails_count(request, domain_id):
    emails_count = Emails.objects.filter(domain_id=domain_id).count()
    data = {"count":emails_count}
    return JsonResponse(data)

def urls_count(request, domain_id):
    urls_count = URLs.objects.filter(domain_id=domain_id).count()
    data = {"count":urls_count}
    return JsonResponse(data)

def get_emails_stats(request, domain_id):
    total = 0
    identified = 0
    has_leak = 0
    has_services = 0
    spoofable = 0
    emails_data = Emails.objects.filter(domain_id=domain_id).select_related('people').all()
    for entry in emails_data.iterator():
        if entry.people is not None:
            identified += 1
        if len(entry.registered_services) != 0:
            has_services += 1
        if entry.is_leaked:
            has_leak += 1
        if entry.spoofable:
            spoofable += 1
        total += 1

    data = {"total": total, 
            "identified": identified,
            "has_leak": has_leak,
            "has_services": has_services,
            "spoofable": spoofable}
    return JsonResponse(data)

def get_available_tasks(request):
    infohound.utils.load_tasks(request.GET['domain_id'])
    infohound.utils.load_custom_tasks(request.GET['domain_id'])
    
    tasks = []
    queryset = Tasks.objects.filter(domain_id=request.GET['domain_id']).order_by('id')
    for entry in queryset.iterator():
        data = {}
        data["num"] = entry.id
        data["id"] = entry.tid
        data["name"] = entry.name
        data["description"] = entry.description
        data["type"] = entry.task_type
        data["custom"] = entry.custom
        if entry.last_execution:
            data["last_execution"] = entry.last_execution.strftime("%d/%m/%y %H:%M")
        if entry.celery_id:
            data["state"] = AsyncResult(entry.celery_id).state
        tasks.append(data)
    return JsonResponse(tasks, safe=False)


def execute_task(request):
    domain = Domain.objects.get(id=request.GET['domain_id'])
    tid = request.GET['tid']
    info = Tasks.objects.get(tid=tid, domain=domain)
    if not info.custom:
        t = getattr(infohound.tasks, tid)
    task = None
    if info.celery_id:
        result = AsyncResult(info.celery_id)
        if result.state != "PENDING":
            if info.custom:
                domain_path = "infohound.tool.custom_modules." + info.name
                task = infohound.tasks.executeCustomTask.delay(domain.id,domain_path)
            else:
                task = t.delay(domain.id)
            Tasks.objects.filter(tid=tid, domain=domain).update(celery_id=task.task_id, last_execution=timezone.now())
    else:
        if info.custom:
            domain_path = "infohound.tool.custom_modules." + info.name
            task = infohound.tasks.executeCustomTask.delay(domain.id,domain_path)
        else:
            task = t.delay(domain.id)
        Tasks.objects.filter(tid=tid, domain=domain).update(celery_id=task.task_id, last_execution=timezone.now())
    res = {}
    if task is None:
        res["error"] = "Task already in progress"
    else:
        res["task"] = task.task_id
    return JsonResponse(res, safe=False)

def get_task_status(request):
    tid = request.GET['tid']
    domain_id = request.GET['domain_id']
    task_id = Tasks.objects.get(tid=tid,domain_id=domain_id).celery_id
    if task_id:
        result = AsyncResult(task_id)
        res = {'msg': result.state}
    else:
        res = {'error': 'Task not created'}
    return JsonResponse(res, status=200)

def get_dorks_results(request):
    res = []
    queryset = Results.objects.filter(domain_id=request.GET['domain_id'])

    for entry in queryset.iterator():
        dork = Dorks.objects.get(id=entry.dork_id,domain_id=request.GET['domain_id'])
        url = URLs.objects.get(id=entry.url_id)
        res.append({"dork":dork.dork,"category":dork.category,"url":url.url})
    return JsonResponse(res, safe=False)

def delete_domain(request, domain_id):
    try:
        Domain.objects.get(id=domain_id).delete() 
        data = {'msg': "Domain correctly removed."}
        
    except Exception as e:
        data = {'error': "Something went wrong."}
    return JsonResponse(data, status=200)



    