# Sync the Monica journal with Zim

from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

import yaml
import os
import argparse

from journals import MonicaJournal


def read_config(config: Path) -> Dict[str, str]:
    # TODO: Fix config typing
    # It's strictly not a Dict[str, str], but in here it doesn't matter. But in MonicaJournal, it gets complicated.
    with config.open() as stream:
        try:
            config_out: Dict[str, str] = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            config_out = dict()
    secret_keys = [key for key in config_out if "MONICA_API" in str(config_out[key])]
    if secret_keys:
        load_dotenv()
        for key in secret_keys:
            try:
                config_out[key] = os.environ[str(key).upper()]
            except KeyError as e:
                raise KeyError(f"Could not find {key} in environment: {e}")
    return config_out


def main(config_file: Path) -> None:
    config = read_config(config=config_file)
    m = MonicaJournal(config, autoload=True, cache=True)
    print(f"Monica journal has {len(m.journal)} dates:")
    for d in m.journal:
        print(f"\t{d.date()}: {len(m.journal[d]['entries'])} entries")
    print("Writing to Zim")
    m._write_to_zim()
    print("Finished writing")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog="JournalSync.py",
        description="Retrieve journal entries from Monica and write them in plaintext for Zim",
    )
    arg_parser.add_argument("-c", "--config", type=Path, default=Path("./config.yaml"))
    args = arg_parser.parse_args()
    main(args.config)
