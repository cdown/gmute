#!/usr/bin/env python

"""
Given a plain mail (for example, from mutt's pipe-message), mute that thread in
Gmail.

This solution is Gmail-specific, as the concept of "muting" and the X-GM-*
attributes are not standardised or widely available.
"""

import argparse
import os
import email.parser
import imaplib
import sys
import configparser

CONFIG_FILE = os.path.expanduser("~/.config/gmute")
PIPE_SEP = b"_PIPE_SEP_"

cur = imaplib.IMAP4_SSL("imap.gmail.com")


def raise_if_invalid_message_id(mid):
    """
    Check that someone hasn't provided a message ID that might be exploitative.

    This can happen if someone manually inserts PIPE_SEP into the body.
    """

    if mid[0] != "<" or mid[-1] != ">" or mid.count("<") != 1 or mid.count(">") != 1:
        raise ValueError("Invalid Message-ID: {}".format(mid))


def get_one_message_id_and_seek_to_next():
    header_lines = []
    for line in sys.stdin.buffer:
        line = line.rstrip(b"\n")

        if not line:
            break

        if line == PIPE_SEP:
            print("PIPE_SEP unexpectedly found while parsing headers?", file=sys.stderr)
            break

        header_lines.append(line)

    if not header_lines:
        return None

    for line in sys.stdin.buffer:
        if line == PIPE_SEP + b"\n":
            break

    hp = email.parser.HeaderParser()
    header_lines.append(b"")  # Trailing newline
    headers = hp.parsestr(
        "\n".join(line.decode("ascii") for line in header_lines), headersonly=True
    )
    mid = headers["Message-ID"]

    raise_if_invalid_message_id(mid)

    return mid


def icheck(ret):
    status, (data,) = ret

    if status != "OK":
        raise ValueError("Bad status '{}': {}".format(status, data))

    return data.decode("ascii")


def print_mid(mid, message, **kwargs):
    print("{}: {}".format(mid, message), **kwargs)


def login(user, password, dry_run):
    print("Logging in...")
    icheck(cur.login(user, password))
    icheck(cur.select("INBOX", readonly=dry_run))


def mark(mid, dry_run):
    base_uids_to_mute = set()

    print_mid(mid, "Searching for UID")
    initial_uid = icheck(cur.search(None, "(HEADER Message-ID %s)" % mid))
    if not initial_uid:
        print_mid(mid, "No such message", file=sys.stderr)
        return 1
    base_uids_to_mute.add(initial_uid)
    print_mid(mid, "Got initial UID {}".format(initial_uid))

    # If this is a patch cover letter, all of the rest are going to have
    # different X-GM-THRIDs
    print_mid(mid, "Looking for In-Reply-Tos")
    data = icheck(cur.search(None, "(HEADER In-Reply-To {})".format(mid)))
    if data:
        child_uids = data.split()
        base_uids_to_mute.update(child_uids)
        print_mid(mid, "Got child UIDs {}".format(child_uids))

    thread_ids = set()
    for uid in base_uids_to_mute:
        print_mid(mid, "Fetching thread ID for {}".format(uid))
        data = icheck(cur.fetch(str(uid), "(X-GM-THRID)"))
        thread_ids.add(data.split()[-1][:-1])

    for thread_id in thread_ids:
        print_mid(mid, "Looking for all mails with thread ID {}".format(thread_id))
        data = icheck(cur.search(None, "(X-GM-THRID {})".format(thread_id)))
        all_uids = data.split()

        if dry_run:
            print_mid(
                mid, "Would tag {} mails, but in dry run mode".format(len(all_uids))
            )
        else:
            print_mid(mid, "Found {} mails to tag. Tagging...".format(len(all_uids)))
            for uid in all_uids:
                icheck(cur.store(uid, "+X-GM-LABELS", r"(\Muted)"))

    print_mid(mid, "Complete for this Message-ID.")

    return 0


def run(user, password, dry_run):
    login(user, password, dry_run)
    mid = get_one_message_id_and_seek_to_next()

    if not mid:
        print("Didn't get any Message-IDs from stdin", file=sys.stderr)

    while mid:
        mark(mid, dry_run)
        mid = get_one_message_id_and_seek_to_next()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="print what we would do, but don't actually mute the messages",
    )
    return parser.parse_args()


def main():
    args = parse_args()

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
        run(user, password, args.dry_run)
    finally:
        disconnect()


def disconnect():
    cur.close()
    cur.logout()


if __name__ == "__main__":
    sys.exit(main())
