tweetwatch
==========

A Python module to collect and analyze tweets through Twitter's streaming API.

## Introduction

For those with Twitter Oauth-based access tokens (which are freely available:
[https://dev.twitter.com/docs/auth/obtaining-access-tokens]), this module does several things:

1. Configure a connection and search parameters quickly and easily.
2. Connect to Twitter's streaming API endpoint: connect, maintain, recover a connection.
3. Route, and to some extent analyze, received data.

## Requirements

To work properly, this module requires several other Python modules to be installed. One of those
isn't currently a standard module, but it can be loaded locally (without root access).

Note: You can check to see if a module loads by running `python` and entering `import modulename` at
the prompt, replacing modulename with the appropriate module.

1. python module: pycurl (This is usually already installed. If it isn't, the following command will
work on Debian/Ubuntu machines: `sudo apt-get install python-pycurl`)
2. python module: urllib (this is usually already installed. If it isn't, the following command will
work on Debian/Ubuntu machines: `sudo apt-get install python-urllib`)
3. non-standard python oauth2 module: get at [https://github.com/simplegeo/python-oauth2] You can
install this by running the contained setup.py (`python setup.py install`). Alternatively, without
root access (or to limit the install locally) you can use `python setup.py install --user` or
`python setup.py install --prefix=/home/mydir/`.

Also, we use the Python Simplejson module and fall back to the standard json module when this
doesn't exist. It is recommended that you install simplejson if it isn't currently on your system.
It's simply a faster and better-developed version of the standard Python json module.

## Installation

I haven't written a setup script for this module yet. For now, just copy the module's `tweetwatch'
directory (which contains a `__init__.py`, `meters.py`, and `stream.py`) so that it is a
subdirectory of your working directory.


