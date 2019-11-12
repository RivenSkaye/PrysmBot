"""
An extension to a utility bot for Discord.
This part of code magically reads RSS Feeds
Author: RivenSkaye / FokjeM
"""
# Built-ins
import json
# Dependencies
import feedparser
import requests
from dateutil.parser import parse

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
try :
    with open("RSS/RSS.json", "r") as rss:
        feeds = json.load(rss)
        assert (len(feeds.keys()) > 0), "There are no Webhooks given!"
except FileNotFoundError:
    with open("RSS/RSS.json", "w+") as rss:
        rss.write("{\n\n}")
        print("There was no RSS.json found; It was created, now add the info for the RSS Feeds.")
except AssertionError:
    print("Don't use the -rss option when no RSS feeds are being listened to!")
    exit(1)

def keysort(val):
    return parse(val["published"])

def rss_fetch(archive_only=False):
    try:
        with open("RSS/archive.txt", "r") as archive_file:
            archive = archive_file.read().split("\n")
    except:
        with open("RSS/archive.txt", "x") as archive_file:
            archive = [] # Don't actually write to the file; we're only adding new entries after all
    new_archive = []
    for feed in feeds.keys():
        try:
            data = requests.get(url=feed, timeout=20).text
        except:
            data = None
        if data:
            for release in sorted(feedparser.parse(data).entries, key=keysort):
                if "guid" in release.keys():
                    rel = release["guid"]
                elif "GUID" in release.keys():
                    rel = release["GUID"]
                elif "uid" in release.keys():
                    rel = release["guid"]
                elif "UID" in release.keys():
                    rel = release["GUID"]
                elif "id" in release.keys():
                    rel = release["id"]
                elif "ID" in release.keys():
                    rel = release["ID"]
                else:
                    feeds.pop(feed, None)
                    print("The feed located at %s does not provide a common identifier for entries.\r\nIt can therefore not be parsed reliably for new entries.\n\tIt has been deleted." % feed)
                    continue
                if rel not in archive:
                    try:
                        if not archive_only:
                            requests.post(url=feeds[feed], data=f"content={rel}", headers=HEADERS, timeout=20)
                        new_archive.append(rel)
                        with open("RSS/archive.txt", "a") as archive_file:
                            for line in new_archive:
                                archive_file.write(f"{line}\n")
                    except Exception as e:
                        print("Could not get the RSS feed!\r\n%s" % e)
                        continue # There may not be any more code in this loop.
