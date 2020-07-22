import re
from datetime import datetime
from calendar import month_name
from topspot.secrets import secrets

def package_path(**kwargs):
    """
    Return the path to the local installation
    of topspot
    """
    import topspot
    file = topspot.__file__
    try: # this will work on linux based OS
        end = file.rindex('/')
    except ValueError: # this will work on windows
        end = file.rindex('\\')
    package_path = file[:end+1]
    
    return package_path
    
package_path = package_path()

env_vars = {'SPOTIPY_CLIENT_ID': secrets.client_id,
            'SPOTIPY_CLIENT_SECRET': secrets.client_secret,
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
             'playlist_db_path': f'{package_path}playlists_db.json',
             'playlist_df_path': f'{package_path}playlists_df.json',
             'cache_path': f'{package_path}.usercache',
             'track_history_path': f'{package_path}track_history_df.json',
             'temp_history_path': f'{package_path}temp_history_df.json'}

class Patterns(object):
    """
    Where I'm storing conventions for naming various
    different types of playlists as regex patterns
    """
    def __init__(self):

        self.singles_playlists = self.get_singles_playlists()
        self.bestofyear_playlists = self.get_bestofyear_playlists()

    def get_singles_playlists(self):
        """
        Return the pattern the pattern used
        for naming monthly singles playlists
        """
        centuries = '|'.join([str(num) for num in range(19, 22)])
        decades_years = '|'.join([str(num) for num in range(0, 100)])
        months = '|'.join(month_name[1:13])

        pattern = f'({centuries})({decades_years}) ({months})'
        return pattern

    def get_bestofyear_playlists(self):
        """
        Return the pattern the pattern used
        for naming favorite songs of the year
        playlists
        """
        centuries = '|'.join([str(num) for num in range(19, 22)])
        decades_years = '|'.join([str(num) for num in range(0, 100)])
        suffix = 'Trp2it'

        pattern = f'({centuries})({decades_years}) {suffix}'
        return pattern

patterns = Patterns()