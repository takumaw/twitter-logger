"""UserStream crawler command"""

import sys
import os
import re
import time
import datetime
import traceback
import json
import logging
import pprint

import pymongo
import tweepy

from .base import Base
from ..utils import common


class UserStream(Base):
    """UserStream crawler"""

    def run(self):
        self.setup_db()
        self.setup_api()

        while True:
            try:
                listener = StreamListener(self.mongo_database)
                stream = tweepy.streaming.Stream(self.twitter_auth, listener)
                stream.userstream()
            except Exception as err:
                logging.error(traceback.format_exc())
                time.sleep(30)


class StreamListener(tweepy.streaming.StreamListener):
    def __init__(self, database):
        super().__init__(self)
        self.database = database

    def on_data(self, data):
        d = json.loads(data)
        common.parse_created_at(d)
        d["_timestamp"] = datetime.datetime.utcnow()

        if "text" in d and "entities" in d:
            logging.info("on_data: {}".format("status"))
            self.database["status"].insert_one(d)
        elif "delete" in d:
            logging.info("on_data: {}".format("delete"))
            self.database["delete"].insert_one(d)
        elif "event" in d:
            logging.info("on_data: {}".format("event"))
            self.database["event"].insert_one(d)
        else:
            logging.warning(pprint.pformat(d))
            self.database["unknown"].insert_one(d)

    def on_error(self, status_code):
        logging.error("on_error: {}".format(status_code))
        raise Exception("on_error: {}".format(status_code))
