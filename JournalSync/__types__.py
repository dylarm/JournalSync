from datetime import datetime
from typing import Dict, List, Any

# TODO: fix typing
# The API returns such a convoluted type of str, int, Dict, List, and None. Example:
# {'data': [{'account': {'id': 1},
#            'created_at': '2022-10-31T21:10:32Z',
#            'date': '2022-10-31T00:00:00.000000Z',
#            'id': 1,
#            'object': 'entry',
#            'post': 'This is a test entry during the day, to see how it looks '
#                    'and what somehow syncing it with Zim would look like.',
#            'title': None,
#            'updated_at': '2022-11-01T01:37:45Z',
#            'url': 'https://MONICA_URL/api/journal/1',
#            'uuid': 'c82aa72b-994e-4907-8da9-483c72e0519c'}],
#  'links': {'first': 'https://MONICA_URL/api/journal?page=1',
#            'last': 'https://MONICA_URL/api/journal?page=1',
#            'next': None,
#            'prev': None},
#   'meta': {'current_page': 1,
#            'from': 1,
#            'last_page': 1,
#            'links': [{'active': False, 'label': '❮ Previous', 'url': None},
#                      {'active': True,
#                       'label': '1',
#                       'url': 'https://MONICA_URL/api/journal?page=1'},
#                      {'active': False, 'label': 'Next ❯', 'url': None}],
#            'path': 'https://MONICA_URL/api/journal',
#            'per_page': 15,
#            'to': 5,
#            'total': 5}}
#
# format of Journal dict:
# {datetime1: {"-1": [int as str],
#              "0": [text],
#              "1": [text], etc.},
#  datetime2: {"-1": [int as str],
#              "2": [text],
#              "3": [text], etc.}}
Journal = Dict[datetime, Dict[str, List[str]]]
APIResponse = Dict[str, Dict[str, str]]
JournalResponse = Dict[
    str, List[Dict[str, str]]
]  # ignoring the types that I don't need
Config = Dict[str, Any]
