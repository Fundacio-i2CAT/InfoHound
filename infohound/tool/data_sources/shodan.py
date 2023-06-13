import shodan
import infohound.infohound_config as config

def getIndo(IP):
	api = shodan.Shodan(config.SHODAN_KEY)
	return api.host(IP)

def getSubdomains(domain):
	api = shodan.Shodan(config.SHODAN_KEY)
	data = []
	more = True
	i = 1
	while more:
		info = api.dns.domain_info(domain='domain', history=False, type=None, page=i)
		more = info["more"]
		data += info["subdomains"]
		i+=1
	print(data)


	