#!/bin/bash
# Copy user cache to raspberry pi topspot installation location (ignored in repo)
/usr/bin/scp /home/johnpcooper/projects/topspot/topspot/.usercache pi@192.168.1.11:/home/pi/venv/.topspot/lib/python3.7/site-packages/topspot
# Copy constants.py to raspberry pi topspot installation location (ignored in repo)
/usr/bin/scp /home/johnpcooper/projects/topspot/topspot/constants.py pi@192.168.1.11:/home/pi/venv/.topspot/lib/python3.7/site-packages/topspot
#echo "Pushed spotify credentials to raspberry pi"