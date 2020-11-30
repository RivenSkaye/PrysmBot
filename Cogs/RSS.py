"""
RSS Reading cog for sending RSS feed information to Webhooks.
This was built with the intent of sending stuff to Discord servers.
Author: RivenSkaye / FokjeM
Special thanks: Nala_Alan
                ngl, most of the code is his, with tweaks to fit my use case.
                This is about to be rewritten for nice JSON + POST webhooks.
"""
# No import for the cog system, this should just run without any commands.
# Built-ins
import json
# Dependencies
import feedparser
import requests
from dateutil.parser import parse

"""
Nala_Alan's keysort function.
This does not belong in the class, but the code depends on it.
"""
def keysort(val):
    return parse(val["published"])

class Prysm_RSS:
    """
    Simple Python class to complement Prysm.
    Fetches RSS feeds as defined in a file and sends back a message for all new
    entries in the feed.
    Primarily aimed at Nyaa releases, might gain more uses later.
    """

    def __init__(self, rssfile: str="RSS.json", rsspath: str="./RSS/", rssarchive: str="archive.txt"):
        if not self._check_create_file(filename=rssfile, filepath=rsspath):
            print(f"Created a new file for info at {rsspath}{rssfile}")
        if not self._check_create_file(filename=rssarchive, filepath=rsspath):
            print(f"Created a new file for info at {rsspath}{rssfile}")
        self.file = rssfile
        self.path = rsspath
        self.archive = rssarchive

    """
    Function to check if the files for sending feed info exist.
    If they don't exist, they will be created.

    :param filename: str:   Name of the file to look for, defaults to 'RSS.json'.
    :param filepath: str:   Path where the file is found. Relative or exact.
                            Be aware of the CWD for relative paths!

    :return: bool:          True if the file was there, false if not.
    """
    def _check_create_file(self, filename: str, filepath: str) -> bool:
        retval = False # Assume it's not there, always
        try:
            with open(filepath+filename, "r") as rss: # Try opening it in read-only mode
                retval = True # If it works, we flip to true
        except FileNotFoundError: # If it didn't exist...
            with open(filepath+filename, "w+") as rss: # ... create it and write to it
                rss.write("") # Make it an empty JSON file.
        return retval

    """
    Checks an RSS feed for new data and stores the ID for this feed in the archive.

    :param feed: str:           URL to the actual RSS feed.
    :param archive: str:        filename for the archive file. The path is assumed
                                to be the same as where the RSS.json lives.
    :param webhook: str:        URL to post the webhook messages to.
    :param archive_only: bool:  Whether or not just to archive URLs without posting.
                                Defaults to False, run with True the first time
                                to prevent massive spam!
    :param **kwargs: Any:       Keyword Args for the JSON data sent to Discord.
                                content, file and payload_jason will be ignored!
                                For more info, consult Discord's docs:
                                https://discord.com/developers/docs/resources/webhook#execute-webhook

    :return: int:               0 on success. 1 if a feed doesn't work,
                                2 if a webhook doesn't respond.
                                3 means PANIC MODE.
    """
    def rss_fetch(self, feed: str, path: str, archive: str, webhook: str, archive_only: bool=False, **kwargs) -> int:
        try:
            data = requests.get(url=feed, timeout=7.5).text # Timeout after 7.5s.
        except:
            return 1
        if data:
            ignored = ["content", "file", "payload_json"]
            with open(path+archive, "r") as arch:
                old_archive = [val for val in arch.read().split('\n') if val]
            print(old_archive)
            new_archive = []
            for release in sorted(feedparser.parse(data).entries, key=keysort):
                # Grab the correct identifier name, which is something like these
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
                else: # No identifier we can recognize? Just drop it and die.
                    print(f"The feed located at {feed} does not provide a known common identifier for entries.\nIt can therefore not be parsed reliably for new entries.\n\tIt has been deleted.")
                    return 1;
                if rel not in old_archive:
                    try:
                        if not archive_only:
                            msg_body = {"content": rel}
                            # Set additional info, ignore content, file and payload_json
                            for arg in kwargs.keys():
                                if arg not in ignored:
                                    msg_body[arg] = kwargs[arg]
                            # Send the message to Discord
                            requests.post(url=webhook, json=msg_body, timeout=5)
                    except Exception as e:
                        print(f"Couldn't send message to Discord!\n{e}")
                        continue #don't finish the loop, don't archive, retry next time.
                    new_archive.append(rel)
            # Save all the keys we got. If we're not receiving an old key anymore, we won't ever again unless pagination changes radically.
            with open(path+archive, "at") as arch:
                for line in new_archive:
                    arch.write(f"{line}\n")
            return 0
        # If due to a freak accident we got an empty string
        return 3

    def fetch_all(self, archive_only: bool=False):
        with open(self.path+self.file) as rssjson:
            webhooks = json.load(rssjson)
        for webhook in webhooks.keys():
            for feed in webhooks[webhook]:
                code = self.rss_fetch(feed, self.path, self.archive, webhook, False)
                if code == 0:
                    continue
                if code == 1:
                    webhooks[webhook].pop(feed, None)
                elif code == 2:
                    webhooks.pop(webhook, None)
                elif code == 3:
                    print(f"For some weird reason, the RSS feed at {feed} yields no results.\n\tPLEASE MONITOR!!")
