import time

import requests


def get_feature_flag(name: str) -> str:
    response = requests.get("http://localhost:8000/flag/" + name)
    if response.status_code == 404:
        return None
    return response.json()['flag_value']


if __name__ == '__main__':
    while True:
        what_is_it = get_feature_flag("THANKSGIVING_DINNER")
        print("What's cooking? " + (what_is_it or "Nothing yet"))
        time.sleep(3)
