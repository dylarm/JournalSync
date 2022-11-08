import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union, Any
from urllib.request import Request, urlopen

import json

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


class MonicaJournal:
    """Getting the journal from a Monica instance via the REST API"""

    def __init__(self, config: Config, autoload: bool = False) -> None:
        self.api: str = config["api_url"]
        self.api_key: str = config["oath_key"]
        self.monica_title_index: int = int(config["monica_title"])
        self.titles: Dict[int, str] = dict(config["titles"])
        self.entry_sep: str = str(config["entry_sep"])
        self.zim: Path = Path(config["zim_journal_path"])
        self.zim_header: List[str] = list(config["zim_header"])
        self.journal_url: str = ""
        self.journal: Journal = dict()
        if autoload:
            self.load_journal()

    def __access_api(self, url: str) -> APIResponse:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        request = Request(method="GET", headers=headers, url=url)
        with urlopen(request) as req:
            response: APIResponse = json.loads(req.read().decode("utf-8"))
        return response

    def __access_api_endpoint(self, url: str) -> JournalResponse:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        request = Request(method="GET", headers=headers, url=url)
        with urlopen(request) as req:
            response: JournalResponse = json.loads(req.read().decode("utf-8"))
        return response

    def __test_api(self) -> bool:
        response = self.__access_api(self.api)
        # Example json response:
        # {'success': {'message': 'Welcome to Monica'},
        #   'links': {'activities_url': 'https://MONICA_API_URL/activities',
        #             'addresses_url': 'https://MONICA_API_URL/addresses',
        #             'calls_url': 'https://MONICA_API_URL/calls',
        #             'contacts_url': 'https://MONICA_API_URL/contacts',
        #             'conversations_url': 'https://MONICA_API_URL/conversations',
        #             'countries_url': 'https://MONICA_API_URL/countries',
        #             'currencies_url': 'https://MONICA_API_URL/currencies',
        #             'documents_url': 'https://MONICA_API_URL/documents',
        #             'journal_url': 'https://MONICA_API_URL/journal',
        #             'notes_url': 'https://MONICA_API_URL/notes',
        #             'relationships_url': 'https://MONICA_API_URL/contacts/:contactId/relationships',
        #             'reminders_url': 'https://MONICA_API_URL/reminders',
        #             'statistics_url': 'https://MONICA_API_URL/statistics'}}
        r = "success" in response
        return r

    def __get_journal_url(self) -> str:
        response: APIResponse = self.__access_api(self.api)
        return response["links"]["journal_url"]

    def __load_journal(self) -> Journal:
        """Retrieve the journal from Monica and make it look nice"""
        self.journal_url = self.__get_journal_url()
        journal: JournalResponse = self.__access_api_endpoint(self.journal_url)
        new_journal: Journal = dict()
        for entry in journal["data"]:
            n = str(entry["id"])
            dtime = datetime.strptime(entry["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            ctime = datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            post = create_monica_post(
                text=entry["post"],
                title=f"{entry['title']}, {ctime}",
                title_fmt=self.titles[self.monica_title_index],
                sep=self.entry_sep,
            )
            if dtime in new_journal:
                new_journal[dtime]["entries"].append(n)
                new_journal[dtime][n] = post
            else:
                new_journal[dtime] = {"entries": [n], n: post}
        return new_journal

    def load_journal(self) -> None:
        self.journal = self.__load_journal()
        return

    def get_titles_for_date(self, dtime: datetime) -> List[str]:
        titles = []
        journal = self.journal[dtime]
        for n in journal["entries"]:
            titles.append(journal[n][0])
        return titles

    def get_all_titles(self) -> Dict[datetime, List[str]]:
        return {dtime: self.get_titles_for_date(dtime) for dtime in self.journal}

    def _make_zim_page(self, dtime: datetime) -> List[str]:
        entries = self.journal[dtime]["entries"]
        text = self.zim_header.copy()
        date_str = dtime.astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
        text[2] = text[2] + f"{date_str[:-2]}:{date_str[-2:]}"
        text.append(
            f"{self.titles[1]} {dtime.strftime('%A %d %b %Y')} {self.titles[1]}"
        )
        text.append("")
        for entry in entries:
            text.extend(self.journal[dtime][entry])
        return text

    def _write_to_zim(self) -> None:
        """Just brute-force writing Monica entries to Zim, overwriting if necessary

        This is so that I can have something that works *now*, and then can make it better later
        """
        for dtime in self.journal:
            file = datetime_zim_path(dtime, root=self.zim)
            text = self._make_zim_page(dtime)
            file.write_text(os.linesep.join(text))


def zim_path_datetime(path: Path) -> datetime:
    parts = (*path.parts[-3:-1], path.stem)
    # tuple(year, month, day.txt)
    dtime = datetime(year=int(parts[0]), month=int(parts[1]), day=int(parts[2]))
    return dtime


def datetime_zim_path(dtime: datetime, root: Path) -> Path:
    full_path = root.joinpath(
        Path(f"{dtime.year}/{str(dtime.month).zfill(2)}/{str(dtime.day).zfill(2)}.txt")
    )
    return full_path


def create_monica_post_title(title: str, title_fmt: str) -> str:
    return f"{title_fmt} {title} {title_fmt}"


def create_monica_post(
    text: str, title: str, title_fmt: str, sep: Union[str, None] = None
) -> List[str]:
    """Create the text for a Monica entry in a Zim page"""
    if sep is None:
        entry = [create_monica_post_title(title, title_fmt)]
    else:
        entry = [sep, create_monica_post_title(title, title_fmt)]
    for line in text.splitlines():
        entry.append(line)
    entry.append("")
    return entry
