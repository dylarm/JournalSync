from pathlib import Path
from datetime import datetime
from typing import List, Dict, Iterable, Tuple, Union
import requests
import os

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
        new_journal = dict()
        for n, file in enumerate(files):
            with file.open() as f:
                entry = f.readlines()
            jtime = zim_path_datetime(file)
            new_journal[jtime] = {"entries": [n], n: [line.rstrip() for line in entry]}
            tag_loc = self.__find_tags(new_journal[jtime][n])
            if tag_loc[0] == len(new_journal[jtime][n]):
                new_journal[jtime][n].append(self.tags["start"])
                new_journal[jtime][n].append(self.tags["end"])
        return new_journal

    def __create_page_header(self, date: datetime) -> List[str]:
        new_header = self.zim_header
        date_str = date.astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
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

    def __find_monica_entry(self, dtime: datetime, title: str) -> int:
        entry = self.journal[dtime]["entries"][0]
        entry_text = self.journal[dtime][entry]
        try:
            n = entry_text.index(title)
        except ValueError:
            n = -1
        return n

    def find_monica_entries(self, dtime: datetime, titles: List[str]) -> List[int]:
        entry_text = self.journal[dtime]["entries"][0]
        monica_entries = []
        for title in titles:
            try:
                monica_entries.append(entry_text.index(title))
            except ValueError:
                pass
        return monica_entries

    def update_page(self, dtime: datetime, entries: Dict[int, List[str]]):
        page_text = self.journal[dtime][self.journal[dtime]["entries"][0]]
        tags = self.__find_tags(page_text)
        for entry in entries:
            positions = self.find_monica_entries(dtime, entries[entry])
            pass
        return


class MonicaJournal:
    """Getting the journal from a Monica instance via the REST API"""

    def __init__(self, config, autoload=False):
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
            n = int(entry["id"])
            dtime = datetime.strptime(entry["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            ctime = datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            post = create_monica_post(
                text=entry["post"],
                title=f"{entry['title']}, {ctime}",  # add the time so every title is unique
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
