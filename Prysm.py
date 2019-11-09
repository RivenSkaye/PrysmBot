#!/usr/bin/env python3

"""
A utility bot for Discord.
Current functionality is limited to
- exit() - including the steps to neatly kill the bot
- restart() - pull in updates from git and restart itself. Only works in *NIX envs
- setInit() - Send a message to the channels this was last called whenever we get back online. One channel per server.
- reminder() - send a reminder every x hours, on a cron schedule. UTC-based to prevent DST issues

- Optional Webhook spamming for RSS feeds. 
Author: RivenSkaye / FokjeM
"""
# Builtins used
import os
import subprocess
import sys
import json
import math
# Discord libraries
import discord
import discord.ext.commands
#External dependencies
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Local imports
import rss_reader
# Make sure we can find all files by having the working directory set to the bot's directory
os.chdir(sys.path[0])
# Make a list of all possible optional arguments
allowed_args = ["-rss"]
# Make a dictionary of all given arguments. That allows an arbitrary order in using them
given_args = {"-rss": False}
for arg in sys.argv:
    argset = arg.split("=")
    if argset[0] in allowed_args:
        if len(argset) > 1:
            given_args[argset[0]] = int(argset[1])
        else:
            given_args[argset[0]] = True


try:
    with open("Prysm.json", "r") as prysmjson:
        base_info = json.load(prysmjson)
        assert (len(base_info["Token"]) > 0), "No token given! Fix your Prysm.json!"
except FileNotFoundError:
    with open("Prysm.json", "w+") as prysmjson:
        prysmjson.write("{\r\n    \"Token\": \"\",\r\n    \"Guilds\": {}\r\n}")
        print("There was no Prysm.json found; It was created, now add the Token for the bot.")
    exit(1)
except AssertionError:
    print("No token given! Fix your Prysm.json!")
    exit(1)
try:
    # I assume people supplying a Prysm.json use correct keys, values and capitalization.
    # They are not immune to mistakes though, so we catch those here if they did supply a valid token. And we warn them about it.
    assert Guilds in base_info, "No Guilds object found!"
    guilds = base_info["Guilds"]
    assert isinstance(guilds, dict)
except AssertionError as e:
    print("Guilds wasn't an object, this has been fixed.\r\nMessage: %s" % e.args[0])
    base_info["Guilds"] = {};
    guilds = base_info["Guilds"]
    saveJSON("Prysm.json", base_info)

bot = discord.ext.commands.Bot(max_messages=0, fetch_offline_members=False, command_prefix=">")
scheduler = AsyncIOScheduler({'apscheduler.timezone': 'UTC'})

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="the boss", type=discord.ActivityType.listening))
    for guild in bot.guilds:
        if str(guild.id) not in guilds.keys():
            guilds[str(guild.id)] = guild.name
        if os.path.isfile(str("Guilds/"+str(guild.id)+".json")):
            with open(str("Guilds/"+str(guild.id)+".json")) as gjson:
                g = json.load(gjson)
                if "Init" in g:
                    e = discord.Embed(title="Prysm started", description="This is a message to let all users know Prysm is online and receptive for input.", colour=discord.Colour.from_rgb(172, 85, 172))
                    await bot.get_channel(g["Init"]).send(embed=e)
                if "Reminders" in g:
                    for reminder in g["Reminders"]:
                        scheduler.add_job(reminder_send, trigger='cron', args=[bot.get_channel(reminder[0]), reminder[1]], hour=reminder[2], minute=reminder[3], second=reminder[4])
    # Once the loop's done, we save all servers we're in now.
    saveJSON("Prysm.json", base_info)
    # Check if the -rss option was set and how often we should check
    if given_args["-rss"] is not False:
        hrs="*"
        if given_args["-rss"] is True: # It's default, every 5 min
            given_args["-rss"] = 5
        elif given_args["-rss"] >= 60:
            given_args["-rss"] = given_args["-rss"]%60
            hrs = "%s" % (given_args["-rss"]/60)
        mins = "*/%s" % given_args["-rss"]
        scheduler.add_job(rss_reader.rss_fetch, trigger='cron', args=[hour=hrs, minute=mins])
    # And start the scheduler
    scheduler.start()

