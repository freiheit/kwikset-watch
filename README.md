[![Pylint](https://github.com/freiheit/kwikset-watch/actions/workflows/pylint.yml/badge.svg)](https://github.com/freiheit/kwikset-watch/actions/workflows/pylint.yml) [![CodeQL Advanced](https://github.com/freiheit/kwikset-watch/actions/workflows/codeql.yml/badge.svg)](https://github.com/freiheit/kwikset-watch/actions/workflows/codeql.yml) [![Bandit](https://github.com/freiheit/kwikset-watch/actions/workflows/bandit.yml/badge.svg)](https://github.com/freiheit/kwikset-watch/actions/workflows/bandit.yml)

# Kwikset Battery Status Watch

## Features:

- Watches battery status of a kwikset lock that is connected to the kwikset
  cloud services (kwikset phone app works for it)
- Logs battery percentage
- Logs details if battery percentage changes, or at periodic intervals
- Can GET a simple heartbeat URL (for monitoring)
- Can POST a status update to a discord text channel (when percentage
  changes or periodically)

## TODO:

- Save auth stuff so it doesn't need 2fa every time

## Installation

1. `git clone https://github.com/freiheit/kwikset-watch.git /opt/kwikset`
2. `cd /opt/kwikset`
3. `python3 -m venv ./venv`
4. `./venv/bin/pip3 install -r requirements.txt`
5. `cp kwikset.conf-example kwikset.conf`
4. Edit kwikset.conf to have your username and password
5. Optionally set monitoring heartbeat URL and/or discord webhook URL
6. `./venv/bin/python3 watch.py`

### Important Note:

It requires 2fa validation every startup.

I run it inside screen/tmux and suggest you do the same.
