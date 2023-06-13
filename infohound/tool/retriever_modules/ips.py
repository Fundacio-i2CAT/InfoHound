from data_sources import shodan

def getIPs():
	print("TO-DO")

def getInfoFromShodan(domain):
	queryset = IPs.objects.filter(all_info__isnull=True, domain_id=domain)
	for entry in queryset.iterator():
		ip = entry.ip
		data = shodan.getIndo(ip)
		entry.all_info = data
		entry.save()

