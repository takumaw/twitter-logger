"""Friends crawler command"""

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


class Friends(Base):
    """Friends crawler"""

    def run(self):
        self.setup_db()
        self.setup_api()

        while True:
            for user in self.target_users:
                logging.info(u"Archiving {}".format(user["screen_name"]))
                friends_users = []
                try:
                    for s in tweepy.Cursor(self.twitter_api.friends,
                                           user_id=user["user_id"]).items():
                        friends_users.append(s._json)
                except tweepy.TweepError as err:
                    logging.error(traceback.format_exc())
                    continue
                logging.info("    received {} items.".format(len(friends_users)))

                for f in friends_users:
                    common.parse_created_at(f)

                friends = {
                    "friends": friends_users,
                    "_crawled_at": datetime.datetime.utcnow(),
                    "_by_user_id": user["user_id"],
                }
                
                self.mongo_collection.insert_one(friends)
                logging.info("    saved {} items.".format(len(friends_users)))
