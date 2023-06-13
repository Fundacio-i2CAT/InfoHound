import re
import requests
import sqlite3
import html
import json
import urllib.parse
from email_validator import validate_email, EmailNotValidError
from django.db import IntegrityError
from infohound.tool.data_sources import google_data
import infohound.tool.infohound_utils as infohound_utils
from infohound.tool.data_sources import bing_data
from infohound.models import Domain,Emails, URLs, Results
import infohound.infohound_config as config


def getEmailsFromText(text):
	emails = re.findall(r'([\%a-zA-Z\.0-9_\-\+]+@[a-zA-Z\.0-9\-]+\.[a-zA-Z\.0-9\-]+)',text)
	return emails

def isValidEmail(email_test):
	res = (False, None)
	try:
		emailinfo = validate_email(email_test, check_deliverability=True)
		email = emailinfo.normalized.lower()
		res = (True, email)
	except EmailNotValidError as e:
		pass
	return res


def findEmails(domain_id):
	domain = Domain.objects.get(id=domain_id).domain
	emails_google = google_data.discoverEmails(domain)
	for email in emails_google:
		(valid, em) = isValidEmail(email)
		if valid:
			try:
				Emails.objects.get_or_create(email=em, source="Google", domain_id=domain_id)
			except IntegrityError as e:
				pass
		else:
			print("Not valid email found: " + email)
	emails_bing = bing_data.discoverEmails(domain)
	for email in emails_bing:
		(valid, em) = isValidEmail(email)
		if valid:
			try:
				Emails.objects.get_or_create(email=em, source="Bing", domain_id=domain_id)
			except IntegrityError as e:
				pass
		else:
			print("Not valid email found: " + email)


def findEmailsFromURLs(domain_id):
	domain = Domain.objects.get(id=domain_id).domain
	queryset = URLs.objects.filter(domain_id=domain_id)
	for entry in queryset.iterator():
		text = urllib.parse.unquote(html.unescape(entry.url))
		email_list = infohound_utils.extractEmails(domain,text)
		for email in email_list:
			(valid, em) = isValidEmail(email)
			if valid:
				try:
					Emails.objects.get_or_create(email=em, source="URLs",domain_id=domain_id)
				except IntegrityError as e:
					pass


def findEmailsFromDorks(domain_id):
	domain = Domain.objects.get(id=domain_id).domain
	queryset = Results.objects.filter(domain_id=domain_id)
	for entry in queryset.iterator():
		text = json.dumps(entry.all_info)
		email_list = infohound_utils.extractEmails(domain,text)
		for email in email_list:
			(valid, em) = isValidEmail(email)
			if valid:
				try:
					Emails.objects.get_or_create(email=em, source="Dorks",domain_id=domain_id)
				except IntegrityError as e:
					pass

	
	
	


