# An open source Discord utility bot written in Python 3.x

This is a personal use bot and isn't hosted anywhere as of yet.
If hosting for multiple servers becomes a viable option, it might be offered.

## Hosting it yourself
You are required to supply the token in the bare Prysm.json that's generated at first start.
Prysm can't and won't do anything if you haven't supplied the token.
### _You can create Prysm.json in the same directory as Prysm.py with the Token supplied to sail smoothly from first start._
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
