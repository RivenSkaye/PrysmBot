# An open source Discord utility bot written in Python 3.x

This is a personal use bot and isn't hosted anywhere as of yet.
If hosting publicly becomes a viable option, it might be offered.

## Hosting it yourself
You are required to supply the token in the bare Prysm.json that's included as an untracked file in this repo.
If it gets deleted, Prysm will create a new, file with _empty_ fields.
Prysm can't and won't do anything if you haven't supplied the token.
### _You can fill in Prysm.json with the Token for your bot account to sail smoothly from first start._
It looks like this:
```json
{
    "Token": "<insert your token here>",
    "Guilds": {}
}
```
Guilds is left intentionally blank, it'll be filled out by the bot when starting and encountering new guilds/servers.

You can run this on any machine running Python 3.x

_Assuming Python 3.x and Pip 3.x are configured as the defaults, use `pip3` and `python3` otherwise_
- `pip install -U discord.py`
- `python Prysm.py`

## Dependencies
The bot has some external dependencies for certain components. These are listed here with their `pip3` names.
An install script has been provided as `dep_install.py`. It assumes `python3` and `pip3` as the executables are usually called.
On a \*NIX system, execute the script directly with `./dep_install.py`, or with whatever points to your python3 install.
On Windows, run it with the local python3 install.
### Dependencies per functionality
| Dependency  |     Functionality     |
|-------------|-----------------------|
| discord.py  | Discord bot functions |
| apscheduler | Reminder functions    |
