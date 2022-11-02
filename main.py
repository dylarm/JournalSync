# Sync the Monica journal with Zim

from pathlib import Path
import yaml
import requests
import json
from datetime import datetime
from typing import Dict, Iterable

CONFIG_PATH = Path("./secrets/config.yaml")


def read_config(config: Path = CONFIG_PATH) -> Dict[str, str]:
    with open(config, "r") as stream:
        try:
            config_out = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config_out


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
def test_api(url: str, key: str) -> bool:
    response = requests.get(url, headers={"Authorization": f"Bearer {key}"})
    r = "success" in response.json()
    return r


def get_journal_url(api_url: str, key: str) -> str:
    response = requests.get(api_url, headers={"Authorization": f"Bearer {key}"}).json()
    return response["links"]["journal_url"]


def get_journal(url: str, key: str) -> Dict[str, Iterable]:
    journal = requests.get(url, headers={"Authorization": f"Bearer {key}"}).json()
    return journal


def parse_journal(journal: Dict[str, Iterable]) -> Dict[int, Iterable]:
    new_journal = dict()
    for entry in journal["data"]:
        new_journal[entry["id"]] = {
            "date": datetime.strptime(entry["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            "title": entry["title"],
            "post": entry["post"],
            "created": datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
        }
    return new_journal


def date_to_path(date: datetime) -> Path:
    p = Path(str(date.year) + "/" + str(date.month).zfill(2))
    return p


def date_to_page(date: datetime) -> Path:
    return Path(str(date.day).zfill(2) + ".txt")


def journal_paths_exist(zim: Path, date: datetime) -> bool:
    journal_present = zim.exists()
    full_journal = zim.joinpath(date_to_path(date)).exists()
    return all([journal_present, full_journal])


def journal_page_exists(zim: Path, date: datetime) -> bool:
    return zim.joinpath(date_to_path(date)).joinpath(date_to_page(date)).exists()


def main():
    config = read_config()
    api_key = config["oath_key"]
    api_url = config["api_url"]
    zim_path = Path(config["zim_journal_path"])
    journal_url = get_journal_url(api_url=api_url, key=api_key)
    journal = get_journal(journal_url, api_key)
    new_journal = parse_journal(journal)
    for entry in new_journal:
        print(journal_paths_exist(zim=zim_path, date=new_journal[entry]["date"]))
        print(journal_page_exists(zim=zim_path, date=new_journal[entry]["date"]))


if __name__ == "__main__":
    main()
