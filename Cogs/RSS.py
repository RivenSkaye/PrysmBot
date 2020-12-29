""" RSS Reading cog for sending RSS feed information to Webhooks.

This was built with the intent of sending stuff to Discord servers,
leveraging the Webhook system to circumvent auth requirements, whilst
allowing for users to separate the information per source visually and
using names and identifiers of their choice.
Webhooks given are parsed and checked to be actual Discord links and
present in the server they're added from.
Author: RivenSkaye
Special thanks: Nala_Alan
                The original code was his, rewritten to be callable from a
                Discord bot. It has since been rewritten again, but maintains
                his core parsing code with a small added check to require an
                identifier field. Nala_Alan's POST request has been replaced
                to send a JSON payload and use aiohttp in order to fetch and
                send the data asynchronously, to be non-blocking to the bot's
                other coroutines.
"""

# Built-ins
import asyncio
import json
from typing import Optional, Union
from datetime import datetime, timezone
# Dependencies
import discord
from discord.ext import commands
import aiohttp
import feedparser

def keysort(val):
    """ Nala_Alan's keysort function. Meant to be used as a callback.

    We only need a single key to sort on, which is why we can't use just the
    built-in and instead need a simple wrapper func. Might a lambda be better?
    This does not belong in the class, but the code depends on it.
    """
    return parse(val["published"])

class Prysm_RSS:
    """Simple Python class to complement Prysm. Users don't touch this class!

    THIS WILL SOON BE DEPRECATED MOVED TO :class:`RSS`!!

    Fetches RSS feeds as defined in a file and sends back a message for all new
    entries in the feed.
    Primarily aimed at Nyaa releases, might gain more uses later.
    """

    def __init__(self, bot, rsspath: str="./RSS/"):
        self.bot = bot
        self.path = rsspath

