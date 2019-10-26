#!/usr/bin/env python3

"""
Dependency installer
This is an automated script that attempts to install all dependencies
that are required for Prysm.
It's quick, it's dirty, and it works so long as you run it with
an elevated command prompt (run as admin) or if you run it as root or with sudo
"""

import subprocess

dependencies = ["apscheduler"]
for dep in dependencies:
    try:
        subprocess.Popen(["pip3", "install", "-U", dep]).wait()
    except:
        print("Error installing package: %s" % dep)
print("Done installing dependencies; Please make sure you keep Prysm up to date!")
