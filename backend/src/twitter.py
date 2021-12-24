from urllib.parse import quote


# URL for a Twitter Advanced Search for terms posted by a particular legislator.
def get_twitter_search_url(twitter_handle, search_terms):
    query_terms = " OR ".join([f'"{term}"' for term in search_terms])
    full_query = f"(from:{twitter_handle}) {query_terms}"
    return f"https://twitter.com/search?q={quote(full_query)}&f=live"


def get_bill_twitter_search_url(bill, legislator):
    if not legislator.twitter:
        return None
    return get_twitter_search_url(
        legislator.twitter, bill.twitter_search_terms
    )
