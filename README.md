# An open source Discord utility bot written in Python 3.x #
This is a personal use bot and isn't hosted anywhere for the public, as of yet.  
If hosting for multiple servers becomes a viable option, it might be offered.

For questions, problems, tips or being social, feel free to drop by [in Prysm's home server](https://discord.gg/7sFRUtH)

## Hosting it yourself ##
Make sure you have a Discord account and a bot token from the [Developer Portal](https://discord.com/developers/applications),
you'll need it for the bot to run.  
You are required to supply the token in the bare Prysm.json that's included as an untracked file in this repo.  
This might be changed because a fork won't have it untracked.

If it gets deleted, Prysm will create a new file with _empty_ fields. Re-add the token there.  
_You can create Prysm.json yourself in the same directory as Prysm.py with the Token and a blank Guilds object supplied to sail smoothly from first start._
```json
{
    "Token": "<insert your token here>",
    "Guilds": {}
}
```

You can run this on any machine running Python 3.x, but it's developed and maintained for 3.8, no guarantees for other versions.  
This bot does not and will not log anything. If you want that, output stdout and stderr to a file.
- Any POSIX-compliant CLI: `python Prysm.py >> err.log 2>&1`.
- Newer versions of Bash may also use `python Prysm.py &> err.log`
- I don't explicitly support other shells. Open a PR or an [issue](https://github.com/FokjeM/PrysmBot/issues/new) and _offer instructions to add to this list_.

_Running the core functions of the bot (assuming requirements are met)_
- `python38 -m pip install -U discord.py`
- `python38 Prysm.py`

## Dependencies ##
The bot has some external dependencies for certain components. These are listed here with their `pip3` names.  
An install script has been provided as `dep_install.py`.
### Dependencies per functionality ###
General functioning of any Discord bot:
- discord.py

For the reminder functionality:
- apscheduler

## Optional modules ##
These won't exist for long, imma replace this stuff  
The bot will have several optional modules that can be _activated_ by passing the filename as arguments on initialization.
This will list the dependencies, for what module and with what options.  
These modules come with their own dependency installers. Run these the same as the base dependency handler.

### RSS module ###
The RSS module takes existing Webhooks and assigns a listener for RSS feeds to it. The host needs to supply the data!
The structure between webhooks and feeds is being fixed, at a small archival expense.
Activate the module passing the argument `rss`.
To set a specific time between two polls on an RSS feed, set a value in minutes. E.g.: `python38 Prysm.py rss=180`.  
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
