from src.app import app
from src.person.models import AssemblyMember, Senator
import logging
from pprint import pprint

import click

PARTY_MAP = {
    "Rep": "R",
    "Republican": "R",
    "Dem": "D",
    "Democratic": "D",
    "Ind": "I",
}


@click.group()
def scrape_state_wiki():
    pass

@scrape_state_wiki.command()
@click.option('--input-csv', help="CSV file of the table data from Wikipedia")
def assembly(input_csv):
    # Columns:
    # 0: District
    # 1: Name
    # 2: Party (Rep or Dem or Ind)
    # 3: Year first elected
    # 4: Counties
    file = open(input_csv)
    lines = file.readlines()

    output = {}
    for line in lines:
        district, name, party, year, counties = line.strip().split(',', 4) # maxsplit because commas may exist inside the county list
        
        existing_members = AssemblyMember.query.filter_by(district=district).all()
        if not existing_members:
            logging.warning(f"No existing member found matching {name}, district {district}")
            continue
        if len(existing_members) > 1:
            logging.warning(f"Multiple matches for {name}, district {district}: {', '.join([m.person.name for m in existing_members])}")
            continue

        member = existing_members[0]

        if counties[0] == '"':
            counties = counties[1:-1]
        output[member.state_member_id] = {
            "name": member.person.name,
            "wiki_scraped_name__SANITY_CHECK": name,
            "district": district,
            "party": PARTY_MAP.get(party, None),
            "counties": counties.split(", ")
    }

    print("Assembly")
    pprint(output)


@scrape_state_wiki.command()
@click.option('--input-csv', help="CSV file of the table data from Wikipedia")
def senate(input_csv):
    # Columns:
    # 0: District
    # 1: Name
    # 2: Party (Republican or Democratic)
    # 3: Year first elected
    # 4: Counties
    file = open(input_csv)
    lines = file.readlines()

    output = {}
    for line in lines:
        district, name, party, year, counties = line.strip().split(',', 4)
        
        existing_members = Senator.query.filter_by(district=district).all()
        if not existing_members:
            logging.warning(f"No existing member found matching {name}, district {district}")
            continue
        if len(existing_members) > 1:
            logging.warning(f"Multiple matches for {name}, district {district}: {', '.join([m.person.name for m in existing_members])}")
            continue

        member = existing_members[0]

        if counties[0] == '"':
            counties = counties[1:-1]
        output[member.state_member_id] = {
            "name": member.person.name,
            "wiki_scraped_name__SANITY_CHECK": name,
            "district": district,
            "party": PARTY_MAP.get(party, None),
            "counties": counties.split(", ")
    }

    print("Senate")
    pprint(output)


if __name__ == '__main__':
    # Get the CSV by taking the Wikipedia table, pasting it into a Google sheet, then export as CSV
    scrape_state_wiki()