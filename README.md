# An open source Discord utility bot written in Python 3.x #
This is a personal use bot and isn't hosted anywhere for the public, as of yet.  
If hosting for multiple servers becomes a viable option, it might be offered. Feel free to message [me]()

## Hosting it yourself ##
You are required to supply the token in the bare Prysm.json that's generated at first start.  
**Prysm can't and won't do anything if you haven't supplied the token.**
You are required to supply the token in the bare Prysm.json that's included as an untracked file in this repo.
If it gets deleted, Prysm will create a new, file with _empty_ fields.
Prysm can't and won't do anything if you haven't supplied the token.
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
**Due to how python/pip works, it requires an elevated environment to run on at least Windows** (not tested on \*NIX-like)
### Dependencies per functionality ###
General functioning of any Discord bot:
- discord.py

For the reminder functionality:
- apscheduler

## Optional modules ##
The bot will have several optional modules that can be _activated_ by passing the filename as arguments on initialization.  
This will list the dependencies, for what module and with what options.
These modules come with their own dependency installers. Run these the same as the base dependency handler.

### RSS module ###
The RSS module takes existing Webhooks and assigns a listener for RSS feeds to it. The host needs to supply the data!  
You can send multiple feeds to the same Webhook, but you can't send one feed to multiple Webhooks as this would require either inefficient code or way too much effort.  
It requires a JSON file to specify what feed goes with what webhook. Like the Prysm.json, the bot will make this itself if it finds none.
```json
{
    "<RSS URL>": "<Webhook URL>"
}
```
Activate the module passing the argument `rss`.
To set a specific time between two polls on an RSS feed, set a value in minutes. E.g.: `python3 Prysm.py rss=180`.
Schedules using the cron trigger for apscheduler, meaning that it runs at predefined _times_. Default is every 5 minutes from the start of an hour.

### Dependencies per functionality
| Dependency  |     Functionality     |
|-------------|-----------------------|
| discord.py  | Discord bot functions |
| apscheduler | Reminder functions    |

| Dependency  | Per module            |
|-------------|-----------------------|
| feedparser  | RSS Module            |
| requests    | RSS Module            |
|python-dateutil| RSS Module          |
