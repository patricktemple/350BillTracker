"""
Contains data on legislators that is not provided by the API. Although st sync
most data that we can from the API, we expect these values to change rarely and
it's fine to have them be fixed.
"""

D = "Democratic"
R = "Republican"

# The API does provide "name", but we have it here too so allow overriding
# the rendering of the name, and also because it makes this dict much easier
# to read.
# TODO: Fill in the twitter data
STATIC_DATA_BY_LEGISLATOR_ID = {
    7739: {"name": "Adrienne E. Adams", "twitter": "AdrienneEAdams1", "party": D},
    7747: {"name": "Alicka Ampry-Samuel ", "twitter": "CMAlickaASamuel", "party": D},
    7742: {"name": "Diana Ayala ", "twitter": "DianaAyalaNYC", "party": D},
    7623: {"name": "Inez D. Barron", "twitter": "CMInezDBarron", "party": D},
    7264: {"name": "Joseph C. Borelli", "twitter": "JoeBorelliNYC", "party": R},
    7748: {"name": "Justin L. Brannan", "twitter": "JustinBrannan", "party": D},
    7561: {"name": "Fernando Cabrera ", "twitter": "FCabreraNY", "party": D},
    7562: {"name": "Margaret S. Chin", "twitter": "CM_MargaretChin", "party": D},
    7604: {"name": "Robert E. Cornegy, Jr.", "twitter": None, "party": D},
    7628: {"name": "Laurie A. Cumbo", "twitter": None, "party": D},
    7744: {"name": "Ruben Diaz, Sr.", "twitter": None, "party": D},
    7563: {"name": "Daniel Dromm ", "twitter": None, "party": D},
    7113: {"name": "Mathieu Eugene", "twitter": None, "party": D},
    7622: {"name": "Vanessa L. Gibson", "twitter": None, "party": D},
    7743: {"name": "Mark Gjonaj ", "twitter": None, "party": D},
    7691: {"name": "Barry S. Grodenchik", "twitter": None, "party": D},
    7746: {"name": "Robert F. Holden", "twitter": None, "party": D},
    7631: {
        "name": "Corey D. Johnson",
        "twitter": "NYCSpeakerCoJo",
        "party": D,
    },
    7632: {"name": "Ben Kallos", "twitter": None, "party": D},
    7565: {"name": "Peter A. Koo", "twitter": None, "party": D},
    386: {"name": "Karen Koslowitz", "twitter": None, "party": D},
    7566: {"name": "Brad S. Lander", "twitter": None, "party": D},
    7567: {"name": "Stephen T. Levin", "twitter": None, "party": D},
    7634: {"name": "Mark Levine", "twitter": None, "party": D},
    7635: {"name": "Alan N. Maisel", "twitter": None, "party": D},
    5953: {"name": "Steven Matteo", "twitter": None, "party": R},
    7636: {"name": "Carlos Menchaca", "twitter": None, "party": D},
    7637: {"name": "I. Daneek Miller", "twitter": None, "party": D},
    7745: {"name": "Francisco P. Moya", "twitter": None, "party": D},
    430: {"name": "Bill Perkins", "twitter": None, "party": D},
    7741: {"name": "Keith Powers ", "twitter": None, "party": D},
    7638: {"name": "Antonio Reynoso", "twitter": None, "party": D},
    7740: {"name": "Carlina Rivera ", "twitter": None, "party": D},
    7541: {"name": "Ydanis A. Rodriguez", "twitter": None, "party": D},
    7568: {"name": "Deborah L. Rose", "twitter": None, "party": D},
    7639: {"name": "Helen K. Rosenthal", "twitter": None, "party": D},
    7714: {"name": "Rafael Salamanca, Jr.", "twitter": None, "party": D},
    7641: {"name": "Mark Treyger", "twitter": None, "party": D},
    7510: {"name": "Eric A. Ulrich", "twitter": None, "party": R},
    7642: {"name": "Paul A. Vallone", "twitter": None, "party": D},
    7569: {"name": "James G. Van Bramer", "twitter": None, "party": D},
    7749: {"name": "Kalman Yeger ", "twitter": None, "party": D},
    7780: {
        "name": "Public Advocate Jumaane Williams",
        "twitter": None,
        "party": D,
    },
    7785: {"name": "Farah N. Louis", "twitter": None, "party": D},
    7793: {"name": "Darma V. Diaz", "twitter": None, "party": D},
    7794: {"name": "Kevin C. Riley", "twitter": None, "party": D},
    5273: {"name": "James F. Gennaro", "twitter": None, "party": D},
    7796: {"name": "Selvena N. Brooks-Powers", "twitter": None, "party": D},
    7799: {"name": "Eric Dinowitz", "twitter": None, "party": D},
    7798: {"name": "Oswald Feliz", "twitter": None, "party": D},
}
