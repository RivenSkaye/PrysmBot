#!/usr/bin/env python3

"""This will get replaced by a proper requirements.txt in the near future

Dependency installer
This is an automated script that attempts to install all dependencies
that are required for Prysm's rss_reader module.
It's quick, it's dirty, and it works so long as you run it with
an elevated command prompt (run as admin) or if you run it as root or with sudo
"""

import subprocess

dependencies = ["feedparser", "aiohttp"]
for dep in dependencies:
    try:
        subprocess.Popen(["python38", "-m", "pip", "install", "-U", dep]).wait()
    except Exception as e:
        print("Error installing package: %s\n\tMessage: %s" % (dep, e))
print("Done installing dependencies; Please make sure you keep Prysm up to date!")
