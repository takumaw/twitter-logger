"""Users crawler command"""

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


class Users(Base):
    """Users crawler"""

    def run(self):
        self.setup_db()
        self.setup_api()

        while True:
            target_user_chunks = [self.target_users[i:i + 100] for i in range(0, len(self.target_users), 100)]
            for target_user_chunk in target_user_chunks:
                logging.info(u"Archiving {} users".format(len(target_user_chunk)))
                user_ids = []
                screen_names = []
                for target_user in target_user_chunk:
                    if target_user["user_id"]:
                        user_ids.append(target_user["user_id"])
                    else:
                        screen_names.append(target_user["screen_name"])
                users = []
                try:
                    for u in self.twitter_api.lookup_users(user_ids=user_ids, screen_names=screen_names):
                        users.append(u._json)
                except tweepy.TweepError as err:
                    logging.error(traceback.format_exc())
                    continue
                logging.info("    received {} items.".format(len(users)))

                if users:
                    for u in users:
                        common.parse_created_at(u)
                        u["_crawled_at"] = datetime.datetime.utcnow()
                    self.mongo_collection.insert_many(users)
                logging.info("    saved {} items.".format(len(users)))
