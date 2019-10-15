#An open source Discord utility bot written in Python 3.x

This is a personal use bot and isn hosted anywhere as of yet.
If hosting for multiple servers becomes a viable option, it will be offered.

##Hosting it yourself
You are required to create a file called Prysm.json that contains at least:
```
{
    "Token": "<insert your token here>",
    "Guilds": {
    }
}
```
Guilds is left intentionally blank, it'll be filled out by the bot once you add it to a few servers.

You can run this on any machine running Python 3.x
_Assuming Python 3.x is configured as the default, use `python3` otherwise_
- `pip install -U discord.py`
- `python Prysm.py`
