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
import json
import discord
import discord.ext.commands

with open("Prysm.json", "r") as prysmjson:
    base_info = json.load(prysmjson)
guilds = base_info["Guilds"]
client = discord.ext.commands.Bot(max_messages=0, fetch_offline_members=False, command_prefix=";")

@client.event
async def on_ready():
    for guild in client.guilds:
        if str(guild.id) in guilds.keys():
            print("Guild found: %s" % guilds[str(guild.id)])
        else:
            print("New guild! %s" % guild.name)
            guilds[str(guild.id)] = guild.name
            print(guilds)

# async def initMessage(guild, channel):

@client.command(name="exit", help="Calls all closing methods on the bot, shutting it down. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_exit(ctx):
    await ctx.channel.send("Prysm off, glad to be of service!")
    await bot_exit(0)

async def bot_exit(status=0):
    with open("Prysm.json", "w") as prysmjson:
        json.dump(base_info, prysmjson, indent=4)
    await client.close()
    exit(status)

client.run(base_info["Token"])
