from urllib.parse import quote

from .bill.models import Bill
from .person.models import Person


# URL for a Twitter Advanced Search for terms posted by a particular legislator.
def get_twitter_search_url(twitter_handle, search_terms):
    query_terms = " OR ".join([f'"{term}"' for term in search_terms])
    full_query = f"(from:{twitter_handle}) {query_terms}"
    return f"https://twitter.com/search?q={quote(full_query)}&f=live"


def get_bill_twitter_search_url(bill: Bill, person: Person):
    if not person.twitter:
        return None
    return get_twitter_search_url(person.twitter, bill.twitter_search_terms)
