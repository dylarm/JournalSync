# Sync the Monica journal with Zim

from pathlib import Path
from pprint import pprint
import yaml
from datetime import datetime
from typing import Dict, Iterable, List

from journals import ZimJournal

CONFIG_PATH = Path("./secrets/config.yaml")


def read_config(config: Path = CONFIG_PATH) -> Dict[str, str]:
    with open(config, "r") as stream:
        try:
            config_out = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
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


def read_journal_page(zim: Path, date: datetime) -> Iterable:
    page = get_page_path(zim, date)
    with open(page, "r") as f:
        r_page = f.readlines()
        # r_page[5] is the first line of actual text
    return r_page


def create_journal_page(zim: Path, date: datetime, header: List[str]):
    new_header = create_journal_header(date, header)
    print(header)


def main():
    config = read_config()
    z = ZimJournal(config)
    pprint(z.journal)


if __name__ == "__main__":
    main()
