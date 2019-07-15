"""Status crawler command"""

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


class Status(Base):
    """Status crawler"""

    def run(self):
        self.setup_db()
        self.setup_api()

        while True:
            for user in self.target_users:
                logging.info(u"Archiving {}".format(user["screen_name"]))
                last_tweet = self.mongo_collection.find_one(
                    {"user.id": user["user_id"]},
                    sort=[("id", pymongo.DESCENDING)])
                since_id = last_tweet["id"] if last_tweet else None
                statuses = []
                try:
                    for s in tweepy.Cursor(self.twitter_api.user_timeline,
                                           user_id=user["user_id"],
                                           since_id=since_id,
                                           count=200,
                                           include_rts=True,
                                           exclude_replies=False,
                                           trim_user=False,
                                           contributor_details=True).items():
                        statuses.append(s._json)
                except tweepy.TweepError as err:
                    logging.error(traceback.format_exc())
                    continue
                logging.info("    received {} items.".format(statuses))

                if statuses:
                    for s in statuses:
                        common.parse_created_at(s)
                        s["_crawled_at"] = datetime.datetime.utcnow()
                    self.mongo_collection.insert_many(statuses)
                logging.info("    saved {} items.".format(statuses))
