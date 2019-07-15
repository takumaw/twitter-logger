"""Base Command class"""

import sys
import os
import re
import logging

import yaml
import pymongo
import tweepy

class Base(object):
    """A base class for commands"""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

        self.debug = False
        self.verbose = False

        self.host = None
        self.port = None
        self.database = None
        self.collection = None
        self.mongo_client = None
        self.mongo_database = None
        self.mongo_collection = None

        self.consumer_key = None
        self.consumer_secret = None
        self.access_key = None
        self.access_secret = None
        self.twitter_api_config = {
            "wait_on_rate_limit": True,
            "wait_on_rate_limit_notify": True,
            "retry_count": 5,
            "retry_delay": 60,
            "retry_errors": [500, 501, 502, 503, 504],
        }
        self.twitter_auth = None
        self.twitter_api = None

        self.target_users = []

        self.parse_options()
        self.setup_logger()

    def parse_options(self):
        """Parse command line self.options."""

        # Parse logging-related options
        if self.options.get("--verbose"):
            self.verbose = True

        # Parse MongoDB-related self.options
        if self.options.get("--host"):
            if not self.options.get("HOST:PORT"):
                print("HOST and/or PORT is not specified correctly.",
                      file=sys.stderr)
                sys.exit(1)
            elif not re.match("[^:]+:[0-9]+$", self.options.get("HOST:PORT")):
                print("HOST and/or PORT is not specified correctly.",
                      file=sys.stderr)
                sys.exit(1)
            else:
                self.host, self.port = self.options.get("HOST:PORT").split(":")

        if self.options.get("--database"):
            if not self.options.get("DATABASE"):
                print("DATABASE is not specified correctly.",
                      file=sys.stderr)
                sys.exit(1)
            else:
                self.database = self.options.get("DATABASE")

        if self.options.get("--collection"):
            if not self.options.get("COLLECTION"):
                print("DATABASE is not specified correctly.",
                      file=sys.stderr)
                sys.exit(1)
            else:
                self.collection = self.options.get("COLLECTION")

        # Parse Twitter API-related self.options
        if self.options.get("--credential"):
            if not self.options.get("CREDENTIAL_FILE"):
                print("TARGET_USERS_FILE is not specified correctly.",
                      file=sys.stderr)
                sys.exit(1)
            with open(self.options.get("CREDENTIAL_FILE")) as f:
                self._parse_credential_file(f)
        elif self.options.get("CONSUMER_KEY") and \
             self.options.get("CONSUMER_SECRET") and \
             self.options.get("ACCESS_KEY") and \
             self.options.get("ACCESS_SECRET"):
            self.consumer_key = self.options.get("CONSUMER_KEY")
            self.consumer_secret = self.options.get("CONSUMER_SECRET")
            self.access_key = self.options.get("ACCESS_KEY")
            self.access_secret = self.options.get("ACCESS_SECRET")
        elif self.options.get("--credential-env"):
            if not os.getenv("TWITTER_CONSUMER_KEY", None) or \
               not os.getenv("TWITTER_CONSUMER_SECRET", None) or \
               not os.getenv("TWITTER_ACCESS_KEY", None) or \
               not os.getenv("TWITTER_ACCESS_SECRET", None):
                print("Credential variable(s) are not specified correctly.",
                      file=sys.stderr)
                sys.exit(1)
            else:
                self.consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
                self.consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
                self.access_key = os.getenv("TWITTER_ACCESS_KEY")
                self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")

        # Parse target users
        if self.options.get("--targets"):
            if not self.options.get("TARGET_USERS_FILE"):
                print("TARGET_USERS_FILE is not specified correctly.",
                      file=sys.stderr)
                sys.exit(1)
            if self.options.get("TARGET_USERS_FILE") == "-":
                self.target_users += self._parse_target_users_file(sys.stdin)
            else:
                with open(self.options.get("TARGET_USERS_FILE")) as f:
                    self.target_users += self._parse_target_users_file(f)

        if self.options.get("USER"):
            self.target_users += self._parse_target_users(self.options.get("USER"))

    def _parse_credential_file(self, f):
        """Load Twitter credential from YAML file."""
        credential = yaml.safe_load(f)
        self.consumer_key = credential["consumer_key"]
        self.consumer_secret = credential["consumer_secret"]
        self.access_key = credential["access_key"]
        self.access_secret = credential["access_secret"]

    def _parse_target_users(self, users):
        target_users = []
        for u in users:
            target_user = {
                "screen_name": u,
                "user_id": None,
            }
            target_users.append(target_user)
        return target_users

    def _parse_target_users_file(self, f):
        """Load target users from file."""
        target_users = []
        for ln in f:
            if ln.startswith("#"):
                continue
            else:
                u = ln.split()
                user = {
                    "user_id": int(u[0]),
                    "screen_name": u[1],
                }
                target_users.append(user)
        return target_users

    def setup_logger(self):
        if self.debug:
            logging.basicConfig(format="%(asctime)s %(message)s",
                                level=logging.DEBUG)
        elif self.verbose:
            logging.basicConfig(format="%(asctime)s %(message)s",
                                level=logging.INFO)
        else:
            logging.basicConfig(format="%(asctime)s %(message)s",
                                level=logging.WARNING)

    def setup_db(self):
        """Establish MongoDB connection."""
        if self.host and self.port and self.database:
            self.mongo_client = pymongo.MongoClient(host=self.host,
                                                    port=int(self.port))
            self.mongo_database = self.mongo_client[self.database]
            if self.collection:
                self.mongo_collection = self.mongo_database[self.collection]

    def setup_api(self):
        """Setup Twitter API."""
        if self.consumer_key and self.consumer_secret and \
           self.access_key and self.access_secret:
            self.twitter_auth = tweepy.OAuthHandler(self.consumer_key,
                                                    self.consumer_secret)
            self.twitter_auth.set_access_token(self.access_key,
                                               self.access_secret)
            self.twitter_api = tweepy.API(self.twitter_auth,
                                          **self.twitter_api_config)

    def run(self):
        raise NotImplementedError('Not Implemented.')
