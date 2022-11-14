# Sync the Monica journal with Zim
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict

import yaml
from dotenv import load_dotenv

from journals import MonicaJournal

logger = logging.getLogger()
log_stream = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter(
    "%(asctime)s - %(threadName)s (%(module)s, %(funcName)s) - %(levelname)s - %(message)s"
)
log_stream.setFormatter(log_format)
logger.addHandler(log_stream)


def read_config(config: Path) -> Dict[str, str]:
    # TODO: Fix config typing
    # It's strictly not a Dict[str, str], but in here it doesn't matter. But in MonicaJournal, it gets complicated.
    with config.open() as stream:
        try:
            logger.debug("Loading config %s", config)
            config_out: Dict[str, str] = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.exception(exc)
            config_out = dict()
    secret_keys = [key for key in config_out if "MONICA_API" in str(config_out[key])]
    if secret_keys:
        logger.warning("Secret keys need to be loaded")
        logger.info("Loading secret keys from .env")
        load_dotenv()
        for key in secret_keys:
            try:
                logger.debug("Loading secret key %s", key)
                config_out[key] = os.environ[str(key).upper()]
            except KeyError as e:
                logger.exception("Key Error for %s: %s", key, e)
                raise KeyError(f"Could not find {key} in environment: {e}")
    return config_out


def main(config_file: Path) -> None:
    logger.debug("Using config file %s", config_file)
    config = read_config(config=config_file)
    m = MonicaJournal(config, autoload=True, cache=True)
    logger.debug("Loaded MonicaJournal %s", m)
    logger.info("Monica journal has %s dates:", len(m.journal))
    for d in m.journal:
        logger.info("%s: %s entries", d.date(), len(m.journal[d]["entries"]))
    print("Writing to Zim")
    m._write_to_zim()
    print("Finished writing")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog="JournalSync.py",
        description="Retrieve journal entries from Monica and write them in plaintext for Zim",
    )
    arg_parser.add_argument("-c", "--config", type=Path, default=Path("../config.yaml"))
    arg_parser.add_argument("-v", "--verbose", type=int, default=3)
    args = arg_parser.parse_args()
    if args.verbose == 1:
        logger.setLevel(logging.WARNING)
    elif args.verbose == 2:
        logger.setLevel(logging.INFO)
    elif args.verbose == 3:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    main(args.config)
