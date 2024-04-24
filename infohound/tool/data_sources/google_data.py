import requests
import json
import html
import time
import urllib.parse
import infohound.tool.infohound_utils as infohound_utils
from bs4 import BeautifulSoup
from random import randint
import infohound.infohound_config as config

API_KEY = config.GOOGLE_API_KEY
ID = config.GOOGLE_ID


def getUrls(query):
    start = 1
    total_results = 0
    total_gathered = 0
    limit = False
    results = True
    info = []

    print("Testing query: " + query)

    while results and start<100 and not limit:
        payload = {"key":API_KEY,"cx":ID,"start":start,"q":query}
        res = requests.get("https://www.googleapis.com/customsearch/v1",params=payload)
        data = json.loads(res.text)
        if "error" in data:
            print(data["error"]["status"])
            limit = True
        else:
            if start == 1:
                total_results = data["searchInformation"]["totalResults"]
            if "items" in data:
                for item in data["items"]:
                    url = item["link"]
                    desc = None
                    if "snippet" in item:
                        desc = item["snippet"]
                    info.append((url,desc,json.dumps(item)))
                    total_gathered = total_gathered + 1
            else:
                results = False
        start = start + 10
        
    print("Found "+str(total_results)+" and added "+str(total_gathered))
    return (info,total_results,total_gathered,limit)

    #- vulnerable paths
    #- files
    #- url

def discoverPeople (query):
    start = 1
    total_results = 0
    total_gathered = 0
    limit = False
    results = True
    people = []

    print("Testing query: " + query)

    while results and start < 100 and not limit:
        payload = {"key":API_KEY,"cx":ID,"start":start,"q":query}
        res = requests.get("https://www.googleapis.com/customsearch/v1",params=payload)
        data = json.loads(res.text)
        if "error" in data:
            print(data["error"]["status"])
            limit = True
        else:
            if start == 1:
                total_results = data["searchInformation"]["totalResults"]
            if "items" in data:
                for item in data["items"]:
                    try:
                        url = item["link"]
                        first_name = item["pagemap"]["metatags"][0]["profile:first_name"]
                        last_name = item["pagemap"]["metatags"][0]["profile:last_name"]
                        url_img = item["pagemap"]["cse_image"][0]["src"]
                        name = f"{first_name} {last_name}"
                        people.append((name,url,json.dumps(item),url_img))
                        print("Added: " + name)
                        total_gathered = total_gathered + 1
                    except KeyError as e:
                        print(f"Error: The key '{e.args[0]}' is not present in the results.")
                    except Exception as e:
                        print(f"Unexpected error: {str(e)}")
            else:
                results = False
        start = start + 10
        time.sleep(1)
        
    print("Found "+str(total_results)+" and added "+str(total_gathered))
    return (people)

def discoverEmails(domain):
    emails = []
    start = 0
    total = 200
    num = 50
    iterations = int(total/num)
    if (total%num) != 0:
        iterations += 1
    url_base = f"https://www.google.com/search?q=intext:@{domain}&num={num}"
    cookies = {"CONSENT": "YES+srp.gws"}
    while start < iterations:
        try:
            url = url_base + f"&start={start}"
            user_agent = infohound_utils.getUserAgents()
            response = requests.get(url,
                headers=user_agent[randint(0, len(user_agent)-1)],
                allow_redirects=False,
                cookies=cookies,
                proxies=None
            )
            escaped_text = response.text.encode('utf-8').decode('unicode_escape')
            text = urllib.parse.unquote(html.unescape(escaped_text))
            
            if response.status_code == 302 and ("htps://www.google.com/webhp" in text or "https://consent.google.com" in text):
                return emails
            elif "detected unusual traffic" in text:
                return emails
            #emails = emails + infohound_utils.extractEmails(domain, text)
            for e in infohound_utils.extractEmails(domain, text):
                if e not in emails:
                    emails.append(e)
            soup = BeautifulSoup(text, "html.parser")
            # h3 is the title of every result
            if len(soup.find_all("h3")) < num:
                break
        except Exception as ex:
            raise ex #It's left over... but it stays there
        start += 1
    return emails

def discoverSocialMedia(domain,email):
    data = {}
    links = []
    name = ""
    
    num = 50
    username = email.split("@")[0]
    scope = email.split("@")[1]
    
    url = f"https://www.google.com/search?q='{username}' {scope}"
    # Seems that this trick does not work any more
    cookies = {"CONSENT": "YES+","SOCS":"CAISHAgCEhJnd3NfMjAyNDAxMzEtMF9SQzQaAmVzIAEaBgiAkIuuBg"}
    
    try:
        user_agent = infohound_utils.getUserAgents()
        response = requests.get(url,
            headers=user_agent[randint(0, len(user_agent)-1)],
            allow_redirects=False,
            cookies=cookies,
            proxies=None
        )
        
        text = response.content

        if response.status_code == 302 and ("htps://www.google.com/webhp" in text or "https://consent.google.com" in text):
            raise GoogleCookiePolicies()
        elif "detected unusual traffic" in text:
            raise GoogleCaptcha()
        links = infohound_utils.extractSocialInfo(text)

        if links != []:
            soup = BeautifulSoup(text, "html.parser")
            if len(soup.find_all("h3")) >= 2:
                info = soup.find_all("h3")[0].string
                if "-" in info:
                    info = info.string.split("-")[0]
                if "," in info:
                    info = info.split(",")[0]
                name = info.strip()

        data["links"] = links
        data["name"] = name
    except Exception as ex:
        raise ex #It's left over... but it stays there
    return data

def discoverSocialMediaByDorks(domain,email):
    data = {}
    links = []
    name = ""
    url_img = None
    info_dump = None
    limit = False
    
    num = 50
    username = email.split("@")[0]
    scope = email.split("@")[1]

    payload = {'key':API_KEY,'cx':ID,'start':1,'q':f'"{username}" {scope}'}
    res = requests.get("https://www.googleapis.com/customsearch/v1",params=payload)
    info = json.loads(res.content)
    if "error" in info:
        print(info["error"]["status"])
        limit = True
    else:
        if "items" in info:
            found_linkedin = False 
            found_twitter = False
            for item in info["items"]:
                try:
                    if "linkedin" in item["link"] and not found_linkedin:
                        l = item["link"].split("?")[0] if "?" in item["link"] else item["link"]
                        first_name = item["pagemap"]["metatags"][0]["profile:first_name"]
                        last_name = item["pagemap"]["metatags"][0]["profile:last_name"]
                        name = f"{first_name} {last_name}"
                        url_img = item["pagemap"]["cse_image"][0]["src"]
                        info_dump = json.dumps(item)
                        links.append(l)
                        found_linkedin = True
                    if "twitter" in item["link"] and not found_twitter:
                        l = item["link"].split("?")[0] if "?" in item["link"] else item["link"]
                        name = item["pagemap"]["person"][0]["givenname"]
                        if not url_img:
                            url_img = item["pagemap"]["cse_image"][0]["src"]
                        if not info_dump:
                            info_dump = json.dumps(item)
                        links.append(l)
                        found_twitter = True
                    if found_twitter and found_linkedin:
                        break
                except KeyError as e:
                        print(f"Error: The key '{e.args[0]}' is not present in the results.")
                except Exception as e:
                    print(f"Unexpected error: {str(e)}")

    data["links"] = links
    data["name"] = name
    data["url_img"] = url_img
    data["info_dump"] = info_dump
    return data
