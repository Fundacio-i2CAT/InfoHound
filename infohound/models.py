from django.db import models

class Domain(models.Model):
    domain = models.CharField(max_length=255)
    whois_data = models.JSONField(null=True, default=None)
    dns_records = models.JSONField(null=True, default=None)
    full_passive = models.BooleanField(default=True)
    has_email_server = models.BooleanField(null=True, default=None)

class People(models.Model):
    name = models.CharField(max_length=255)
    phones = models.JSONField(default=list, null=True)
    social_profiles = models.JSONField(default=list)
    source = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

# TO-DO: change spoofable to allow 3 states
class Emails(models.Model):
    email = models.CharField(max_length=255)
    people = models.ForeignKey(People, on_delete=models.SET_NULL, null=True)
    registered_services = models.JSONField(default=list, null=True)
    spoofable = models.BooleanField(null=True)
    is_leaked = models.BooleanField(null=True)
    source = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('email', 'domain'),)

class Subdomains(models.Model):
    subdomain = models.CharField(max_length=255, primary_key=True)
    takeover = models.BooleanField(null=True, default=None)
    is_active = models.BooleanField(null=True, default=None)
    service = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('subdomain', 'domain'),)

class URLs(models.Model):
    url = models.TextField()
    source = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('url', 'domain'),)

class Files(models.Model):
    url = models.ForeignKey(URLs, on_delete=models.SET_NULL, null=True)
    url_download = models.TextField()
    filename = models.CharField(max_length=255)
    metadata = models.JSONField(null=True)
    source = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE) 

class Dorks(models.Model):
    dork = models.TextField()
    category = models.CharField(max_length=255)
    total_results = models.IntegerField(null=True)
    results_gathered = models.IntegerField(null=True)
    last_executed = models.DateField(null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('dork', 'domain'),)

class Results(models.Model):
    url = models.ForeignKey(URLs, on_delete=models.CASCADE)
    dork = models.ForeignKey(Dorks, on_delete=models.CASCADE)
    description = models.TextField()
    all_info = models.JSONField()
    last_detected = models.DateField()
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('url', 'dork', 'domain'),)

class Usernames(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, null=True)
    profiles = models.JSONField(default=list)
    people = models.ForeignKey(People, on_delete=models.SET_NULL, null=True)
    source = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('username', 'domain'),)

class Tasks(models.Model):
    tid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    celery_id = models.CharField(max_length=255, null=True)
    custom = models.BooleanField()
    TASK_TYPE_CHOICES = [("analysis", "Analysis"),("retrieve", "Retrieve")]
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES)
    last_execution = models.DateTimeField(null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('tid', 'domain'),)

class IPs(models.Model):
    ip = models.CharField(max_length=12, primary_key=True)
    all_info = models.TextField(null=True)
    is_vulnerable = models.BooleanField(null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)


