#! /usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Generator
import os
import random
import requests

BASE_URL = "https://magireco.com/"

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.5",
           "Accept-Encoding": "gzip, deflate",
           "DNT": "1",
           "Connection": "keep-alive",
           "Upgrade-Insecure-Requests": "1",
           "Priority": "u=0, i"}

GREEN = "\033[0;32m"
RED = "\033[0;31m"
RESET = "\033[0m"

def main():
    scrape_all(magia_report_candidates)


def magia_report_candidates() -> Generator[str, None, None]:
    p3 = ".jpg"
    for i in ("images/comic/image/", "images/comic2/image/"):
        p1 = i
        for j in range(1000):
            p2 = str(j).zfill(2)
            yield f"{p1}{p2}{p3}"


# Scrape all paths given by a generator function
def scrape_all(candidates: callable) -> None:
    # I believe requests isn't thread safe when using cookies, but this should be fine
    with requests.Session() as session, ThreadPoolExecutor(max_workers=20) as executor:
        for asset in candidates():
            # Use loop to retry after each connection, so transient network errors don't stop the program
            while True:
                try:
                    # print(f"Queuing   {asset}")
                    executor.submit(scrape, session, asset)
                    break
                except Exception as e:
                    print(f"{RED}{e}{RESET}")


def scrape(session: requests.Session, asset: str) -> None:
    # asset is the portion after the domain, without the leading /
    # e.g. "images/comic2/image/339.jpg"
    response = session.get(f"{BASE_URL}{asset}", headers=HEADERS, timeout=random.randint(4,10))
    if response.status_code == 404:
        print(f"Not found {asset}")
        return
    elif response.status_code != 200:
        raise Exception(f"returned status code {response.status_code}")
    else:
        content = response.content
        print(f"{GREEN}Found     {asset}!{RESET}")
        os.makedirs(os.path.dirname(Path(asset)), exist_ok=True)
        with open(Path(asset), mode="wb") as file:
            file.write(content)


if __name__ == "__main__":
    main()
