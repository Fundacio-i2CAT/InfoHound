import re
import psycopg2
from bs4 import BeautifulSoup
from infohound.models import Tasks
from django.db import IntegrityError


def getUserAgents():
    user_agent = {
        0: {'User-agent': 'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.86 Mobile Safari/537.36'},
        1: {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'},
        2: {'User-agent': 'Opera/9.80 (Linux armv7l) Presto/2.12.407 Version/12.51 , D50u-D1-UHD/V1.5.16-UHD (Vizio, D50u-D1, Wireless)'},
        3: {'User-agent': 'BrightSign/7.1.95 (XT1143) Mozilla/5.0 (Unknown; Linux arm) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.6.0 Chrome/45.0.2454.101 Safari/537.36'},
        4: {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.24 Safari/537.36'},
        5: {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'},
        6: {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
    }
    return user_agent

def extractEmails(domain, text):
    regex = r"[\%a-zA-Z\.0-9_\-\+]+@" + domain
    emails = re.findall(regex, text.replace("<em>", "").replace("<\em>","")
                                .replace("<strong>", "").replace("</strong>", "")
                                .replace("<b>", "").replace("</b>", ""))
    return emails

def extractSocialInfo(text):
    data = []

    # Linkedin
    regex = r"(http(s)?:\/\/)?([\w]+\.)?linkedin\.com\/(in)\/[^&\"\/]*"
    t = re.search(regex, text)
    if t is not None:
         data.append(t.group(0))

    # Twitter
    regex = r"(http(s)?:\/\/)?([\w]+\.)?twitter\.com\/[^&\/?\"\%]*"
    t = re.search(regex, text)
    if t is not None:
         data.append(t.group(0))
    return data

async def async_list_iterator(lst):
    for item in lst:
        yield item


