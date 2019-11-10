#!/usr/bin/env python3

"""
Dependency installer
This is an automated script that attempts to install all dependencies
that are required for Prysm's rss_reader module.
It's quick, it's dirty, and it works so long as you run it with
an elevated command prompt (run as admin) or if you run it as root or with sudo
"""

import subprocess

dependencies = ["feedparser", "requests", "python-dateutil"]
for dep in dependencies:
    try:
        subprocess.Popen(["pip3", "install", "-U", dep]).wait()
    except Exception as e:
        print("Error installing package: %s\r\n\tMessage: %s" % (dep, e))
print("Done installing dependencies; Please make sure you keep Prysm up to date!")