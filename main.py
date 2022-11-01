# Sync the Monica journal with Zim

from pathlib import Path
import yaml
import requests
import json

CONFIG_PATH = Path("./secrets/config.yaml")


def read_config(config=CONFIG_PATH):
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
def test_api(url, key):
    response = requests.get(url, headers={"Authorization": f"Bearer {key}"})
    r = "success" in response.json()
    return r


def get_journal_url(api_url, key):
    response = requests.get(api_url, headers={"Authorization": f"Bearer {key}"}).json()
    return response["links"]["journal_url"]


def get_journal(url, key):
    journal = requests.get(url, headers={"Authorization": f"Bearer {key}"}).json()
    print(json.dumps(journal, indent=2))


def main():
    config = read_config()
    api_key = config["oath_key"]
    api_url = config["api_url"]
    journal_url = get_journal_url(api_url=api_url, key=api_key)
    get_journal(journal_url, api_key)


if __name__ == "__main__":
    main()
