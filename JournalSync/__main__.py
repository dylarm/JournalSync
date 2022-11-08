# Sync the Monica journal with Zim

from pathlib import Path
from typing import Dict

import yaml

from journals import MonicaJournal

CONFIG_PATH = Path("./config.yaml")
SECRET_CONFIG_PATH = Path("../secrets/config.yaml")


def read_config(config: Path = CONFIG_PATH) -> Dict[str, str]:
    with CONFIG_PATH.open() as stream:
        try:
            config_out = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            config_out = dict()
    secret_keys = [key for key in config_out if "MONICA_API" in str(config_out[key])]
    if secret_keys:
        with SECRET_CONFIG_PATH.open() as stream:
            try:
                config_secret = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print("Could not load secret keys\n", exc)
        for key in secret_keys:
            config_out[key] = config_secret[key]
    return config_out


def main():
    config = read_config()
    m = MonicaJournal(config, autoload=True)
    print(f"Monica journal has {len(m.journal)} dates:")
    for d in m.journal:
        print(f"\t{d.date()}: {len(m.journal[d]['entries'])} entries")
    print("Writing to Zim")
    m._write_to_zim()
    print("Finished writing")


if __name__ == "__main__":
    main()
