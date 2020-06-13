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

You might also want to ``unset wait_key`` in your mutt config to avoid the
"press any key to continue" prompt.

Installation
============

To install the latest stable version from PyPi:

.. code::

    pip install -U gmute

To install the latest development version directly from GitHub:

.. code::

    pip install -U git+https://github.com/cdown/gmute.git
