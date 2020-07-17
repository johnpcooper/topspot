import pandas as pd
from topspot import playback, utilities, constants, artist, track
from importlib import reload
from datetime import datetime, timedelta
import calendar
from textwrap import dedent

def database(**kwargs):
    """
    Return the dataframe containing a database
    of playlists in the user's library

    If no file found at path, return None
    """
    path = kwargs.get('path', constants.user_vars['playlist_db_path'])
    try:
        db = pd.read_csv(path)
    except FileNotFoundError:
        db = None
        print(f'No file at path: {path}')
        if kwargs.get('path') == None:
            print(dedent("""\
                   Either create a refreshed database using playlist.update_database()
                   or update the value of constants.user_vars['playlist_db_path'] to refer to
                   a file that exists
                   """))
        else:
            print(dedent("""\
                   Pass an existing path keyword argument
                   """))
        
    return db

def dataframe(**kwargs):
    """
    Return the dataframe of user playlists where each row 
    is a track, include release date, first artist name, etc.

    If no file found at path, return None
    """
    path = kwargs.get('path', constants.user_vars['playlist_df_path'])
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        df = None
        print(f'No file at path: {path}')
        if kwargs.get('path') == None:
            print(dedent("""\
                   Create a refreshed dataframe using playlist.make_playlists_df()
                   which will save the outputt at constants.user_vars['playlist_df_path']
                   """))
        else:
            print(dedent("""\
                   Pass an existing path keyword argument
                   """))
        
    return df

def get_playlist(playlist_id='7Gr9kNeQNwapj3KYaAIhCu', **kwargs):
    """
    Return playlist (a dictionary). playlist_id can be looked up by name
    in in the DataFrame returned by playlist.database()

    This function does instantiate a user spotipy object (utilities.get_user_sp())
    """
    sp = kwargs.get('sp', utilities.get_user_sp())
    try:
        playlist = sp.playlist(playlist_id, fields="tracks,next")
    except Exception as e:
        playlist = None
        print(f"Couldn't find playlist with id: {playlist_id}\nSpotipy error:\n{e}")
        print(f'You can look up playlist ids in playlist.database()')
    
    return playlist


def get_playlist_tracks(playlist_id='7Gr9kNeQNwapj3KYaAIhCu', **kwargs):
    """
    Return a list of dictionaries, one for each track in the playlist 
    found using <playlist_id>.
    
    Keys of each dict are 'name' for track name, etc:    
    
    dict_keys(['album', 'artists', 'available_markets', 'disc_number', 'duration_ms',
               'episode', 'explicit', 'external_ids', 'external_urls', 'href', 'id',
               'is_local', 'name', 'popularity', 'preview_url', 'track', 'track_number',
               'type', 'uri'])
    """
    results = get_playlist(playlist_id)
    # I'm limited to only grabbing up to 100 tracks from the playlist
    tracks = results['tracks']
    tracks_list = [tracks['items'][i]['track'] for i in range(len(tracks['items']))]
    
    return tracks_list



def make_playlist_tracks_df(playlist_id='7Gr9kNeQNwapj3KYaAIhCu', allkeys=False, **kwargs):
    # need to add functinality to get song release date and my add date
    # to make_playlist_tracks_df()
    keys = kwargs.get('fields', ['name', 'uri',
                                 'id', 'artist_name',
                                 'artist_id', 'release_date'])
    tracks_list = get_playlist_tracks(playlist_id)
    columns_dict = {}
    
    track_dfs = []
    for i, track_dict in enumerate(tracks_list):
        # Add some custom extracted fields. Sometimes 
        track_dict['artist_name'] = track.artist_names(track_dict)[0]
        track_dict['artist_id'] = track.artist_ids(track_dict)[0]
        track_dict['release_date'] = track.release_date(track_dict)
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
            track_df = pd.DataFrame(columns_dict, index=[i])
            track_dfs.append(track_df)

    tracks_df = pd.concat(track_dfs)
    
    return tracks_df

def get_playlists_from_db():
    """
    Return a list of playlist objects returned by sp.playlist(<playlist_id>)
    for each playlist_id in playlist.database()
    """
    sp = utilities.get_user_sp()
    db = database()
    playlist_ids = db.id
    playlists = [sp.playlist(plid) for plid in playlist_ids]
    print(f"Found {len(playlists)} playlists")
    
    return playlists

