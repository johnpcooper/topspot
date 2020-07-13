#!/bin/bash
# Copy history from raspberry pi disk
/usr/bin/scp pi@192.168.1.11:/home/pi/venv/.topspot/lib/python3.7/site-packages/topspot/track_history_df.json /home/johnpcooper/projects/topspot/topspot/temp_history_df.json
# Merge raspberry pi history with local disk history
~/venvs/.topspot/bin/python -c "import topspot.database as db; db.merge_track_histories()"