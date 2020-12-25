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
import os
import json
import asyncio
# Discord libraries
import discord
import discord.ext.commands

def _saveJSON(jsonFile: str, data: Dict[str, Any]):
    """Utility fuction to save data to a JSON file.

    param: str jsonFile:    A file name or path for use with open()
    param: Dict data:       The data to be saved, dicts convert very easily.
    """
    with open(jsonFile, "w") as jsonHandle:
        json.dump(data, jsonHandle, indent=4)

async def split_messages(list_in, limit: int=1750) -> List:
    """Internal utility function to split messages before they get too big.
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
            ret = msg
            msg = entry
    # Make sure to add the last message
    ret.append(msg)
    return ret

async def _gen_err(command: str, content: str, member: discord.Member) -> discord.Embed:
    """Generator for error embeds, used throughout the bot.

    Standardizes the color and format. Takes in the message body as a whole,
    so generate this from the function that errors, or from the on_error handler
    and try to be descriptive but brief.
    Make sure to pass all important info to the user!
    """
    return discord.Embed(title=f"Error executing `{command}`!",
                         description=content,
                         colour=discord.Colour.from_rgb(172, 43, 43),
                         author=member,
                         footer="_Making mistakes is human. Seeing this message frequently just makes you **very** human._")

def _gen_crontab(h: Union[int,str], m: Union[int,str], s: Union[int,str], freq: int=3, unit="h"):
    """Generator for crontabs to be used with apscheduler.

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

# Create a class for the bot here, rather than a monolithic script

try:
    with open("Prysm.json", "r") as prysmjson:
        base_info = json.load(prysmjson)
        assert (len(base_info["Token"]) > 0), "No token given! Fix your Prysm.json!"
except FileNotFoundError:
    # Create the Prysm.json file manually, ensure we have working stuff.
    with open("Prysm.json", "w+") as prysmjson:
        prysmjson.write("{\n    \"Token\": \"\",\n    \"Guilds\": {}\n}")
        print("There was no Prysm.json found! It was created, now add the Token for the bot.")
    exit(1)
except AssertionError:
    print("No token given! Fix your Prysm.json!")
    exit(1)
try:
    # I assume people supplying a Prysm.json use correct keys, values and capitalization.
    # They are not immune to mistakes though, so we catch those here if they did supply a valid token. And we warn them about it.
    assert "Guilds" in base_info, "No Guilds object found!"
    assert isinstance(base_info["Guilds"], dict)
except AssertionError as e:
    print(f"Guilds wasn't an object, this has been fixed.\r\nMessage: {e}")
    base_info["Guilds"] = {};
    saveJSON("Prysm.json", base_info)
# Either we just fetched with no changes, or already saved it here
guilds = base_info["Guilds"]
# Initialize the bot and establish connection info
bot = discord.ext.commands.Bot(max_messages=0, fetch_offline_members=False, command_prefix=";")

"""
on_ready handler, this performs a set of actions when the bot successfully
    initializes and connects to Discord. No args, just run shit.
"""
@bot.event
async def on_ready():
    set_act = bot.change_presence(activity=discord.Activity(name="Riven-senpai <3", type=discord.ActivityType.listening))
    for guild in bot.guilds:
        if str(guild.id) not in guilds.keys():
            guilds[str(guild.id)] = guild.name
        if os.path.isfile(str(f"Guilds/{str(guild.id)}.json")):
            with open(str("Guilds/"+str(guild.id)+".json")) as gjson:
                g = json.load(gjson)
                if "Init" in g:
                    e = discord.Embed(title="Prysm started", description="This is a message to let all users know Prysm is online and receptive for input.\nWorking on a full rebuild, Prysm will go off immediately.", colour=discord.Colour.from_rgb(172, 85, 172))
                    await bot.get_channel(g["Init"]).send(embed=e)
    await set_act
    # Once the loop's done, we save all servers we're in now.
    saveJSON("Prysm.json", base_info)

bot.run(base_info["Token"])
