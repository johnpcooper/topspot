from datetime import datetime, timedelta
from dateutil.parser import parse

import pandas as pd
import numpy as np

from topspot import utilities, playlist

def artist_names(track_dict):
    # best to get track_dict from get_playlist_tracks()[i]
    artists = track_dict['artists']
    names = [artist['name'] for artist in artists]
    
    return names

def artist_ids(track_dict):
    artists = track_dict['artists']
    ids = [artist['id'] for artist in artists]
    
    return ids

def release_date(track_dict):
    """
    Return the release date of the album containing
    the track matching track_uri
    """
    try:
        release_date = track_dict['album']['release_date']
    except:
        release_date = None
        print("Failed to find release date for this track")
        try:
            print(f"track_name: {track_dict['name']}")
        except:
            pass
        
    return release_date

def recently_played(**kwargs):
    """
    Return the list of track_dicts for the 50
    (limited by spotify) tracks for the user.

    Adds 'played_at' item to track_dict as a datetime
    object in central timezone
    """
    sp = kwargs.get('sp', utilities.get_user_sp())
    
    recently_played = sp.current_user_recently_played(limit=50)['items']
    track_dicts = []
    for item in recently_played:
        played_at = item['played_at']
        played_at_dt = parse(played_at)
        played_at_central_dt = played_at_dt - timedelta(hours=5)
        # Get rid of timezone awareness because it
        # simplifies things downstream
        played_at_central_dt = played_at_central_dt.replace(tzinfo=None)
        track = item['track']
        track['played_at'] = played_at_central_dt
        
        track_dicts.append(track)

    return track_dicts

def tracks_df(**kwargs):
    """
    Return a dataframe made from the tracks_dict passed
    as a kwarg. If no tracks_dict kwarg, make a df 
    containing the 50 most recently played tracks.

    Recently played df inlcudes datetime obj of when song
    was played in central timezone.

    At some point
    """
    track_dicts = kwargs.get('track_dicts', recently_played())
    allkeys = kwargs.get('allkeys', False)
    keys = kwargs.get('fields', ['name', 'uri',
                                 'id', 'artist_name',
                                 'artist_id', 'release_date'])
    
    columns_dict = {}    
    track_dfs = []
    for i, track_dict in enumerate(track_dicts):
        # Add some custom extracted fields. 
        track_dict['artist_name'] = '|'.join(artist_names(track_dict))
        track_dict['artist_id'] = '|'.join(artist_ids(track_dict))
        track_dict['release_date'] = release_date(track_dict)
        if allkeys:
            for key in track_dict.keys():
                columns_dict[key] = track_dict[key]
            try:
                track_df = pd.DataFrame(columns_dict, index=[i])
                track_dfs.append(track_df)
            except:
                pass
        else:
            # Only get keys from shorter list above
            for key in keys:
                columns_dict[key] = track_dict[key]
            # If, as is the default, tracks_dict comes from
            # track.recently_played() then each track_dict will
            # have an 'added_at' key
            try:
                # Coerce played_at into np.datetime64. This is the standard
                # dtype for pandas DataFrames cells with datetime objects
                columns_dict['played_at'] = np.datetime64(track_dict['played_at'])
            except:
                pass
            track_df = pd.DataFrame(columns_dict, index=[i])
            track_dfs.append(track_df)

    tracks_df = pd.concat(track_dfs)
    
    return tracks_df