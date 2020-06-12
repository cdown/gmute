gmute adds support for Gmail's "mute" feature to mutt, and any other mail
client which can output the raw headers to a file. Muting prevents new entries
in a thread from appearing in the inbox, which can be very useful for managing
mailing list activity.

Usage
=====

First, put your IMAP credentials in ``~/.config/gmute``, like so:

::

    [auth]
    user = jcd@unatco.int
    pass = bionicman

If you want to use this from the mutt index, you can add something like the
following binding to your configuration with gmute in mutt's $PATH:

::

    macro index M '<pipe-message>gmute<enter><sync-mailbox>'

Then, with a message from a thread you want to mute highlighted in the index,
press M to mute that thread, just as would work in the Gmail UI.
