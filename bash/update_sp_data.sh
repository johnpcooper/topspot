PI_READPATH=$"pi@192.168.1.11:/home/pi/venv/.topspot/lib/python3.7/site-packages/topspot/track_history_df.json"
WSL_WRITEPATH=$"/root/venvs/.topspot/lib/python3.8/site-packages/topspot-2.0.0-py3.8.egg/topspot/temp_history_df.json"
# Listening at port 22, copy raspberry pi track_history_df tino
# temp_history_df .json file in WSL topspot installation directory
scp -P 22 $PI_READPATH $WSL_WRITEPATH

# Add new tracks from listening history just copied over from the raspberry pi
# to the local WSL track_history_df .json 
/root/venvs/.topspot/bin/python -c "import topspot.database as db; db.merge_track_histories()"