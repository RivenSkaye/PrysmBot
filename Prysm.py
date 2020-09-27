#!/usr/bin/env python3

"""
A utility bot for Discord.
Functionality is currently very limited.
Please forgive me as I expand the bot.

Author: RivenSkaye / FokjeM
"""
from typing import Dict, List, Any
import os
import subprocess
import sys
import json
import math
import importlib
# Discord libraries
import discord
import discord.ext.commands

"""
Utility fuction to save data to a JSON file.
Mostly used to not duplicate lines of code all over.

param: str jsonFile:    A file name or path for use with open()
param: Dict data:        The data to be saved, dicts convert very easily.
"""
def saveJSON(jsonFile: str, data: Dict[str, Any]):
    with open(jsonFile, "w") as jsonHandle:
        json.dump(data, jsonHandle, indent=4)

try:
    with open("Prysm.json", "r") as prysmjson:
        base_info = json.load(prysmjson)
        assert (len(base_info["Token"]) > 0), "No token given! Fix your Prysm.json!"
except FileNotFoundError:
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
        if os.path.isfile(str("Guilds/"+str(guild.id)+".json")):
            with open(str("Guilds/"+str(guild.id)+".json")) as gjson:
                g = json.load(gjson)
                if "Init" in g:
                    e = discord.Embed(title="Prysm started", description="This is a message to let all users know Prysm is online and receptive for input.\nWorking on a full rebuild, Prysm will go off immediately.", colour=discord.Colour.from_rgb(172, 85, 172))
                    await bot.get_channel(g["Init"]).send(embed=e)
    await set_act
    # Once the loop's done, we save all servers we're in now.
    saveJSON("Prysm.json", base_info)

bot.run(base_info["Token"])
