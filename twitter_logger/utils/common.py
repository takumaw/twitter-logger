"""Common functions."""

import datetime


def parse_created_at(obj):
    if isinstance(obj, dict):
        for key in obj:
            if key == u"created_at":
                obj[key] = datetime.datetime.\
                    strptime(obj[key], "%a %b %d %H:%M:%S +0000 %Y")
            elif isinstance(obj[key], dict):
                parse_created_at(obj[key])
    elif isinstance(obj, list):
        for itm in obj:
            parse_created_at(itm)
