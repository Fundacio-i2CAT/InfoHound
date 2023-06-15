import whois
import socket
import dns.resolver
import infohound.infohound_config as config
#from ipwhois import IPWhois
from infohound.models import Domain
from infohound.tool.data_sources import alienvault

def getWhoisInfo(domain_id):
    domain,b = Domain.objects.get_or_create(id=domain_id)
    info = {}
    try:
        whois_obj = whois.whois(domain.domain)
        #data = alienvault.getWhois(domain)
    

        info = {
            'domain_name': whois_obj.domain_name,
            'registrar': whois_obj.registrar,
            'whois_server': whois_obj.whois_server,
            'referral_url' : whois_obj.referal_url,
            'name_servers': whois_obj.name_servers,
            'status': whois_obj.status,
            'emails': whois_obj.emails,
            'dnssec': whois_obj.dnssec,
            'name': whois_obj.name,
            'org': whois_obj.org,
            'address': whois_obj.address,
            'city': whois_obj.city,
            'state': whois_obj.state,
            'zipcode': whois_obj.zipcode,
            'country': whois_obj.country,
        }

        if whois_obj.creation_date:
            info['creation_date'] = [d.strftime('%Y-%m-%d %H:%M:%S') for d in whois_obj.creation_date]
        if whois_obj.expiration_date:  
            info['expiration_date'] =[d.strftime('%Y-%m-%d %H:%M:%S') for d in whois_obj.expiration_date],
        if whois_obj.updated_date:
            info['updated_date'] =[d.strftime('%Y-%m-%d %H:%M:%S') for d in whois_obj.updated_date],
            
        domain.whois_data = info
        domain.save()
    except Exception as e:
        print(f"Error: {e}")

def get_dns_records(domain_id):
    domain = Domain.objects.get(id=domain_id)
    dns_records = {}

    # Query A records
    try:
        a_records = dns.resolver.resolve(domain.domain, 'A')
        dns_records['A'] = [record.to_text() for record in a_records]
    except Exception as e:
        print(f"Error fetching A records: {e}")

    # Query AAAA records
    try:
        aaaa_records = dns.resolver.resolve(domain.domain, 'AAAA')
        dns_records['AAAA'] = [record.to_text() for record in aaaa_records]
    except Exception as e:
        print(f"Error fetching AAAA records: {e}")

    # Query MX records
    try:
        mx_records = dns.resolver.resolve(domain.domain, 'MX')
        dns_records['MX'] = [record.to_text() for record in mx_records]
    except Exception as e:
        print(f"Error fetching MX records: {e}")

    # Query NS records
    try:
        ns_records = dns.resolver.resolve(domain.domain, 'NS')
        dns_records['NS'] = [record.to_text() for record in ns_records]
    except Exception as e:
        print(f"Error fetching NS records: {e}")

    # Query TXT records
    try:
        txt_records = dns.resolver.resolve(domain.domain, 'TXT')
        dns_records['TXT'] = [record.to_text() for record in txt_records]
    except Exception as e:
        print(f"Error fetching TXT records: {e}")

    print(dns_records)

    if dns_records:
        domain.dns_records = dns_records
        domain.save()

"""
def get_ip_address(domain): 
    ip_address = ""
    try:
        ip_address = socket.gethostbyname(domain)
    except socket.gaierror as e:
        print(f"Error resolving IP address: {e}")
    print(ip_address)

def get_hosting_info(ip_address):
    hosting_info = None
    try:
        ipwhois = IPWhois(ip_address)
        hosting_info = ipwhois.lookup_rdap() 
    except Exception as e:
        print(f"Error fetching hosting information: {e}")
    if hosting_info:
        print("\nHosting information:")
        print(f"  Network: {hosting_info['network']['cidr']}")
        print(f"  ASN: {hosting_info['asn']}")
        print(f"  ASN CIDR: {hosting_info['asn_cidr']}")
        print(f"  ASN description: {hosting_info['asn_description']}")
        print(f"  ASN Country: {hosting_info['asn_country_code']}")
        print(f"  IP range start: {hosting_info['network']['start_address']}")
        print(f"  IP range end: {hosting_info['network']['end_address']}")
"""
