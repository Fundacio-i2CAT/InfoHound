# InfoHound - OSINT organization profiler tool
During the reconnaissance phase, an attacker searches for any information about his target to create a profile that will later help him to identify possible ways to get in an organization. InfoHound performs passive analysis techniques (which do not interact directly with the target) using OSINT to extract a large amount of data given a web domain name. This tool will retrieve emails, people, files, subdomains, usernames and urls that will be later analyzed to extract even more valuable information. 

## Infohound architecture
![InfoHound](https://github.com/xampla/InfoHound/blob/main/infohound_diagram.jpg)

## 🛠️ Installation
```
git clone https://github.com/xampla/InfoHound.git
cd InfoHound
mv infohound_config.sample.py infohound_config.py
docker-compose up -d
```
You must add API Keys inside infohound_config.py file
## Default modules
TBD
## Custom modules
TBD

