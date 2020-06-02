#!/usr/bin/env python3

import sys
import dbm
import pathlib
import requests
import os
from typing import Iterator
from urllib.parse import urlparse


def list_msgs(maildir: str) -> Iterator[str]:
    for dirpath, _, file_list in os.walk(maildir):
        for fname in file_list:
            if ":" in fname:
                path = os.path.join(dirpath, fname)
                if os.path.isfile(path):
                    yield path


def main() -> None:
    if len(sys.argv) != 4:
        print(f"USAGE: {sys.argv[0]} maildir rspam_address password", file=sys.stderr)
        sys.exit(1)

    maildir = sys.argv[1]
    base_url = sys.argv[2]
    password = sys.argv[3]

    url = urlparse(base_url)
    session = requests.Session()

    with dbm.open("processed.db", "c") as db:
        for msg in list_msgs(maildir):
            filepath, flags = msg.split(":")
            msg_path = pathlib.Path(filepath)
            msg_id = msg_path.name
            if "S" not in flags or db.get(msg_id, None):
                continue
            locations = msg_path.parents
            if len(locations) < 2:
                continue
            folder = locations[1]
            if folder.name.lower() == "spam":
                path = "learnspam"
            else:
                path = "learnham"

            try:
                msg_fd = open(msg, "rb")
            except OSError as e:
                print(f"cannot open {msg}: {e}")
                continue

            try:
                print(f"[{path}] {msg}")
                for i in range(0, 10):
                    try:
                        session.post(f"https://{url.netloc}/{path}",
                                     data=msg_fd,
                                     headers=dict(Password=password))
                        break
                    except requests.exceptions.ConnectionError as e:
                        print(f"failed to send {msg}: {e}")
                        if i == 9:
                            print("Give up")
            finally:
                msg_fd.close()
            db[msg_id] = "1"


if __name__ == "__main__":
    main()
