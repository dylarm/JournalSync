# Sync the Monica journal with Zim

from pathlib import Path
from pprint import pprint
import yaml
from datetime import datetime
from typing import Dict

from journals import ZimJournal, MonicaJournal

CONFIG_PATH = Path("./config.yaml")
SECRET_CONFIG_PATH = Path("./secrets/config.yaml")


def read_config(config: Path = CONFIG_PATH) -> Dict[str, str]:
    with CONFIG_PATH.open() as stream:
        try:
            config_out = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            config_out = dict()
    secret_keys = [key for key in config_out if "MONICA_API" in config_out[key]]
    if secret_keys:
        with SECRET_CONFIG_PATH.open() as stream:
            try:
                config_secret = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print("Could not load secret keys\n", exc)
        for key in secret_keys:
            config_out[key] = config_secret[key]
    return config_out


def date_to_path(date: datetime) -> Path:
    p = Path(str(date.year) + "/" + str(date.month).zfill(2))
    return p


def date_to_page(date: datetime) -> Path:
    return Path(str(date.day).zfill(2) + ".txt")


def journal_paths_exist(zim: Path, date: datetime) -> bool:
    journal_present = zim.exists()
    full_journal = zim.joinpath(date_to_path(date)).exists()
    return all([journal_present, full_journal])


def get_page_path(zim: Path, date: datetime) -> Path:
    return zim.joinpath(date_to_path(date)).joinpath(date_to_page(date))


def journal_page_exists(zim: Path, date: datetime) -> bool:
    return get_page_path(zim, date).exists()


def main():
    config = read_config()
    z = ZimJournal(config)
    pprint(z.journal)
    m = MonicaJournal(config, autoload=True)
    pprint(m.journal)


if __name__ == "__main__":
    main()
