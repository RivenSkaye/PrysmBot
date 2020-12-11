"""
RSS Reading cog for sending RSS feed information to Webhooks.
This was built with the intent of sending stuff to Discord servers.
Author: RivenSkaye
Special thanks: Nala_Alan
                The original code was his, rewritten to be callable from a
                Discord bot. It has since been rewritten again to use his
                base workflow, but heavily modified and with JSON requests
                to the Discord WebHooks rather than HTTP form data
"""
# No import for the cog system, this should just run without any commands.
# Built-ins
import asyncio
import json
from time import sleep # Used to prevent getting blocked for too many requests
# Dependencies
from discord.ext import commands
import discord
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

    :return: int:               0 on success.
                                1 if a feed doesn't work,
                                2 if a webhook doesn't respond.
                                3 means PANIC MODE.
    """
    async def rss_fetch(self, feed: str, path: str, archive: str, webhook: str, archive_only: bool=False, **kwargs) -> int:
        try:
            data = requests.get(url=feed, timeout=7.5).text # Timeout after 7.5s.
        except:
            return 1
        if data:
            ignored = ["content", "file", "payload_json"]
            with open(path+archive, "r") as arch:
                old_archive = [val for val in arch.read().split('\n') if val]
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

    """
    Loops over all feeds listed in the feeds file. Allows to set a limit to
    limit the amount of requests made per second.

    :param limit: int:          The limit on the amount of requests to send
                                per second. Set to 0 to disable.
                                Use this parameter to prevent sending too many
                                requests to a feed and getting blocked.
                                Defaults to 500 requests per second.
    :param archive_only: bool:  Passed through to the singular rss_fetch.
                                Defaults to False.
    """
    async def fetch_all(self, limit: int=500, archive_only: bool=False):
        with open(self.path+self.file) as rssjson:
            webhooks = json.load(rssjson)
        codes = []
        for webhook in webhooks.keys():
            for feed in webhooks[webhook]:
                codes.append(self.rss_fetch(feed, self.path, self.archive, webhook, False))
            if limit > 0:
                sleep(1/limit)
        for result in codes:
            code = await result
            print(code)
            if code == 0:
                continue
            if code == 1:
                webhooks[webhook].pop(feed, None)
            elif code == 2:
                webhooks.pop(webhook, None)
            elif code == 3:
                print(f"For some weird reason, the RSS feed at {feed} yields no results.\n\tPLEASE MONITOR!!")

class RSS(commands.Cog):
    """
    RSS Cog for Prysm, this handles manipulating what feeds to fetch and
    which Webhooks it should send the messages to.
    Also handles some setup for creating new Webhooks to work with.
    """
    def __init__(self, bot):
        self.bot = bot
        self.COG_NAME = "RSS"
        self.footer = "_RSS management is restricted to users that have both 'Manage Channel' and 'Manage Webhooks' permissions. Please keep this in mind when using commands in this cog._"

    """
    This is going to warn users that rss is not a command and then present them
    with a nice list of all commands in this cog.
    Calling this is basically giving out an error message!
    """
    @commands.group(invoke_without_command=True, cog_name="RSS", name="rss")
    async def rss(self, ctx):
        embedtext = "You have tried to call a command group as a command, this doesn't work unfortunately.\nThere's a set list of commands in this group that you _can_ use however."
        commandlist = ""
        for command in self.get_commands():
            commandlist += f"- {command.name}\n"
        e = discord.Embed(title="RSS Cog Info", type="rich", colour=discord.Colour.from_rgb(172, 43, 43), author=ctx.author, description=embedtext, footer=self.footer)
        e.add_field(name="Commands in this cog:", value=commandlist)
        ctx.channel.send(embed=e)