# MOVE ALL OF THIS CODE AND REWRITE FOR aiohttp

    async def rss_fetch(self, feed: str, path: str, archive: str, webhook: str, archive_only: bool=False, **kwargs) -> int:
        """Checks an RSS feed for new data and archives it

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
                relkeys = release.keys()
                # Grab the correct identifier name, which is something like these
                if "guid" in relkeys:
                    rel = release["guid"]
                elif "GUID" in relkeys:
                    rel = release["GUID"]
                elif "uid" in relkeys:
                    rel = release["guid"]
                elif "UID" in relkeys:
                    rel = release["GUID"]
                elif "id" in rrelkeys:
                    rel = release["id"]
                elif "ID" in relkeys:
                    rel = release["ID"]
                else: # No identifier we can recognize? Just drop it and die.
                    print(f"The feed located at {feed} does not provide a known common identifier for entries.\nIt can therefore not be parsed reliably for new entries.\n\tIt has been deleted.")
                    return 1;
                if "title" in relkeys:
                    rel = f"**{release['title']}**\n{rel}"
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

    async def fetch_all(self, limit: int=500, archive_only: bool=False):
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

    def __init__(self, bot, rsspath: str="./RSS/"):
        self.bot = bot
        self.path = rsspath
        self.COG_NAME = "RSS"
        self.footer = "_RSS management is restricted to bots and users that have the guild-wide 'Manage Channel' and 'Manage Webhooks' permissions._"

    def _check_or_create_file(self, filename: str, filepath: str) -> bool:
        """Function to check if a file exists, creates it if it doesn't.

        :param filename: str:   Name of the file to look for, defaults to 'RSS.json'.
        :param filepath: str:   Path where the file is found. Relative or exact.
                                Be aware of the CWD for relative paths!

        :return: bool:          True if the file was there, false if not.
        """
        retval = False # Assume it's not there, always
        try:
            # Try and see if the file exists and flip to True
            with open(filepath+filename, "r") as rss:
                retval = True
        # If it doesn't exist, we get a FileNotFound
        except FileNotFoundError:
            # So we create it.
            with open(filepath+filename, "w+") as rss:
                # Force a write
                rss.write("")
        return retval

    @commands.group(invoke_without_command=True, case_insensitive=True, cog_name="RSS", name="rss")
    @commands.has_guild_permissions(manage_channels=True, manage_webhooks=True)
    @commands.guild_only()
    async def rss(self, ctx):
        """
        This is going to warn users that rss is not a command and then present them
        with a nice list of all commands in this cog.
        Calling this is basically giving out a simplified help message!
        """
        embedtext = "This command group has no base command unfortunately.\nThere's a set list of commands in this group that you _can_ use however. More info on these with `help rss <command>`"
        commandlist = ""
        for command in self.get_commands():
            commandlist += f"- {command.name}\n"
        e = discord.Embed(title="RSS Cog Info", type="rich", colour=discord.Colour.from_rgb(172, 43, 43), author=ctx.author, description=embedtext, footer=self.footer)
        e.add_field(name="Commands in this cog:", value=commandlist)
        ctx.send(embed=e)

    @rss.command(name='serverwebhooks', aliases=['servhooks', 'swh'])
    async def get_webhooks(self, ctx):
        """
        Get all webhooks registered for this server on the Discord end of things.
        Easy to get info to register new listeners with.
        """
        with ctx.typing():
            hooks = []
            webhooks = await ctx.guild.webhooks()
            if len(webhooks) == 0:
                ctx.message.send("There are no webhooks registered for this server.\nPlease add one and try again.")
            for webhook in webhooks:
                hook = f"**{webhook.name}**. id: {webhook.id}, channel: {webhook.channel}.\n"
                hooks.append(hook)
            msgs = bot._split_messages(hooks)
            for msg in msgs:
                await ctx.send(msg)

    @rss.command(name='listall')
    async def listall(self, ctx):
        """
        List all feeds the bot is sending for every webhook.
        Operation may take a while if a lot of data has to be processed,
        thus we set the bot to a typing status until it's done.
        """
        webhooks = await ctx.guild.webhooks()
        async with ctx.typing():
            with open(self.path+self.file, 'rt') as rf:
                hooks = json.load(rf)
                guildhooks = []
                for wh in webhooks:
                    if wh.url in hooks.keys():
                        guildhooks.append(wh)
            await ctx.send("**Feeds being listened to in this guild per webhook:**")
            feeds = []
            for wh in guildhooks:
                feeds.append(f"**{wh.name}** ({wh.channel}):\n{hooks[wh.url]}\n------------------")
                msgs = bot._split_messages(feeds)
                for msg in msgs:
                    await ctx.send(msg)

    @rss.command(name="addfeed", aliases=['new', 'af', 'add'])
    async def addfeed(self, ctx, feed: str, hook: Union[str,int], interval: int=60):
        """Add an RSS feed to listen to, and a webhook to send the messages to.

        Minimum time is every 15 minutes, maximum is whatever apscheduler allows.

        :param feed: str:       The url pointing to the RSS feed.
                                May be enclosed in <> for link suppression.
        :param hook: str:       For any Webhook in this guild: the id, URL, or name.
        :param interval: int:   The interval between fetches of the feed.
                                provide time in minutes, with a minimum of 15.
        """

        # Prepare an error message for malformed use of the command.
        # The most probable issue is a malformed webhook identifier.
        # Not an RSS feed is its own beast and will be handled later.
        errcontent = f"""Could not add <{feed}> to the list due to a problem with the given Webhook.\n
        Due to the nature of Webhooks in Discord, names are case sensitive, the IDs are series of 13 numbers and URLs are without spaces.\n
        You can supply any one of these in the correct format to this function.\n\n

        Please retry the command in the format `{ctx.prefix}{ctx.invoked_with} <{feed}> <Webhook name, ID, or URL> <interval>`."""
        # Remove any link suppression
        feed = feed.replace("<", "").replace(">", "")
        webhooks = await ctx.guild.webhooks()
        for wh in webhooks:
            if hook in [wh.id, wh.name, wh.url]:
                target = wh.url
                break
        else:
            e = self.bot._gen_err(command=ctx.invoked_with, content=errcontent, member=ctx.author)
            await ctx.send(embed=e)
            return
        # We managed to find the Webhook, so now we set up shit to push to it.
        date = datetime.now(timezone.utc)
        # Create a trigger and make something to save to DB here
        pass
