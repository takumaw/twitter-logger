"""Favorites crawler command"""

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


class Favorites(Base):
    """Favorites crawler"""

    def run(self):
        self.setup_db()
        self.setup_api()

        while True:
            for user in self.target_users:
                logging.info("Archiving {}".format(user["screen_name"]))
                last_tweet = self.mongo_collection.find_one(
                    {"favorited_by_user_id": user["user_id"]},
                    sort=[("id", pymongo.DESCENDING)])
                since_id = last_tweet["id"] if last_tweet else None
                favs = []
                try:
                    favorites = tweepy.Cursor(self.twitter_api.favorites,
                                              user_id=user["user_id"],
                                              since_id=since_id,
                                              count=200,
                                              include_entities=True).items()
                    for f in favorites:
                        favs.append(f._json)
                except tweepy.TweepError as err:
                    logging.error(traceback.format_exc())
                    continue
                logging.info("    received {} items.".format(favs))

                if favs:
                    for f in favs:
                        common.parse_created_at(f)
                        f["_timestamp"] = datetime.datetime.utcnow()
                        f["favorited_by_user_id"] = user["user_id"]
                    self.mongo_collection.insert_many(favs)
                logging.info("    saved {} items.".format(favs))
