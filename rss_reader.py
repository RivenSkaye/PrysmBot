"""
An extension to a utility bot for Discord.
This part of code magically reads RSS Feeds
Author: RivenSkaye / FokjeM
"""
import feedparser
import json
import requests
from dateutil.parser import parse

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
try :
    with open("RSS/RSS.json", "r") as rss:
        feed = json.load(rss)
        assert (len(feed.keys()) > 0), "There are no webhooks given!"
except FileNotFoundError:
    with open("RSS/RSS.json", "w+") as rss:
        rss.write("{\r\n    \"<Webhook URL>\": \"<RSS Feed URL>\"\r\n}")
        print("There was no RSS.json found; It was created, now add the info for the RSS Feed.")
    exit(1)
except AssertionError:
    print("No token given! Fix your Prysm.json!")
    exit(1)
    feed = json.load(rss)
WEBHOOK = feed.keys()[0]