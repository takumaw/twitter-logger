"""
Twitter logger that stores into MongoDB.

  twitter_logger COMMAND [OPTIONS]

Usage:
  twitter_logger userstream [-v] -H HOST:PORT -D DATABASE
    (-c CREDENTIAL_FILE | --credential-env | --consumer-key CONSUMER_KEY --consumer-secret CONSUMER_SECRET --access-key ACCESS_KEY --access-secret ACCESS_SECRET)
  twitter_logger status [-v] -H HOST:PORT -D DATABASE -C COLLECTION
    (-c CREDENTIAL_FILE | --credential-env | --consumer-key CONSUMER_KEY --consumer-secret CONSUMER_SECRET --access-key ACCESS_KEY --access-secret ACCESS_SECRET) (-t TARGET_USERS_FILE | USER [USER...])
  twitter_logger favorites [-v] -H HOST:PORT -D DATABASE -C COLLECTION
    (-c CREDENTIAL_FILE | --credential-env | --consumer-key CONSUMER_KEY --consumer-secret CONSUMER_SECRET --access-key ACCESS_KEY --access-secret ACCESS_SECRET) (-t TARGET_USERS_FILE | USER [USER...])
  twitter_logger friends [-v] -H HOST:PORT -D DATABASE -C COLLECTION
    (-c CREDENTIAL_FILE | --credential-env | --consumer-key CONSUMER_KEY --consumer-secret CONSUMER_SECRET --access-key ACCESS_KEY --access-secret ACCESS_SECRET) (-t TARGET_USERS_FILE | USER [USER...])
  twitter_logger followers [-v] -H HOST:PORT -D DATABASE -C COLLECTION
    (-c CREDENTIAL_FILE | --credential-env | --consumer-key CONSUMER_KEY --consumer-secret CONSUMER_SECRET --access-key ACCESS_KEY --access-secret ACCESS_SECRET) (-t TARGET_USERS_FILE | USER [USER...])

Options:
  --help                Show usage help.
  --version             Show version.
  -v --verbose          Enable verbose output.
  -H --host             Host name.
  -D --database         Database name.
  -C --collection       Collection name.
  -c --credential       Specify Twitter API credential file.
  --credential-env      Retrieve credential keys from environmental variables.
  --consumer-key        Specify CONSUMER_KEY.
  --consumer-secret     Specify CONSUMER_SECRET.
  --access-key          Specify ACCESS_KEY.
  --access-secret       Specify ACCESS_SECRET.
  -t --targets          Specify target users file.
"""


import docopt
import inspect

from . import __version__
from . import commands as commands_


def main():
    options = docopt.docopt(__doc__, version=__version__)
    for name, module in inspect.getmembers(commands_, inspect.isclass):
        if options.get(name.lower()) and name != "Base":
            module(options).run()
