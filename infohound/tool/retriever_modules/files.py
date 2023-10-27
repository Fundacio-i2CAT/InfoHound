import requests
import trio
import infohound.tool.infohound_utils as infohound_utils
import infohound.infohound_config as config
from django.db import IntegrityError
from infohound.models import Domain,Files,URLs
from django.db.models import Subquery
from infohound.tool.data_sources import archive
from urllib.parse import urlparse


file_types = ["doc","docx","ppt","pptx","pps","ppsx","xls","xlsx",
			  "odt","ods","odg","odp",
			  "sxw","sxc","sxi",
			  "pdf","wpd","svg","indd","rdp","ica","zip","rar"]

#concurrency_limit = trio.CapacityLimiter(5)


async def process_url(url, source, domain_id):
	path = urlparse(url).path
	ext = path.split(".")[-1:][0]
	fname = path.split("/")[-1:][0]
	if ext in file_types:
		url_file = ""
		if source == "Archive":
			# Try to download - Max: 5 retries
			retry = 0
			found = False
			while retry < 5 and not found:
				try:
					url_file = await archive.get_download_url(url)
					found = True
				except Exception as e:
					print("Retrying " + str(retry))
					retry = retry+1
					if retry==5:
						print("Giving up on this one")
		else:
			url_file = url
		if url_file != "":
			u = URLs.objects.get(url=url)
			try:
				Files.objects.get_or_create(url=u, url_download=url_file, filename=fname, source=source, domain_id=domain_id)
			except IntegrityError as e:
				pass
			print(url_file)

async def get_files_from_urls(domain_id):
	domain = Domain.objects.get(id=domain_id)
	domain_name = domain.domain
	full_passive = domain.full_passive
	present_urls = [entry.url_id for entry in Files.objects.filter(domain_id=domain_id)]
	urls = {entry.url: entry.source for entry in URLs.objects.filter(domain_id=domain_id).exclude(url__in=present_urls)}
	print("Starting gathering download URLS")
	async with trio.open_nursery() as nursery:
		async for url in infohound_utils.async_list_iterator(urls):
			if domain_name in urlparse(url).netloc and full_passive:
				pass
			source = urls[url]
			nursery.start_soon(process_url, url, source, domain_id)

