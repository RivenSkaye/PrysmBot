#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Prysm.py
#
#  Copyright 2019  Riven Skaye / FokjeM
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import os
import subprocess
import sys
import json
import discord
import discord.ext.commands

try :
    with open("Prysm.json", "r") as prysmjson:
        base_info = json.load(prysmjson)
        assert (len(str(base_info["Token"])) < 1), "No token given! Fix your Prysm.json!"
except FileNotFoundError:
    with open("Prysm.json", "w+") as prysmjson:
        prysmjson.write("{\r\n    \"Token\": \"\",\r\n    \"Guilds\": {}\r\n}")
        print("There was no Prysm.py found; It was created, now add the Token for the bot.")
    exit(1)
except AssertionError:
    print("No token given! Fix your Prysm.json!")
    exit(1)

guilds = base_info["Guilds"]
bot = discord.ext.commands.Bot(max_messages=0, fetch_offline_members=False, command_prefix=";")

@bot.event
async def on_ready():
    bot.change_presence(name="to the boss", type=discord.ActivityType.listening)
    for guild in bot.guilds:
        if str(guild.id) in guilds.keys():
            print("Guild found: %s" % guilds[str(guild.id)])
        else:
            print("New guild! %s" % guild.name)
            guilds[str(guild.id)] = guild.name
            print(guilds)
        if os.isfile(str("Gulds/"+guild.id+".json")):
            with open(str("Guilds/"+guild.id+".json")) as gjson:
                g = json.load(g.json)
                e = discord.Embed(title="Prysm started", description="This is a message to let all users know Prysm is online and receptive for input.", colour=discord.Colour.from_rgb(172, 85, 172))
                await bot.send_message(bot.get_channel(g["Init"]), embed=e)
    # Once the loop's done, we save all servers we're in now.
    saveJSON("Prysm.json", base_info)

# async def initMessage(guild, channel):
@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, discord.ext.commands.MissingPermissions):
        await ctx.channel.send("Sorry %s, it seems you lack the permission %s" % (ctx.author.mention(), err.missing_perms))

@bot.command(name="setInit", help="Sets what channel to send a message signaling the bot is online. Requires the 'manage channels' permission.", pass_context=True)
@discord.ext.commands.has_permissions(manage_channels=True)
async def cmd_setInit(ctx):
    channeljson = open(str("Guilds/"+ctx.guild.id+".json"), "r+")
    channel = json.load(channeljson)
    channel["Init"] = ctx.channel.id
    saveJSON(str("Guilds/"+ctx.guild.id+".json"), channel)
    e = discord.Embed(title="Registered Init Channel", description="This message will now be used to notify of Prysm's online status.", colour=discord.Colour.from_rgb(172, 85, 172))
    await bot.send_message(bot.get_channel(channel["Init"]), embed=e)

@bot.command(name="restart", help="Pulls in latest git code and restarts to load it in. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_restart(ctx):
    saveJSON("Prysm.json", base_info)
    p = subprocess.Popen(["git", "pull"])
    await ctx.channel.send("I'm now updating and restarting. As soon as I'm back, you can use me again!")
    p.wait()
    os.execv(sys.executable, ["python"]+sys.argv)

@bot.command(name="exit", help="Calls all closing methods on the bot, shutting it down. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_exit(ctx):
    await ctx.channel.send("Prysm off, glad to be of service!")
    await bot_exit(0)

async def bot_exit(status=0):
    saveJSON("Prysm.json", base_info)
    await bot.close()
    exit(status)

def saveJSON(jsonFile, data):
    with open(jsonFile, "w") as jsonHandle:
        json.dump(data, jsonHandle, indent=4)

bot.run(base_info["Token"])
