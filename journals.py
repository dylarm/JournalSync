from pathlib import Path
from datetime import datetime
import requests


class ZimJournal:
    """A plaintext-ish journal"""

    def __init__(self, config):
        self.zim = Path(config["zim_journal_path"])
        self.blank_header = list(config["header"])
        self.journal = self.__load_journal()

    def __load_journal(self):
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
                journal[entry]["text"] = r.readlines()
            journal[entry]["creation_date"] = datetime.fromisoformat(
                journal[entry]["text"][2][15:-1]
            )
        return journal

    def create_page(self, text):
        pass


class MonicaJournal:
    """Getting the journal from a Monica instance via the REST API"""

    def __init__(self, config, autoload=False):
        self.api = config["api_path"]
        self.api_key = config["oath_key"]
        if autoload:
            self.journal = self.load_journal()
        else:
            self.journal = None
            self.journal_url = None

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

    def load_journal(self):
        """Retrieve the journal from Monica and make it look nice"""
        self.journal_url = self.__get_journal_url()
        journal = requests.get(
            self.journal_url, headers={"Authorization": f"Bearer {self.api_key}"}
        ).json()
        new_journal = dict()
        for entry in journal["data"]:
            new_journal[entry["id"]] = {
                "date": datetime.strptime(entry["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                "title": entry["title"],
                "post": entry["post"],
                "created": datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
            }
        return new_journal