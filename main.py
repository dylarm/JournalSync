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


def test_api(url, key):
    response = requests.get(url, headers={"Authorization": f"Bearer {key}"})
    r = "success" in response.json()
    return r


def main():
    config = read_config()
    r = test_api(url=config["api_url"], key=config["oath_key"])
    print(r)


if __name__ == "__main__":
    main()
