#!/usr/bin/env python3

import sys
import re
import json
import time
from datetime import datetime, timedelta


class Item:
    def __init__(self, title, subtitle, arg):
        self.title = title
        self.subtitle = subtitle
        self.arg = arg


class Feedback:
    def __init__(self, items):
        self.items = items


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


def atoi_default(s, default):
    try:
        return int(s)
    except ValueError:
        return default


LAYOUTS = [
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S %z",
    "%c",
]


def generate_items(t):
    tz = time.strftime("%Z", time.localtime())
    ts = str(int(time.mktime(t.timetuple())))
    items = [Item(ts, "Timestamp", ts)]
    items.extend([Item(t.strftime(layout), tz, t.strftime(layout))
                 for layout in LAYOUTS])
    return items


def generate_feedback(items):
    return CustomEncoder().encode(Feedback([Item(item.title, item.subtitle, item.arg) for item in items]))


def duration(timestr):
    mult = {"s": 1, "m": 60, "h": 60*60, "d": 60*60*24}
    parts = re.findall(r"(\d+(?:\.\d)?)([smhd])", timestr)
    return timedelta(seconds=sum(float(x) * mult[m] for x, m in parts))


HINT = "Please enter now+-1d1h1m1s / timestamp / %Y-%m-%d / %Y-%m-%d %H:%M:%S"


def main():
    try:
        items = list()

        arg = sys.argv[1].strip().lower()
        ts = atoi_default(arg, 0)
        if len(arg) == 0:
            now = datetime.now()
            items = generate_items(now)
        elif arg.startswith("now"):
            t = datetime.now()
            delta = arg[3:]
            if len(delta) > 0:
                if delta[0] == '+':
                    t += duration(delta[1:])
                elif delta[0] == '-':
                    t -= duration(delta[1:])

            items = generate_items(t)
        elif ts > 0:
            t = datetime.fromtimestamp(ts)
            items = generate_items(t)
        else:
            for layout in LAYOUTS:
                try:
                    t = datetime.strptime(arg, layout)
                    items = generate_items(t)
                except ValueError:
                    continue

        if len(items) == 0:
            items.append(Item(HINT, "Invalid input", HINT))

        print(generate_feedback(items))
    except IndexError:
        print("Invalid input")
        exit(1)


if __name__ == '__main__':
    main()
