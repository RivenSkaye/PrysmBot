# An open source Discord utility bot written in Python 3.x #

This is a personal use bot and isn't hosted anywhere for the public, as of yet.  
If hosting for multiple servers becomes a viable option, it might be offered. Feel free to message [me]()

## Hosting it yourself ##
You are required to supply the token in the bare Prysm.json that's generated at first start.  
**Prysm can't and won't do anything if you haven't supplied the token.**
### _You can create Prysm.json in the same directory as Prysm.py with the Token and a blank Guilds object supplied to sail smoothly from first start._ ###
It looks like this:
```json
{
    "Token": "<insert your token here>",
    "Guilds": {}
}
```
Guilds is left intentionally blank, it'll be filled out by the bot when starting and encountering new guilds/servers.

You can run this on any machine running Python 3.x  
This bot does not and will not log anything. If you want that, output stdout and stderr to a file.
- Any POSIX-compliant CLI: `python Prysm.py >> err.log 2>&1`.
- Newer versions of Bash may also use `python Prysm.py &> err.log`
- I don't explicitly support other shells. Open a PR or an Issue and _offer instructions to add_.

_Assuming Python 3.x and Pip 3.x are configured as the defaults, use `pip3` and `python3` otherwise._
- `pip3 install -U discord.py`
- `python Prysm.py`

## Dependencies ##
The bot has some external dependencies for certain components. These are listed here with their `pip3` names.  
An install script has been provided as `dep_install.py`. It assumes `python3` and `pip3` as the executables are usually called.  
On a \*NIX system, execute the script directly with `./dep_install.py`, or with whatever points to your python3 install.  
On Windows, run it with the local python3 install.
### Dependencies per functionality ###
General functioning of any Discord bot:
- discord.py

For the reminder functionality:
- apscheduler

## Optional modules ##
The bot will have several optional modules that can be _activated_ by passing the corresponding arguments on initialization.  
This will list the dependencies, for what module and with what options.
- Feedparser for the rss module. Pass `-rss`
#### RSS module
The RSS module takes existing Webhooks and assigns a listener for RSS feeds to it. The host needs to supply the data!  
You can send multiple feeds to the same Webhook, but you can't send one feed to multiple Webhooks as this would require either inefficient code or way too much effort.  
It requires a JSON file to specify what feed goes with what webhook. Like the Prysm.json, the bot will make this itself if it has to.
```json
{
    "<RSS URL>": "<Webhook URL>"
}
```
