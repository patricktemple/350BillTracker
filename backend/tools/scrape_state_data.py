from bs4 import BeautifulSoup
import requests

import re

from src.app import app
from src.person.models import Person, Senator, AssemblyMember
import json

def get_senate_data():
    senator_list_html = requests.get('https://www.nysenate.gov/senators-committees').text

    url_root = "https://www.nysenate.gov"

    list_soup = BeautifulSoup(senator_list_html)

    senator_urls = set()
    for link in list_soup.find_all('a'):
        href = link.get('href')
        if href is not None and href.startswith('/senators/'):
            party_text = str(link.find('span', class_='nys-senator--party').string)
            # print(party_text)
            if re.compile('[\( ]D[,\)]').search(party_text):
                # print(party_text)
                party = "D" # THIS IS WRONG, all people are D here?
            elif re.compile('[\( ]R[,\)]').search(party_text):
                party = "R"
            else:
                party = None

            senator_urls.add((url_root + href + "/contact", party))

    # print(senator_urls)

    def extract_contact_info(address_section):
        phone = address_section.find('span', string="Phone: ")
        fax = address_section.find('span', string="Fax: ")
        city = address_section.find('span', class_="locality")
        return {
            "phone": phone and phone.next_sibling,
            "fax": fax and fax.next_sibling,
            "city": re.compile('\w+[\s\w]*').search(city.string).group()
        }

    output = {}

    for contact_url, party in senator_urls:
        print(contact_url, party)
        contact_page = requests.get(contact_url).text
        contact_soup = BeautifulSoup(contact_page)
        district = contact_soup.find_all('a', href=lambda href: href and href.startswith('/district/'))[0]['href'][len('/district/'):]
        # print(district)
        address_tags = contact_soup.find_all('div', class_='location vcard')
        district_tags = [t for t in address_tags if 'district office' in str(t).lower()]
        albany_tags = [t for t in address_tags if 'albany office' in str(t).lower()]

        email = contact_soup.find('div', class_='c-block--senator-email').find('div', class_='field-content').find('a').string

        results = {
            "email": email,
            "district_contact": [],
            "albany_contact": [],
            "name": contact_soup.find('span', class_="c-senator-hero--name").find('a').string,
            "website": contact_url,
            "district": district,
            "party": party
        }
        for d in district_tags:
            results['district_contact'].append(extract_contact_info(d))
        
        for a in albany_tags:
            results['albany_contact'].append(extract_contact_info(a))
        
        output[results['district']] = results

    return output


def get_assembly_data():
    assembly_list_html = requests.get('https://www.nyassembly.gov/mem').text
    # print(assembly_list_html)

    soup = BeautifulSoup(assembly_list_html)

    items = soup.find_all('section', class_='mem-item')
    print(len(items))

    output = {}
    for item in items:
        # print(item)
        result = {}
        info = item.find('div', class_='mem-info')
        result['name'] = next(info.find('h3', class_='mem-name').find('a').strings).strip()
        email_container = info.find('div', class_='mem-email')
        result['email'] = email_container and email_container.find('a').string.strip()
        address = item.find('div', class_='mem-address')
        addresses = item.find_all('div', class_='full-addr notranslate')

        district_result = re.compile('District (\d+)').search(str(item))
        result['district'] = district_result and district_result.group(1)

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
                    print(city)
                    addr['city'] = city
            if 'LOB' in lines[0]:
                result['albany_contact'].append(addr)
            else:
                result['district_contact'].append(addr)
        
        output[result['district']] = result
    return output

# print(get_senate_data())

data = {'senate': get_senate_data(), 'assembly': get_assembly_data()}
# print(get_assembly_data())

# TWO STEPS

senators = Senator.query.all()
senator_data = {}
for senator in senators:
    matching_item = data['senate'][str(senator.district)]
    senator_data[senator.state_member_id] = {
        "name": senator.person.name,
        "district": senator.district,
        "scrape_name__SANITY_CHECK": matching_item['name'],
        "district_contact": matching_item['district_contact'],
        "albany_contact": matching_item['albany_contact']
    }

print("Senate")
print(senator_data)


assembly_members = AssemblyMember.query.all()
assembly_data = {}
for member in assembly_members:
    matching_item = data['assembly'].get(str(member.district))
    if not matching_item:
        print(f"no matching item for {member.person.name}")
        continue

    assembly_data[member.state_member_id] = {
        "name": member.person.name,
        "district": member.district,
        "scrape_name__SANITY_CHECK": matching_item['name'],
        "district_contact": matching_item['district_contact'],
        "albany_contact": matching_item['albany_contact']
    }

print("Assembly")
print(assembly_data)