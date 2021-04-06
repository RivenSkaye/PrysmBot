# EOL and Deprecation #
Prysm had a good run as a testing grounds for me, but it was mostly just for me to poke around in discord.py to get the hang of what I'm doing.
That said, I do plan to take what I've learned from this to a new bot project that I plan to actually develop. Except this time I'm doing it
from the ground up and with the proper way of handling it from the start.

Trying to port over the monolithic eternally running script to a class-based bot proved too annoying, especially since it didn't really work the way
I'd wanted it to from the start and everything was a bit sluggish and massive. So I'm creating a new bot, Zwei.
I'll edit in a link later on when I get started.

Zwei will have the functions I envisioned Prysm would have, but with an identity and a clean start that will allow me to focus on the important
bits and pieces. Namely the code, an actual database to back things and an organized structure to work on.
I will make sure all local changes (working or not) get pushed to the dev branch so you can see why I've decided a clean start is better.

## Main features for Zwei ##
- Basic management like:
    - A three-and-five-strike warning system. (Kick on the 3rd warn, ban on the 5th. If a user is re-added within a month, ban on every next as well)
    - Channel locking
    - Channel creation
    - Muting of users
    - Nickname changing
    - Mute, Deafen and Move people in voice chats
- GIF reactions, such as hugs and slaps. Basic stuff to convey how you feel with the power of anime gifs
- Custom embed messages
    - Later edits may be added sometime, but it's not exactly planned
    - Easy to use syntax
    - Generator tool might be provided as well
- Welcome/greet messages
- Goodbye messages
- Subscribe to RSS feeds
    - These will be fetched at set intervals
    - The feeds will be saved in a global list so all servers recieve updates at the same time
    - Select fields from the RSS feed to be notified of
    - Sane defaults
- Purge command (with a cooldown)

_This list is just a preview, more stuff may be added._

## Thanks to everyone who helped get Prysm and my basics for Discord bots started! ##

# An open source Discord utility bot written in Python 3.x #
This is a personal use bot and isn't hosted anywhere for the public, as of yet.  
If hosting for multiple servers becomes a viable option, it might be offered.

For questions, problems, tips or being social, feel free to drop by [in Prysm's home server](https://discord.gg/7sFRUtH)  
~~we have a waifu roulette~~

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
- I don't explicitly support other shells. Open a PR or an [issue](https://github.com/FokjeM/PrysmBot/issues/new) and _offer instructions to add_.

_Assuming Python 3.x and Pip 3.x are configured as the defaults, use `pip3` and `python3` otherwise._
- `pip install -U discord.py`
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
