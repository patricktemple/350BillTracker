"""
Contains data on legislators that is not provided by the API. Although st sync
most data that we can from the API, we expect these values to change rarely and
it's fine to have them be fixed.
"""

# The API does provide "name", but we have it here too so allow overriding
# the rendering of the name, and also because it makes this dict much easier
# to read.
# TODO: Fill in the party and twitter data
STATIC_DATA_BY_LEGISLATOR_ID = {
    7739: {"name": "Adrienne E. Adams", "twitter": None, "party": None},
    7747: {"name": "Alicka Ampry-Samuel ", "twitter": None, "party": None},
    7742: {"name": "Diana Ayala ", "twitter": None, "party": None},
    7623: {"name": "Inez D. Barron", "twitter": None, "party": None},
    7264: {"name": "Joseph C. Borelli", "twitter": None, "party": None},
    7748: {"name": "Justin L. Brannan", "twitter": None, "party": None},
    7561: {"name": "Fernando Cabrera ", "twitter": None, "party": None},
    7562: {"name": "Margaret S. Chin", "twitter": None, "party": None},
    7604: {"name": "Robert E. Cornegy, Jr.", "twitter": None, "party": None},
    7628: {"name": "Laurie A. Cumbo", "twitter": None, "party": None},
    7744: {"name": "Ruben Diaz, Sr.", "twitter": None, "party": None},
    7563: {"name": "Daniel Dromm ", "twitter": None, "party": None},
    7113: {"name": "Mathieu Eugene", "twitter": None, "party": None},
    7622: {"name": "Vanessa L. Gibson", "twitter": None, "party": None},
    7743: {"name": "Mark Gjonaj ", "twitter": None, "party": None},
    7691: {"name": "Barry S. Grodenchik", "twitter": None, "party": None},
    7746: {"name": "Robert F. Holden", "twitter": None, "party": None},
    7631: {
        "name": "Corey D. Johnson",
        "twitter": "NYCSpeakerCoJo",
        "party": "Democratic",
    },
    7632: {"name": "Ben Kallos", "twitter": None, "party": None},
    7565: {"name": "Peter A. Koo", "twitter": None, "party": None},
    386: {"name": "Karen Koslowitz", "twitter": None, "party": None},
    7566: {"name": "Brad S. Lander", "twitter": None, "party": None},
    7567: {"name": "Stephen T. Levin", "twitter": None, "party": None},
    7634: {"name": "Mark Levine", "twitter": None, "party": None},
    7635: {"name": "Alan N. Maisel", "twitter": None, "party": None},
    5953: {"name": "Steven Matteo", "twitter": None, "party": None},
    7636: {"name": "Carlos Menchaca", "twitter": None, "party": None},
    7637: {"name": "I. Daneek Miller", "twitter": None, "party": None},
    7745: {"name": "Francisco P. Moya", "twitter": None, "party": None},
    430: {"name": "Bill Perkins", "twitter": None, "party": None},
    7741: {"name": "Keith Powers ", "twitter": None, "party": None},
    7638: {"name": "Antonio Reynoso", "twitter": None, "party": None},
    7740: {"name": "Carlina Rivera ", "twitter": None, "party": None},
    7541: {"name": "Ydanis A. Rodriguez", "twitter": None, "party": None},
    7568: {"name": "Deborah L. Rose", "twitter": None, "party": None},
    7639: {"name": "Helen K. Rosenthal", "twitter": None, "party": None},
    7714: {"name": "Rafael Salamanca, Jr.", "twitter": None, "party": None},
    7641: {"name": "Mark Treyger", "twitter": None, "party": None},
    7510: {"name": "Eric A. Ulrich", "twitter": None, "party": None},
    7642: {"name": "Paul A. Vallone", "twitter": None, "party": None},
    7569: {"name": "James G. Van Bramer", "twitter": None, "party": None},
    7749: {"name": "Kalman Yeger ", "twitter": None, "party": None},
    7780: {
        "name": "Public Advocate Jumaane Williams",
        "twitter": None,
        "party": None,
    },
    7785: {"name": "Farah N. Louis", "twitter": None, "party": None},
    7793: {"name": "Darma V. Diaz", "twitter": None, "party": None},
    7794: {"name": "Kevin C. Riley", "twitter": None, "party": None},
    5273: {"name": "James F. Gennaro", "twitter": None, "party": None},
    7796: {"name": "Selvena N. Brooks-Powers", "twitter": None, "party": None},
    7799: {"name": "Eric Dinowitz", "twitter": None, "party": None},
    7798: {"name": "Oswald Feliz", "twitter": None, "party": None},
}
