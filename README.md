# InfoHound - OSINT tool for domain profiling
During the reconnaissance phase, an attacker searches for any information about his target to create a profile that will later help him to identify possible ways to get in an organization. InfoHound performs passive analysis techniques (which do not interact directly with the target) using OSINT to extract a large amount of data given a web domain name. This tool will retrieve emails, people, files, subdomains, usernames and urls that will be later analyzed to extract even more valuable information. 

## :house: Infohound architecture
<p align="center"><img src="https://github.com/Fundacio-i2CAT/InfoHound/blob/main/infohound_diagram.jpg" alt="Infohound diagram" ></p>

## 🛠️ Installation
```
git clone https://github.com/Fundacio-i2CAT/InfoHound.git
cd InfoHound/infohound
mv infohound_config.sample.py infohound_config.py
cd ..
docker-compose up -d
```
You can now access infohound navigating with your browser to:
```
http://localhost:8000/infohound/
```
**NOTE:** You must add API Keys inside infohound_config.py file

#### Google Programmable Search Engine API
* [Create your custom engine and get the ID](https://programmablesearchengine.google.com/controlpanel/all)
* [Create API KEY](https://developers.google.com/custom-search/v1/overview)

## Default modules
InfoHound has 2 different types of modules, those which retreives data and those which analyse it to extract more relevant information.
### :mag: Retrieval modules
| Name | Description |
| ---- | ----------- |
| Get Whois Info | Get relevant information from Whois register. |
| Get DNS Records | This task queries the DNS. |
| Get Subdomains | This task uses Alienvault OTX API, CRT.sh, and HackerTarget as data sources to discover cached subdomains. |
| Get Subdomains From URLs | Once some tasks have been performed, the URLs table will have a lot of entries. This task will check all the URLs to find new subdomains. |
| Get URLs | It searches all URLs cached by Wayback Machine and saves them into the database. This will later help to discover other data entities like files or subdomains. |
| Get Files from URLs | It loops through the URLs database table to find files and store them in the Files database table for later analysis. The files that will be retrieved are: doc, docx, ppt, pptx, pps, ppsx, xls, xlsx, odt, ods, odg, odp, sxw, sxc, sxi, pdf, wpd, svg, indd, rdp, ica, zip, rar |
| Find Email | It looks for emails using queries to Google and Bing. |
| Find People from Emails | Once some emails have been found, it can be useful to discover the person behind them. Also, it finds usernames from those people. |
| Find Emails From URLs | Sometimes, the discovered URLs can contain sensitive information. This task retrieves all the emails from URL paths. |
| Execute Dorks | It will execute the dorks defined in the dorks folder. Remember to group the dorks by categories (filename) to understand their objectives. |
| Find Emails From Dorks | By default, InfoHound has some dorks defined to discover emails. This task will look for them in the results obtained from dork execution. |

### :microscope: Analysis
| Name | Description |
| ---- | ----------- |
| Check Subdomains Take-Over | It performs some checks to determine if a subdomain can be taken over. |
| Check If Domain Can Be Spoofed | It checks if a domain, from the emails InfoHound has discovered, can be spoofed. This could be used by attackers to impersonate a person and send emails as him/her. |
| Get Profiles From Usernames | This task uses the discovered usernames from each person to find profiles from services or social networks where that username exists. This is performed using the [Maigret](https://github.com/soxoj/maigret) tool. It is worth noting that although a profile with the same username is found, it does not necessarily mean it belongs to the person being analyzed. |
| Download All Files | Once files have been stored in the Files database table, this task will download them in the "download_files" folder. |
| Get Metadata | Using exiftool, this task will extract all the metadata from the downloaded files and save it to the database. |
| Get Emails From Metadata | As some metadata can contain emails, this task will retrieve all of them and save them to the database. |
| Get Emails From Files Content | Usually, emails can be included in corporate files, so this task will retrieve all the emails from the downloaded files' content. |
| Find Registered Services using Emails | It is possible to find services or social networks where an email has been used to create an account. This task will check if an email InfoHound has discovered has an account in Twitter, Adobe, Facebook, Imgur, Mewe, Parler, Rumble, Snapchat, Wordpress, and/or Duolingo. |
| Check Breach | This task checks Firefox Monitor service to see if an email has been found in a data breach. Although it is a free service, it has a limitation of 10 queries per day. If Leak-Lookup API key is set, it also checks it. |

## :pill: Custom modules
InfoHound lets you create custom modules, you just need to add your script inside `infohoudn/tool/custom_modules`. One custome module has been added as an example which uses [Holehe](https://github.com/megadose/holehe) tool to check if the emails previously are attached to an account on sites like Twitter, Instagram, Imgur and more than 120 others. 

```
# Import the packages you need
import trio
import httpx
import requests
from holehe import core

# Import the Django models you will work with
from infohound.models import Emails

MODULE_ID = "findRegisteredSitesHoleheCustomTask" # Set a module ID
MODULE_NAME = "Find sites with Holehe" # Set a module name
MODULE_DESCRIPTION = "Using Holehe tool, this task will find where an email has been used to create an account. Holehe checks more than 120 sites."  # Set a description
MODULE_TYPE = "Analysis" # Set the type: Analysis or Retrieve


# This function is the only function it will be called by InfoHound
# Change its content and create other the functions if needed
def custom_task(domain_id):
	trio.run(findRegisteredSitesHolehe, domain_id)


async def findRegisteredSitesHolehe(domain_id):
	queryset = Emails.objects.filter(domain_id=domain_id)
	for entry in queryset.iterator():
		out = []
		email = entry.email

		modules = core.import_submodules("holehe.modules")
		websites = core.get_functions(modules)
		client = httpx.AsyncClient()

		for website in websites:
			await core.launch_module(website, email, client, out)
			print(out)
		await client.aclose()

		services = []
		for item in out:
			if item["exists"]:
				services.append(item["name"])

		entry.registered_services = services
		entry.save()
```

## :camera: Screenshots
<p align="center"><img src="https://github.com/xampla/InfoHound/blob/main/email_tab.png" alt="Emails tab" width="60%"></p>

## :eight_spoked_asterisk: Export to GraphML
Do you want to create a visualization graph with the findings? You can export the whole domain analysis to a GraphML file and open it with yED, Gephi or any tool of your choice. It currently exports files, people, emails, social profiles, registered sites and usernames. URLs and subdomains are not included due to the amount of results.
<p align="center"><img src="https://github.com/xampla/InfoHound/blob/main/graph_example.png" alt="Graph visualization example" width="50%"></p>

## :bulb: Inspired by
* [Holehe](https://github.com/megadose/holehe)
* [Maigret](https://github.com/soxoj/maigret)
* [reconFTW](https://github.com/six2dez/reconftw)
* [Poastal](https://github.com/jakecreps/poastal)
* And many others

# Copyright
This code has been developed by Fundació Privada Internet i Innovació Digital a Catalunya (i2CAT).

i2CAT is a *non-profit research and innovation centre* that  promotes mission-driven knowledge to solve business challenges, co-create solutions with a transformative impact, empower citizens through open and participative digital social innovation with territorial capillarity, and promote pioneering and strategic initiatives.

i2CAT *aims to transfer* research project results to private companies in order to create social and economic impact via the out-licensing of intellectual property and the creation of spin-offs.

Find more information of i2CAT projects and IP rights at https://i2cat.net/tech-transfer/


# License
This code is licensed under the terms *AGPLv3*. Information about the license can be located at [link](https://www.gnu.org/licenses/agpl-3.0.html).

If you find that this license doesn't fit with your requirements regarding the use, distribution or redistribution of our code for your specific work, please, don’t hesitate to contact the intellectual property managers in i2CAT at the following address: techtransfer@i2cat.net
