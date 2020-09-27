"""
RSS Reading cog for sending RSS feed information to Webhooks.
This was built with the intent of sending stuff to Discord servers.
Author: RivenSkaye / FokjeM
Special thanks: Nala_Alan
"""
# No import for the cog system, this should just run without any commands.
# Built-ins
import json
# Dependencies
import feedparser
import requests
from dateutil.parser import parse

# Headers to set for all webhooks
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
try:
    with open("RSS/RSS.json", "r") as rss:
        webhooks = json.load(rss)
        assert (len(webhooks.keys()) > 0), "There are no Webhooks given!"
except FileNotFoundError:
    with open("RSS/RSS.json", "w+") as rss:
        rss.write("{\n\n}")
        print("There was no RSS.json found; It was created, now add the info for the RSS Feeds.")
except AssertionError:
    print("Don't use the -rss option when no RSS feeds are being listened to!")

def keysort(val):
    return parse(val["published"])

def rss_fetch(webhook, feed, archive, archive_file, archive_only: bool=False) -> bool:
    try:
        data = requests.get(url=feed, timeout=20).text
    except:
            data = None
    new_archive = []
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
                print(f"The feed located at {feed} does not provide a common identifier for entries.\r\nIt can therefore not be parsed reliably for new entries.\n\tIt has been deleted.")
                return False;
            if rel not in archive:
                print(rel)
                try:
                    if not archive_only:
                        requests.post(url=webhook, data=f"content={rel}", headers=HEADERS, timeout=20)
                    new_archive.append(rel)
                    with open("RSS/archive.txt", "a") as archive_file:
                        for line in new_archive:
                            archive_file.write(f"{line}\n")
                except Exception as e:
                    print(f"Could not get the RSS feed!\n{e}")
                    continue # There may not be any more code in this loop."""
        return True;

def run_all(archive_only: bool=False):
    print(webhooks)
    try:
        with open("RSS/archive.txt", "r") as archive_file:
            archive = archive_file.read().split("\n")
    except:
        with open("RSS/archive.txt", "x") as archive_file:
            archive = [] # Don't actually write to the file; we're only adding new entries after all
    for webhook in webhooks.keys():
        for feed in webhooks[webhook]:
            if not rss_fetch(webhook, feed, archive, archive_file, archive_only):
                webhooks[webhook].pop(feed, None)
    return;