def make_playlists_df():
    
    sp = utilities.get_user_sp()
    username = constants.user_vars['username']
    playlists = get_playlists_from_db()
    playlist_dfs = []

    keys = ['name',
            'uri',
            'id']
    
    for i, playlist_dict in enumerate(playlists):
        print(f"Making playlist DataFrame {i+1} of {len(playlists)}", end='\r')
        columns_dict = {}
        for key in keys:
            columns_dict[key] = playlist_dict[key]
            if key == 'id':
                tracks_df = make_playlist_tracks_df(playlist_id=playlist_dict[key], sp=sp)
                # need to add functinality to get song release date and my add date
                # to make_playlist_tracks_df()
                for col in tracks_df.columns:
                    columns_dict[f'track_{col}'] = tracks_df.loc[:, col]
                    
        playlist_df = pd.DataFrame(columns_dict)
        playlist_dfs.append(playlist_df)

    playlists_df = pd.concat(playlist_dfs)
    playlists_df.to_csv(constants.user_vars['playlist_df_path'], index=False)
    
    return playlists_df

def make_playlists_db():
    
    sp = utilities.get_user_sp()
    username = constants.user_vars['username']
    playlists = sp.user_playlists(username, limit=50)
    playlist_dfs = []

    keys = ['name',
            'uri',
            'id']
    
    for i, playlist_dict in enumerate(playlists['items']):
        columns_dict = {}
        for key in keys:
            columns_dict[key] = playlist_dict[key]                    
        playlist_df = pd.DataFrame(columns_dict, index=[i])
        playlist_dfs.append(playlist_df)

    playlists_df = pd.concat(playlist_dfs)
    
    return playlists_df

def update_database():
    """
    Refresh the playlist database .csv. 
    Check topspot.constants.user_vars['playlist_db_path'] and make sure
    there is an existing .csv at that path
    """
    path = constants.user_vars['playlist_db_path']
    new_db = make_playlists_db()
    old_db = database()
    # Check if there's a .csv at the path. If not,
    # just create an empty one with the same cols
    # as the new database
    try:   
        # Get information for playlists in the new
        # database that aren't already in the pre-existing one
        new_db = new_db[~new_db.id.isin(old_db.id)]
        final_db = pd.concat([old_db, new_db], ignore_index=True)
        # Save the updated database
        final_db.to_csv(path, index=False)
    except:        
        old_db = pd.DataFrame(columns=new_db.columns)
        old_db.to_csv(path, index=False)

def get_playlist_by_name(playlist_name='2020 June'):
    """
    Look up playlist_name in playlist.database() to get id.
    Get playlist with playlist.get_playlist(id)
    
    get_playlist() returns None if no playlist found
    """
    db = database()
    if playlist_name not in db.name.values:
        print(f"'{playlist_name}' not recorded in playlist.database()")
        return None
    playlist_id = db.set_index('name').loc[playlist_name, 'id']
    playlist = get_playlist(playlist_id=playlist_id)
    
    return playlist

def new_playlist(**kwargs):
    """
    Create an empty playlist and add it to playlist.database()
    using playlist.update_database(). If playlist_name is already
    in the database, warn the user, return None and don't make a
    new playlist.
    """
    username = kwargs.get('username', constants.user_vars['username'])
    now = datetime.now()
    name = kwargs.get('name', f'Playlist {now.year}{now.month}{now.day}')
    public = kwargs.get('public', False)
    sp = utilities.get_user_sp()
    db = database()    
    # The playlist will have been create at the top
    # of playlist organization, so update_datebase()
    # will find it and add it to the database
    if name in db.name.values:
        print(f'Playlist already exists with name: {name}')
        return None
    else:
        # user_playlist_create() returns the playlist dict 
        # object
        new_pl = sp.user_playlist_create(username, name, public)
        update_database()
        return new_pl

def n_tracks(playlist_id, **kwargs):
    sp = kwargs.get('sp', utilities.get_user_sp())
    user = constants.user_vars['username']
    pl = sp.user_playlist(user=user, playlist_id=playlist_id)
    track_items = pl['tracks']['items']
    existing_ids = [track_item['track']['id'] for track_item in track_items]
    n = len(existing_ids)
    return n

