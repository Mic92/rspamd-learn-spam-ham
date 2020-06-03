#!/usr/bin/env python3

import sys
import dbm.gnu
import pathlib
import requests
import os
from typing import Iterator, IO
from urllib.parse import urlparse


def list_msgs(maildir: str) -> Iterator[str]:
    for dirpath, _, file_list in os.walk(maildir):
        for fname in file_list:
            if ":" in fname:
                path = os.path.join(dirpath, fname)
                if os.path.isfile(path):
                    yield path


class RspamdClient:
    def __init__(self, url: str, password: str):
        self.session = requests.Session()
        self.url = urlparse(url)
        self.password = password

    def _post(self, msg_fd: IO[bytes], path: str) -> None:
        self.session.post(
            f"https://{self.url.netloc}/{path}",
            data=msg_fd,
            headers=dict(Password=self.password),
        )

    def learn_ham(self, msg_fd: IO[bytes]) -> None:
        self._post(msg_fd, "ham")

    def learn_spam(self, msg_fd: IO[bytes]) -> None:
        self._post(msg_fd, "spam")


def process_maildir(db: "dbm.gnu._gdbm", client: RspamdClient, maildir: str) -> None:
    for msg in list_msgs(maildir):
        filepath, flags = msg.split(":")
        msg_path = pathlib.Path(filepath)
        msg_id = msg_path.name
        if "S" not in flags or db.get(msg_id, False):
            continue
        locations = msg_path.parents
        if len(locations) < 2:
            continue
        folder = locations[1]

        try:
            msg_fd = open(msg, "rb")
        except OSError as e:
            print(f"cannot open {msg}: {e}")
            continue

        try:
            for i in range(0, 10):
                try:
                    if folder.name.lower() == "spam":
                        print(f"[spam] {msg}")
                        client.learn_spam(msg_fd)
                    else:
                        print(f"[ham] {msg}")
                        client.learn_ham(msg_fd)
                    break
                except requests.exceptions.ConnectionError as e:
                    print(f"failed to send {msg}: {e}")
                    if i == 9:
                        print("Give up")
        finally:
            msg_fd.close()
        db[msg_id] = "1"


def each_key(db: "dbm.gnu._gdbm") -> Iterator[bytes]:
    k = db.firstkey()
    while k is not None:
        yield k
        k = db.nextkey(k)


def main() -> None:
    if len(sys.argv) != 4:
        print(f"USAGE: {sys.argv[0]} maildir rspam_address password", file=sys.stderr)
        sys.exit(1)

    maildir = sys.argv[1]
    base_url = sys.argv[2]
    password = sys.argv[3]

    client = RspamdClient(base_url, password)

    with dbm.gnu.open("processed.db", "c") as db:
        for key in each_key(db):
            db[key] = "2"
        process_maildir(db, client, maildir)
        for key in each_key(db):
            if db[key] == b"2":
                del db[key]


if __name__ == "__main__":
    main()
