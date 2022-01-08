from bs4 import BeautifulSoup
import requests

import re

senator_list_html = requests.get('https://www.nysenate.gov/senators-committees').text

url_root = "https://www.nysenate.gov"

list_soup = BeautifulSoup(senator_list_html)

senator_urls = set()
for link in list_soup.find_all('a'):
    href = link.get('href')
    if href is not None and href.startswith('/senators/'):
        senator_urls.add(url_root + href + "/contact")

# print(senator_urls)

def extract_contact_info(address_section):
    phone = address_section.find('span', string="Phone: ")
    fax = address_section.find('span', string="Fax: ")
    return {
        "phone": phone and phone.next_sibling,
        "fax": fax and fax.next_sibling,
    }

for contact_url in senator_urls:
    print(contact_url)
    contact_page = requests.get(contact_url).text
    contact_soup = BeautifulSoup(contact_page)
    address_tags = contact_soup.find_all('div', class_='location vcard')
    district = [t for t in address_tags if 'district office' in str(t).lower()]
    albany = [t for t in address_tags if 'albany office' in str(t).lower()]

    email = contact_soup.find('div', class_='c-block--senator-email').find('div', class_='field-content').find('a').string

    results = {
        "email": email,
        "district": [],
        "albany": [],
        "name": contact_soup.find('span', class_="c-senator-hero--name").find('a').string
    }
    for d in district:
        results['district'].append(extract_contact_info(d))
    
    for a in albany:
        results['albany'].append(extract_contact_info(a))
    
    print(results)