# async def initMessage(guild, channel):
@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, discord.ext.commands.MissingPermissions):
        await ctx.channel.send("Sorry %s, it seems you lack the permission %s" % (ctx.author.mention(), err.missing_perms))
    else:
        await ctx.channel.send("Sorry, something went wrong, other than permissions.\r\nMessage: %s" % err)

@bot.command(name="setInit", help="Sets what channel to send a message signaling the bot is online. Requires the 'manage channels' permission.", pass_context=True)
@discord.ext.commands.has_permissions(manage_channels=True)
async def cmd_setInit(ctx):
    guildfile = str("Guilds/"+str(ctx.guild.id)+".json")
    if not os.path.isfile(guildfile):
        with open(guildfile, "w+") as f:
            f.write("{}")
    with open(guildfile, "r") as gf:
        channel = json.load(gf)
    channel["Init"] = ctx.channel.id
    saveJSON(guildfile, channel)
    e = discord.Embed(title="Registered Init Channel", description="This message will now be used to notify of Prysm's online status.", colour=discord.Colour.from_rgb(172, 85, 172))
    await bot.get_channel(channel["Init"]).send(embed=e)

@bot.command(name="reminder", help="Set a reminder from the specified time, every x hours, with the specified message. Calculates the reminders on a per-day basis with UTC times. Requires the 'manage channels' permission.")
@discord.ext.commands.has_permissions(manage_channels=True)
async def cmd_reminder(ctx, time: str, freq: int, msg: str, ):
    scheduler.pause()
    # Get all time components, we need this for the 'cron' scheduler
    h = int(time.split(":")[0])%freq
    m = int(time.split(":")[1])
    s = int(time.split(":")[2])
    # Create an array to hold all the hours
    hours = []
    # Calculate how mmany times this'll occur on a daily basis and shove it into the list
    loop = math.floor(24/freq)
    while loop > 0:
        hours.append(str(h))
        h += freq
        loop -= 1
    hour_str = ",".join(hours)
    # Save data for next bot instance
    guildfile = str("Guilds/"+str(ctx.guild.id)+".json")
    if not os.path.isfile(guildfile):
        with open(guildfile, "w+") as f:
            f.write("{}")
    with open(guildfile, "r") as gf:
        channel = json.load(gf)
        if "Reminders" not in channel:
            channel["Reminders"] = []
        channel["Reminders"].append([ctx.channel.id, msg, hour_str, m, s])
    saveJSON(guildfile, channel)
    # Create the job
    scheduler.add_job(reminder_send, trigger='cron', args=[ctx.channel, msg], hour=hour_str, minute=str(m), second=str(s))
    try:
        scheduler.resume()
    except:
        scheduler.start()
    e = discord.Embed(title="Reminder Added", description="Reminder created for this channel (%s).\r\nMessage: %s\r\nThis will be sent every %i hour(s) at hh:%i:%i." % (ctx.channel.name, msg, freq, m, s))
    await ctx.channel.send(embed=e)

async def reminder_send(channel, msg):
    await channel.send(msg)

@bot.command(name="restart", help="Pulls in latest git code and restarts to load it in. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_restart(ctx):
    saveJSON("Prysm.json", base_info)
    await ctx.channel.send("I'm now updating and restarting. As soon as I'm back, you can use me again!")
    subprocess.Popen(["git", "pull"]).wait()
    await bot.close()
    os.execv(sys.executable, ["python"]+sys.argv)

@bot.command(name="exit", help="Calls all closing methods on the bot, shutting it down. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_exit(ctx):
    await ctx.channel.send("Prysm off, glad to be of service!")
    await bot_exit()

async def bot_exit(status=0):
    saveJSON("Prysm.json", base_info)
    await bot.close()

def saveJSON(jsonFile, data):
    with open(jsonFile, "w") as jsonHandle:
        json.dump(data, jsonHandle, indent=4)

bot.run(base_info["Token"])
