"""
A utility bot for Discord.
This is the v2 rewrite, which uses actually proper code and tries to make it
as sleek and lightweight as possible. Try not to use or run anything that isn't
required and try not to use more resources than necessary.

Generator functions are better than duplicating code, since they leave a smaller
memory footprint and should be small, fast tasks that can be mostly asynced.

Author: RivenSkaye
"""
from typing import Dict, List, Any, Union
from collections.abc import Callable
import os
import json
import asyncio
import sqlite3
# Discord libraries
import discord
import discord.ext.commands
# Cog dependencies, categorized. Remove these for cogs you don't run.
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job

class Prysm(discord.ext.commands.Bot):

    def __init__(self, **kwargs): #
        try:
            with open("Prysm.json", "r") as prysmjson:
                self.base_info = json.load(prysmjson)
                assert (len(self.base_info["Token"]) > 0), "No token given! Fix your Prysm.json!"
        except FileNotFoundError:
            # Create the Prysm.json file manually, ensure we have working stuff.
            with open("Prysm.json", "w+") as prysmjson:
                prysmjson.write("{\n    'Token': '',\n    'Guilds': {}\n}")
                print("There was no Prysm.json found! It was created, now add the Token for the bot.")
            exit(1)
        except AssertionError as ae:
            print(ae)
            exit(1)
        try:
            # I assume people supplying a Prysm.json use correct keys, values and capitalization.
            # They are not immune to mistakes though, so we catch those here if they did supply a valid token. And we warn them about it.
            assert "Guilds" in self.base_info, "No Guilds object found!"
            assert isinstance(self.base_info["Guilds"], dict)
        except AssertionError as e:
            self.base_info["Guilds"] = {};
            self._saveJSON("Prysm.json", self.base_info)
        # Initialize the bot and establish connection info
        intents = discord.Intents(guilds=True,
                                  members=True,
                                  ban=True,
                                  emojis=False,
                                  integrations=False,
                                  webhooks=True,
                                  invites=False,
                                  voice_states=False,
                                  presences=True,
                                  guild_messages=True,
                                  dm_messages=False,
                                  guild_reactions=True,
                                  dm_reactions=False,
                                  typing=False)
        super().__init__(**kwargs, intents=intents)
        # standard colors for Prysm
        self.base_color = discord.Colour.from_rgb(172, 85, 172)
        self.err_color = discord.Colour.from_rgb(172, 43, 43)

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name="Riven-senpai <3", type=discord.ActivityType.listening))
        for guild in self.guilds:
            if str(guild.id) not in self.base_info["Guilds"].keys():
                guilds[str(guild.id)] = guild.name
            if os.path.isfile(str(f"Guilds/{str(guild.id)}.json")):
                with open(str("Guilds/"+str(guild.id)+".json")) as gjson:
                    g = json.load(gjson)
                    if "Init" in g:
                        e = discord.Embed(title="Prysm started", description="This is a message to let all users know Prysm is online and receptive for input.\nWorking on a full rebuild, Prysm will go off immediately.", colour=discord.Colour.from_rgb(172, 85, 172))
                        await self.get_channel(g["Init"]).send(embed=e)
        # Once the loop's done, we save all servers we're in now.
        self._saveJSON("Prysm.json", self.base_info)

    def _saveJSON(self, jsonFile: str, data: Dict[str, Any]):
        """Utility fuction to save data to a JSON file. Will be replaced with async DB func

        param: str jsonFile:    A file name or path for use with open()
        param: Dict data:       The data to be saved, dicts convert very easily.
        """
        with open(jsonFile, "w") as jsonHandle:
            json.dump(data, jsonHandle, indent=4)

    def _split_messages(self, list_in, limit: int=1750) -> List:
        """Pagination function to split messages before they get too big.
        Leaves 250 chars of space to perform join and formatting operations.

        :param list: list_in:   The input list to process
        :param int: limit:      Max amount of chars in a message.
                                Defaults to 1750 to be safe on the 2k limit.

        :return: list:          A list of messages to send in succession
        """
        ret = []
        msg = ""
        for entry in list_in:
            # append the messages until we get to the char limit
            if len(msg) + len(str(entry)) <= limit:
                msg.append(str(entry))
            else:
                ret.append(msg)
                msg = entry
        # Make sure to add the last message
        ret.append(msg)
        return ret

    def _gen_err(self, command: str, content: str, member: discord.Member) -> discord.Embed:
        """Generator for error embeds, used throughout the bot.

        Standardizes the color and format. Takes in the message body as a whole,
        so generate this from the function that errors, or from the on_error handler
        and try to be descriptive but brief.
        Make sure to pass all important info to the user!
        """
        return discord.Embed(title=f"Error executing `{command}`!",
                             description=content,
                             colour=self.err_color,
                             author=member,
                             footer="_Making mistakes is human. Seeing this message frequently just makes you **very** human._")

    def _schedule(self, scheduler: AsyncIOScheduler=None, trigger_type: str='interval', sched_kwargs: Dict=None, callback: Callable=None, func_kwargs: Dict=None) -> Job:
        """Wrapper function to automate job scheduling all over the bot.

        If it's not an AsyncIOScheduler, we're fucked.
        This should be fine though, since all the schedulers used in the bot should
        already be AsyncIOSchedulers. If not, blame the dev.
        """
        return scheduler.add_job(func=callback, trigger=trigger_type, coalesce=True, kwargs=func_kwargs, **sched_kwargs)

    def _gen_crontab(self, h: Union[int,str], m: Union[int,str], s: Union[int,str], freq: int=3, unit="h"):
        """Generator for crontabs to be used with apscheduler. Might delete this.

        Takes an input time split by hours minutes and seconds and returns a valid
        crontab that repeats an action on every interval of frequency units.
        If units is m (minutes), freq must be in the range 15-60.
        If units is h (hours), freq must be in the range 1-24.
        Does not raise anything, just assumes user inadequacy
        """
        crontab = {'hour': None, 'minute': None, 'second': None}
        unit = unit[:1].lower()
        if not unit in ['m', 'h']:
            # User is inadequate, default to whatever will annoy them the most.
            return {'month': "*/2", 'day': 31}
        hours = []
        mins = []
        if unit == 'h':
            h = h%freq
            loop = 24/freq
            while loop > 0:
                hours.append(str(h))
                h += freq
                loop -= 1
            crontab['hour'] = ",".join(hours)
            crontab['minute'] = str(m)
        else:
            m = m%freq
            loop = 60/freq
            while loop > 0:
                mins.append(str(h))
                m += freq
                loop -= 1
            crontab['minute'] = ",".join(mins)
            crontab['hour'] = str(h)
        crontab['second'] = str(h)
        return crontab

    @Commands.group(pass_context=True, invoke_without_command=True, case_insensitive=True, cog_name="core", name="core")
    @Commands.guild_only()
    async def core(self, ctx):
        if ctx.invoked_subcommand is None:
            embedtext = f"No subcommand given, try `{ctx.prefix}help core` for more information."
            await ctx.send(embed=self._gen_err(command="Core Group", content=embedtext, member=ctx.author))

    @core.command(name="yeet", aliases=["ban"])
    @commands.has_guild_permissions(ban_members=True)
    async def yeet(self, ctx, member: discord.Member, *, reason="The mod was pissed at you"):
        await ctx.guild.ban(user=member, reason=reason)
        embed = discord.Embed(title=f"Banned {member.name}#{member.discriminator}",
                              description=f"{member.display_name} was banned from the server.\n**Reason**\n>>> {reason}",
                              colour=discord.Colour.from_rgb(172, 43, 107),
                              author=ctx.author,
                              footer=f"_Don't make the mistakes {member.name}#{member.discriminator} made_")

    @core.command(name="boot", aliases=["kick"])
    @commands.has_guild_permissions(kick_members=True)
    async def boot(self, ctx, member: discord.Member, *, reason="The mod was pissed at you"):
        await ctx.guild.kick(user=member, reason=reason)
        embed = discord.Embed(title=f"Kicked {member.name}#{member.discriminator}",
                              description=f"{member.display_name} was kicked from the server.\n**Reason**\n>>> {reason}",
                              colour=discord.Colour.from_rgb(172, 43, 107),
                              author=ctx.author,
                              footer=f"_{member.display_name} slipped up. They can come back and try again later_")

    @core.command(name="warn")
    async def warn(self, ctx, member: discord.Member):
        await ctx.message.send(f"ROFLMAO, you wanna give {member.mention} another chance at doing the same thing?\nIf it happens again, use `{ctx.prefix}boot @member`")
