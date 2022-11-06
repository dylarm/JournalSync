from pathlib import Path
from datetime import datetime
from typing import List, Dict, Iterable, Tuple, Union
import requests

# format of Journal dict:
# {datetime1: {entries: [int],
#              0: [text],
#              1: [text], etc.},
#  datetime2: {entries: [int],
#              2: [text],
#              3: [text], etc.}}
Journal = Dict[datetime, Dict[Union[int, str], List[Union[int, str]]]]


class ZimJournal:
    """A plaintext-ish journal"""

    def __init__(self, config):
        self.zim: Path = Path(config["zim_journal_path"])
        self.zim_header: List[str] = list(config["zim_header"])
        self.title: Dict[int, str] = dict(config["titles"])
        self.tags: Dict[str, str] = dict(config["monica_tag"])
        self.journal: Journal = self.__load_journal()

    def __load_journal(self) -> Journal:
        files = self.zim.glob("**/*.txt")
        raw_journal = []
        new_journal = dict()
        for n, file in enumerate(files):
            with file.open() as f:
                entry = f.readlines()
            jtime = zim_path_datetime(file)
            new_journal[jtime] = {"entries": [n], n: [line.rstrip() for line in entry]}
        return new_journal

    def __create_header(self, date: datetime) -> List[str]:
        new_header = []
        return new_header

    def __find_tags(self, text: List[str]) -> Tuple[int, int]:
        """Returns index of start tag, and negative index to insert before end tag"""
        try:
            start = text.index(self.tags["start"])
            end = text.index(self.tags["end"])
        except ValueError:
            start, end = len(text), len(text) - 1
        return start, end - len(text)

    def __find_monica_entries(self, entry: int, titles: List[str]) -> List[int]:
        entries = []
        return entries

    def insert_text(self, entry: int, new_text: List[str]) -> None:
        return

    def create_page(self, date: datetime, text: List[str]):
        pass


class MonicaJournal:
    """Getting the journal from a Monica instance via the REST API"""

    def __init__(self, config, autoload=False):
        self.api = config["api_url"]
        self.api_key = config["oath_key"]
        self.journal_url: str = ""
        self.journal: Journal = dict()
        if autoload:
            self.load_journal()

    def __test_api(self) -> bool:
        response = requests.get(
            self.api, headers={"Authorization": f"Bearer {self.api_key}"}
        )
        # Example json response:
        # /home/dylan/Public/JournalSync/venv/bin/python /home/dylan/Public/JournalSync/main.py
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
        r = "success" in response.json()
        return r

    def __get_journal_url(self) -> str:
        response = requests.get(
            self.api, headers={"Authorization": f"Bearer {self.api_key}"}
        ).json()
        return response["links"]["journal_url"]

    def __load_journal(self) -> Journal:
        """Retrieve the journal from Monica and make it look nice"""
        self.journal_url = self.__get_journal_url()
        journal = requests.get(
            self.journal_url, headers={"Authorization": f"Bearer {self.api_key}"}
        ).json()
        new_journal = dict()
        for entry in journal["data"]:
            new_journal[int(entry["id"])] = {
                "date": datetime.strptime(entry["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                "title": entry["title"],
                "post": entry["post"].splitlines(),
                "created": datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
            }
        new_journal[-1] = collate_entry_dates(new_journal)
        return new_journal

    def load_journal(self) -> None:
        self.journal = self.__load_journal()
        return


def zim_path_datetime(path: Path) -> datetime:
    parts = (*path.parts[-3:-1], path.stem)
    # tuple(year, month, day.txt)
    dtime = datetime(year=int(parts[0]), month=int(parts[1]), day=int(parts[2]))
    return dtime
