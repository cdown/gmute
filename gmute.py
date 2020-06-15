#!/usr/bin/env python

"""
Given a plain mail (for example, from mutt's pipe-message), mute that thread in
Gmail.

This solution is Gmail-specific, as the concept of "muting" and the X-GM-*
attributes are not standardised or widely available.
"""

import os
import email.parser
import imaplib
import sys
import configparser

CONFIG_FILE = os.path.expanduser("~/.config/gmute")

cur = imaplib.IMAP4_SSL("imap.gmail.com")


def get_message_id_from_stdin():
    hp = email.parser.HeaderParser()
    headers = hp.parse(sys.stdin, headersonly=True)
    return headers["Message-ID"]


def icheck(ret):
    status, (data,) = ret

    if status != "OK":
        raise ValueError("Bad status '{}': {}".format(status, data))

    return data.decode("ascii")


def mark(user, password):
    mid = get_message_id_from_stdin()
    print("Parsed message ID {}".format(mid))

    print("Logging in...")
    icheck(cur.login(user, password))
    icheck(cur.select('"[Gmail]/All Mail"'))

    initial_uid = icheck(cur.search(None, "(HEADER Message-ID %s)" % mid))

    if not initial_uid:
        print("No such message: {}".format(mid), file=sys.stderr)
        return 1

    data = icheck(cur.fetch(str(initial_uid), "(X-GM-THRID)"))
    thread_id = data.split()[-1][:-1]

    data = icheck(cur.search(None, "(X-GM-THRID {})".format(thread_id)))
    all_uids = data.split()

    print("Found {} mails to tag. Tagging...".format(len(all_uids)))

    for uid in all_uids:
        icheck(cur.store(uid, "+X-GM-LABELS", r"(\Muted)"))

    print("Tagging complete.")

    return 0


def main():
    if sys.stdin.isatty():
        print("Mail file should be provided on stdin", file=sys.stderr)
        return 1

    cp = configparser.ConfigParser()
    config = cp.read(CONFIG_FILE)
    if len(config) != 1:
        raise ValueError(
            "Auth config file {} missing, please populate it as documented".format(
                CONFIG_FILE
            )
        )

    user = cp.get("auth", "user")
    password = cp.get("auth", "pass")

    try:
        return mark(user, password)
    finally:
        disconnect()


def disconnect():
    cur.close()
    cur.logout()


if __name__ == "__main__":
    sys.exit(main())
