from src.app import app
from src.person.models import AssemblyMember
import logging
from pprint import pprint

# Get this CSV by taking the Wikipedia table, pasting it into a Google sheet, then export as CSV
file = open('/Users/patrick/Downloads/wiki-assembly.csv')
lines = file.readlines()

# Columns:
# 0: District
# 1: Name
# 2: Party (Rep or Dem)
# 3: Year first elected
# 4: Counties

output = {}
# make sure to sort at the end

PARTY_MAP = {
    "Rep": "R",
    "Dem": "D",
    "Ind": "I"
}

for line in lines:
    district, name, party, year, counties = line.split(',', 4) # maxsplit because commas may exist inside the county list
    
    existing_members = AssemblyMember.query.filter_by(district=district).all()
    if not existing_members:
        logging.warning(f"No existing member found matching {name}, district {district}")
        continue
    if len(existing_members) > 1:
        logging.warning(f"Multiple matches for {name}, district {district}: {', '.join([m.person.name for m in existing_members])}")
        continue

    member = existing_members[0]
    output[member.state_member_id] = {
        "name": member.person.name,
        "wiki_scraped_name__SANITY_CHECK": name,
        "district": district,
        "party": PARTY_MAP.get(party, None),
    }

pprint(output)