def add_track_to_playlist(track, playlist_name, **kwargs):
    """
    Look up the playlist id corresponding to playlist_name
    in the dataframe returned by database() and add track
    to that playlist.
    
    This function won't add track to playlist if track is
    already on that playlist.
    """
    assert type(track) == dict, "track must be a dictionary"
    db = database()
    sp = kwargs.get('sp', utilities.get_user_sp())
    # If the sp object was passed as a kwarg, we need to make
    # sure it isn't expired
    try:
        sp.user(constants.user_vars['username'])
    except:
        sp = utilities.get_user_sp()
    user = constants.user_vars['username']
    # Need to update so that if playlist_name not in db.name.values,
    # create a new playlist with that track using playlist.new_playlist()
    # which will add the new playlist's information to playlist.database(). 
    assert playlist_name in db.name.values, "playlist name not recorded in playlist.database()"
    # Check if the track is already on the playlist. If so, don't add it
    # and let the user know
    playlist_id = db.set_index('name').loc[playlist_name, 'id']
    # Get the playlist spotify object so we can check whether the
    # track is already in the playlist
    pl = sp.user_playlist(user=user, playlist_id=playlist_id)
    track_items = pl['tracks']['items']
    # This will only get the 100 earliest added tracks, so duplicates
    # could still be added. Trying to figure out a loop to reliably
    # make extension playlists everytime the orginial playlist gets
    # to 100 tracks
    existing_ids = [track_item['track']['id'] for track_item in track_items]
    
    if track['id'] in existing_ids:
        print(f"{track['name']} already in {playlist_name}")
        return
    else:
        track_ids = [track['id']]
        sp.user_playlist_add_tracks(user, playlist_id, tracks=track_ids, position=None)
        print(f"Added {track['name']} by {track['artists'][0]['name']} to {playlist_name}")

def add_single_to_playlist(track, **kwargs):

    release_date = kwargs.get('release_date', None)
    if release_date == None:
        release_date = track['album']['release_date']
    try: # don't add this track if it doesn't have a valid
    # release date
        date_dt = datetime.fromisoformat(release_date)
    except ValueError:
        return
    year = date_dt.year
    month = calendar.month_name[date_dt.month]
    suffix = kwargs.get('suffix', None)
    name = f'{year} {month}'
    if suffix != None:
        name = f'{name} {suffix}'

    # Works if there's an existing singles playlist
    # for this track in playlist.database()
    try:
        add_track_to_playlist(track, name)
    # If no existing playlist, just create a new monthly
    # playlist with playlist.new_playlist() and add track
    # to the new playlist
    except:
        new_playlist(name=name)
        add_track_to_playlist(track, name)

def add_current_track_to_playlist(ask_name=False, **kwargs):

    db = database()
    track = playback.get_current_track()

    if ask_name:
        name = input("Enter name of target playlist> ")
        while name not in db.name.values:
            db = database() # get a fresh copy of the db
            # object in case it got updated in new_playlist()
            # name = input(f"No playlist with name {name}, try again> ")
            nextstep = input(f"getlist or makenew?> ")
            if nextstep == 'getlist':
                for plname in db.name.values:
                    print(plname)
                name = input("Enter name of target playlist> ")
            elif nextstep == 'makenew':
                new_playlist(name=name)
                add_track_to_playlist(track, name)


        add_track_to_playlist(track, name)

    # Otherwise, add track to the singles playlists for 
    # that song's release month
    else:
        add_single_to_playlist(track)

def update_singles_playlists(**kwargs):
    # Don't want artist.singles_df to instantiate
    # a new spotify (sp) object for every artist
    df = dataframe()
    sp = utilities.get_user_sp()
    sdfs = []
    artist_names = []
    time_window = kwargs.get('time_window', 100)
    cutoff = datetime.today() - timedelta(days=time_window)
    n_artists = kwargs.get('n_artists', len(df.track_artist_id.unique()))
    artist_ids = list(df.track_artist_id.unique()[600:n_artists])

    for i, artist_id in enumerate(artist_ids):

        sdf = artist.singles_df(artist_id=artist_id, sp=sp)
        print(f'artist {i+1} of {len(artist_ids)}')
        cutoff_date = '-'.join([str(integer).zfill(2) for integer in cutoff.isocalendar()])

        if sdf.empty == True:
            print(f'No singles from {artist_name} since {cutoff_date}')

        else:
            artist_name = sdf.artist_name.iloc[0]
            # Drop singles from before the cut off date, which
            # defaults to current day - offset
            bool_inds = []
            for rd in sdf.release_date:
                try:
                    bool_ind = datetime.fromisoformat(rd) >= cutoff
                except:
                    bool_ind = False
                bool_inds.append(bool_ind)
            sdf = sdf.loc[bool_inds, :]
            sdfs.append(sdf)
            artist_names.append(artist_name)

            for single_album_id in sdf.album_id.values:
                try:
                    album = sp.album(single_album_id)
                    tracks = sp.album_tracks(single_album_id)['items']
                except:
                    # Might need to refresh an expired token
                    sp = utilities.get_user_sp()
                    album = sp.album(single_album_id)
                    tracks = sp.album_tracks(single_album_id)['items']
                rd = album['release_date']
                

                for track in tracks:
                    add_single_to_playlist(track, release_date=rd, suffix='auto')
                    