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
        feeds = json.load(rss)
        assert (len(feed.keys()) > 0), "There are no Webhooks given!"
except FileNotFoundError:
    with open("RSS/RSS.json", "w+") as rss:
        rss.write("{\r\n\r\n}")
        print("There was no RSS.json found; It was created, now add the info for the RSS Feeds.")
except AssertionError:
    print("Don't use the -rss option when no RSS feeds are being listened to!")
    exit(1)

def keysort(val):
    return parse(val["published"])

def rss_fetch():
    try:
        with open("RSS/archive.txt", "r") as archive_file:
            archive = archive_file.read().split("\r\n")
    except:
        with open("RSS/archive.txt", "w") as archive_file: # Quick and dirty way to create it if it ain't there
            archive = [] # Don't actually write to the file; we're only adding new entries after all
    for feed in feeds.keys():
        try:
            data = requests.get(url=feed, timeout=30).text
        except:
            data = None
        if data:
            for release in sorted(feedparser.parse(data).entries, key=keysort):
                if release["guid"] not is None:
                    rel = release["guid"]
                elif release["GUID"] not is None:
                    rel = release["GUID"]
                if release["uid"] not is None:
                    rel = release["guid"]
                elif release["UID"] not is None:
                    rel = release["GUID"]
                elif release["id"] not is None:
                    rel = release["id"]
                elif release["ID"] not is None:
                    rel = release["ID"]
                else:
                    feeds.pop(feed, None)
                    print("The feed located at %s does not provide a common identifier for entries.\r\nIt can therefore not be parsed reliably for new entries.\r\n\tIt has been deleted." % feed)
                    continue
                if rel not in archive:
                    try:
                        request.post(url=feeds[feed], data=f"content={rel}", headers=HEADERS, timeout=30)
                        archive.append(rel)
                        with open("RSS/archive.txt", "a") as archive_file:
                            for line in archive:
                                archive_file.write("%s\r\n" % line)
                    except:
                        continue # There may not be any more code in this loop.
