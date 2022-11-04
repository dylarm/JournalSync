from pathlib import Path
from datetime import datetime
from typing import List, Dict, Iterable, Tuple, Union
import requests

Journal = Dict[
    int, Dict[str, Union[datetime, Path, Tuple[int, int], List[str], List[int]]]
]


class ZimJournal:
    """A plaintext-ish journal"""

    def __init__(self, config):
        self.zim: Path = Path(config["zim_journal_path"])
        self.blank_header: List[str] = list(config["header"])
        self.title: Dict[int, str] = dict(config["title"])
        self.tags: Dict[str, str] = dict(config["monica_tag"])
        self.journal: Journal = self.__load_journal()

    def __load_journal(self) -> Journal:
        journal = {
            n: {"path": path}
            for n, path in enumerate(x for x in self.zim.glob("**/*.txt"))
        }
        for entry in journal:
            file_date_parts = journal[entry]["path"].parts[-3:]
            # tuple (year, month, day.txt)
            journal[entry]["file_date"] = datetime(
                year=int(file_date_parts[0]),
                month=int(file_date_parts[1]),
                day=int(file_date_parts[2][0:2]),
            )
            with journal[entry]["path"].open() as r:
                journal[entry]["text"] = [s.rstrip() for s in r.readlines()]
            journal[entry]["creation_date"] = datetime.fromisoformat(
                journal[entry]["text"][2][15:]
            )
            journal[entry]["tag"] = self.__find_tags(journal[entry]["text"])
            journal[entry]["entries"] = list()
        return journal

    def __create_header(self, date: datetime) -> List[str]:
        date_str = date.astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
        new_header = self.blank_header
        new_header[2] = (
            new_header[2] + f"{date_str[:-2]}:{date_str[-2:]}"
        )  # Because Zim is different
        new_header.append(
            f"{self.title[1]} {date.strftime('%A %d %b %Y')} {self.title[1]}"
        )
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
        entries = [self.journal[entry]["text"].index(title) for title in titles]
        return entries

    def insert_text(self, entry: int, new_text: List[str]) -> None:
        tag, text = self.journal[entry]["tag"], self.journal[entry]["text"]
        if tag[0] == len(text):
            text.extend(["", self.tags["start"], self.tags["end"]])
            self.journal[entry]["tag"] = self.__find_tags(self.journal[entry]["text"])
            tag = self.journal[entry]["tag"]
        self.journal[entry]["text"] = text[: tag[1]] + new_text + text[tag[1] :]
        return

    def create_page(self, date: datetime, text: List[str]):
        pass


class MonicaJournal:
    """Getting the journal from a Monica instance via the REST API"""

    def __init__(self, config, autoload=False):
        self.api = config["api_url"]
        self.api_key = config["oath_key"]
        self.journal_url: str = ""
        self.journal: Dict[int, Iterable] = dict()
        if autoload:
            self.journal = self.load_journal()

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

    def load_journal(self) -> Dict[int, Iterable]:
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
        return new_journal
