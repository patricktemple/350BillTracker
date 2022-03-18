from .assembly_data_from_website import ASSEMBLY_DATA_FROM_WEBSITE
from .assembly_data_from_wiki import ASSEMBLY_DATA_FROM_WIKI

ASSEMBLY_DATA_BY_MEMBER_ID = {
    key: {
        **ASSEMBLY_DATA_FROM_WEBSITE[key],
        **ASSEMBLY_DATA_FROM_WIKI.get(key, {}),
    }
    for key in ASSEMBLY_DATA_FROM_WEBSITE.keys()
}
