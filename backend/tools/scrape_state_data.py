"""
Scrapes the senate and assembly websites for contact info and other data about
representatives. Prints out a Python dict containing this data.

This dict should be placed into the static_data/senate_data.py and static_data/assembly_data.py
after visually inspecting it for any obvious mistakes.
"""

from bs4 import BeautifulSoup
import requests

import re

from src.app import app
from src.person.models import Person, Senator, AssemblyMember
import json
from pprint import pprint


SENATE_URL_ROOT = "https://www.nysenate.gov"



def convert_city(city):
    if city == "New York":
        return "Manhattan"
    
    return city

def _extract_senate_contact_info(address_section):
    phone = address_section.find('span', string="Phone: ")
    fax = address_section.find('span', string="Fax: ")
    city = address_section.find('span', class_="locality")
    return {
        "phone": phone and phone.next_sibling,
        "fax": fax and fax.next_sibling,
        "city": convert_city(re.compile('\w+[\s\w]*').search(city.string).group())
    }

def get_senate_data():
    print("Fetching main Senate directory page")
    senator_list_html = requests.get(f"{SENATE_URL_ROOT}/senators-committees").text
    list_soup = BeautifulSoup(senator_list_html)

    senator_urls_and_parties = set()
    for link in list_soup.find_all('a'):
        href = link.get('href')
        if href is not None and href.startswith('/senators/'):
            party_text = str(link.find('span', class_='nys-senator--party').string)
            if re.compile('[\( ]D[,\)]').search(party_text):
                party = "D"
            elif re.compile('[\( ]R[,\)]').search(party_text):
                party = "R"
            else:
                party = None

            senator_urls_and_parties.add((SENATE_URL_ROOT + href + "/contact", party))

    output = {}
    for contact_url, party in senator_urls_and_parties:
        print(f"Fetching senator detail page: {contact_url}")

        contact_page = requests.get(contact_url).text
        contact_soup = BeautifulSoup(contact_page)

        # This page has multiple divs each containing full address info. One is for Albany and the
        # rest are for the district.
        district_number = contact_soup.find_all('a', href=lambda href: href and href.startswith('/district/'))[0]['href'][len('/district/'):]
        address_tags = contact_soup.find_all('div', class_='location vcard')
        district_divs = [t for t in address_tags if 'district office' in str(t).lower()]
        albany_divs = [t for t in address_tags if 'albany office' in str(t).lower()]

        email = contact_soup.find('div', class_='c-block--senator-email').find('div', class_='field-content').find('a').string

        results = {
            "email": email,
            "district_contact": [],
            "albany_contact": [],
            "name": contact_soup.find('span', class_="c-senator-hero--name").find('a').string,
            "website": contact_url,
            "district": district_number,
            "party": party
        }
        for d in district_divs:
            results['district_contact'].append(_extract_senate_contact_info(d))
        
        for a in albany_divs:
            results['albany_contact'].append(_extract_senate_contact_info(a))
        
        output[results['district']] = results

    return output



def get_assembly_data():
    f"Fetching Assembly data"
    assembly_list_html = requests.get('https://www.nyassembly.gov/mem').text

    soup = BeautifulSoup(assembly_list_html)

    assembly_member_sections = soup.find_all('section', class_='mem-item')

    output = {}
    for assembly_member_section in assembly_member_sections:
        result = {}

        info = assembly_member_section.find('div', class_='mem-info')
        result['name'] = next(info.find('h3', class_='mem-name').find('a').strings).strip()
    
        email_container = info.find('div', class_='mem-email')
        result['email'] = email_container and email_container.find('a').string.strip()
    
        # address = assembly_member_section.find('div', class_='mem-address')
        addresses = assembly_member_section.find_all('div', class_='full-addr notranslate')

        district_match = re.compile('District (\d+)').search(str(assembly_member_section))
        result['district'] = district_match and district_match.group(1)

        result['district_contact'] = []
        result['albany_contact'] = []
        for address in addresses:
            lines = list(address.strings)
            addr = {}
            for line in lines:
                phone_re = re.compile('\d{3}-\d{3}-\d{4}')
                if re_result := phone_re.search(str(line)):
                    if 'Fax' in line:
                        addr['fax'] = re_result.group()
                    else:
                        addr['phone'] = re_result.group()
                elif match := re.compile('^\s*(\w+[\w\s]*), NY').search(line):
                    city = match.group(1)
                    addr['city'] = convert_city(city)
            if 'LOB' in lines[0]:
                result['albany_contact'].append(addr)
            else:
                result['district_contact'].append(addr)
        
        output[result['district']] = result
    return output

data = {'senate': get_senate_data(), 'assembly': get_assembly_data()}

# Now join them against the DB to line them up against the state member ID used by the API.
senators = Senator.query.all()
senator_data = {}
for senator in senators:
    matching_item = data['senate'][str(senator.district)]
    senator_data[senator.state_member_id] = {
        **matching_item,
        "name": senator.person.name,
        "district": senator.district,

        # This should be visually inspected every time the scraper is re-run,
        # before the data is accepted.
        "scrape_name__SANITY_CHECK": matching_item['name'],
    }

print("Senate\n")
pprint(senator_data)
print()


assembly_members = AssemblyMember.query.all()
assembly_data = {}
for member in assembly_members:
    matching_item = data['assembly'].get(str(member.district))
    if not matching_item:
        print(f"no matching item for {member.person.name}")
        continue

    assembly_data[member.state_member_id] = {
        **matching_item,
        "name": member.person.name,
        "district": member.district,
        "scrape_name__SANITY_CHECK": matching_item['name'],
    }

print("Assembly\n")
pprint(assembly_data)