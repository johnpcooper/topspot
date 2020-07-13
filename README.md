# topspot

This project is developed in the Windows subsystem for Linux, so there are some quirks specific to the WSL in these docs. Making it work in Windows is straightforward.

## Windows installation

```sh
cd C:\
git clone https://github.com/johnpcooper/topspot
cd topspot
```

Before installing the package, you need to get credentials configured with spotify and add them to `topspot\constants.py`:

1.  Create a spotify app on the [spotify developer dashboard](https://developer.spotify.com/dashboard/applications).
2. Get your client ID and client secret from the dashboard page
3. set up a redirect URI in dashboard page > edit settings. I recommend using the one that's already in `topspot/constants_example.py`
4. Change the name of `topspot/constants_example.py` to `topspot/constants.py` after adding the above information. Should look like this (minus `package_path` definition which doesn't need to be changed):

```python
env_vars = {'SPOTIPY_CLIENT_ID': '<your-spotify-client-id>',
            'SPOTIPY_CLIENT_SECRET': '<your-spotify-client-secret>',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:9090', 
            'DISPLAY': ':0'}

scope_list = ['user-modify-playback-state',
              'user-read-recently-played',
              'user-read-playback-state',
              'playlist-read-private',
              'playlist-read-collaborative',
              'user-read-currently-playing',
              'playlist-modify-private',
              'playlist-modify-public',
              'user-top-read',
              'user-read-playback-position']
scope = " ".join(scope_list)


user_vars = {'username': 'anothergriningsoul',
             'playlist_db_path': f'{package_path}playlists_db.csv',
             'playlist_df_path': f'{package_path}playlists_df.csv',
             'cache_path': f'{package_path}.usercache',
             'track_history_path': f'{package_path}track_history_df.json',
             'temp_history_path': f'{package_path}temp_history_df.json'}
```

Now that `constants.py` is properly configured, you can install `topspot` and then use .ahk shortcuts:

```sh
pip install virtualenv
# Create a virtual environment in which to install the package. You could also
# just install it outside of a venv, but you'll need to remove the environment activation part of the ahk functions
cd C:\
python -m venv .spotify
.spotify\Scripts\activate
cd topspot
pip install -r requirements.txt
# Install the package in .spotify venv
python setup.py install
```

## Running Tkinter in the windows subsystem for linux

It was pretty annoying to make tkinter work in the WSL, but I wanted tkinter for a more universal form of OS clipboard access. You must install tkinter with the following:

```sh
$ sudo apt-get update
$ sudo apt-get install python3-tk
```

Then in order to get the tkinter root object (`Tk`), you need to install [Ximing X server for Windows](https://virtualizationreview.com/articles/2017/02/08/graphical-programs-on-windows-subsystem-on-linux.aspx) explained in this [tutorial](https://virtualizationreview.com/articles/2017/02/08/graphical-programs-on-windows-subsystem-on-linux.aspx).

## Playback history collection

### Listen to playback with raspberry pi

I use my raspberry pi to run `database.update_track_history()` every 5 minutes with `cron`:

```sh
# bash command to edit your sudo crontab tasks
sudo crontab -e
# Add the following commands to the end of the file
# First, update track history at reboot. Note that
# You don't have to activate the venv if you just
# interpret the python command with the python.exe
# in that venv
@reboot ~/venv/.topspot/bin/python -c "from topspot.database import updated_track_history; update_track_history()"
# Then, update every five minutes
*/5 * * * * ~/venv/.spotify/bin/python -c "from topspot.database import updated_track_history; update_track_history()"
```

This writes last 50 tracks of playback history to `<constants.package_path>track_history_df.json`

### Merge playback history with main `topspot` source on WSL

I use this bash script to run `scp` on my WSL to copy `<constants.package_path>/track_history_df.json` (which gets updated every x minutes with `cron`) from raspberry pi into `<constants.package_path/temp_history_df.json>` in my WSL. Then I merge that temporary history `DataFrame` with the WSL `database.track_history_df()` copy:

```sh
# script at constants.package_path/bash/update_sp_data.sh:

# Copy history from raspberry pi disk
/usr/bin/scp <username@<ip>:/home/pi/venv/.topspot/lib/python3.7/site-packages/topspot/track_history_df.json /home/john
pcooper/projects/topspot/topspot/temp_history_df.json
# Merge raspberry pi history with local disk history
~/venvs/.topspot/bin/python -c "import topspot.database as db; db.merge_track_histories()"
```

**You'll need to set up public `ssh` keys for each of your two devices and put them in each other's `~/.ssh/authorized_keys` files**. This is good resource for setting up [`ssh` on your WSL](https://www.illuminiastudios.com/dev-diaries/ssh-on-windows-subsystem-for-linux/) and this is a good resource for using [`scp` on linux-based OS](https://help.ubuntu.com/community/SSH/TransferFiles)

### Running SFTP/SCP commands on raspberry pi

I used to use `scp` to automatically transfer the updated copy of `track_history_df.json` to the location of my main `topspot` source in my WSL. However, the **raspberry pi tends to freeze when copying files from its disk using SFTP/SCP** to other machines. So now I run scp from WSL to get files from raspberry pi as described above. 

First, the bash script for copying the file located at `/home/pi/scripts/update_sp_data.sh`:

```sh
# Direct path to scp + <constants.packge_path>/track_history_df.json
# + destination on my WSL
/usr/bin/scp /home/pi/venv/.spotify/lib/python3.7/site-packages/topspot/track_history_df.json <username>@<computer_name>:/home/johnpcooper/projects/topspot/topspot
```

And then the `cron` command that runs the bash script every 5 minutes:

```sh
# Important that you put this command is the user crontab.
# Your ssh key won't be available in the root environment
crontab -e # open the crontab file
# Put this line at the end
*/5 * * * * /bin/bash /home/pi/scripts/update_sp_data.sh
```
