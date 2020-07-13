import pandas as pd
import numpy as np
from datetime import datetime
from topspot import utilities, playlist, constants

def drop_clean_and_dup_tracks(albums_df):
    """
    For each duplicated album_title, check if one of the  
    duplicates is explicit, if so choose that one to keep.
    If none of the duplicates for that album_title is 
    explicit, choose the first one to keep.
    
    album_df could an artist.singles_df(artist_id) or an 
    artists.albums_df(artist_id)
    """
    df = albums_df
    dup_slice = df[df.duplicated('album_title')]
    try:
        # Won't work if there are no duplicates in 
        # the df. If so, just return the original df
        dup_titles = dup_slice.album_title
    except:
        return df
    albums_dups = df.set_index('album_title', drop=False).loc[dup_titles, :]

    all_ids = albums_dups.album_id.values
    keep_ids = []

    for title in albums_dups.index.unique():
        # For each duplicated album_title, check if one of the  
        # duplicates is explicit, if so choose that one to keep.
        # If none of the duplicates for that album_title is 
        # explicit, choose the first one to keep.
        album_slice = albums_dups.loc[title, :]
        assert len(album_slice) > 1, f"Album title: {title}/nDuplicated album slice has only one unique album"
        # Check if one of the duplicated single albums slice has 
        # one or more explicit tracks
        if True in album_slice.explicit_tracks.values:
            explicit_track = album_slice[album_slice.explicit_tracks == True]
            # If there is an explicit track, check if there are
            # more than one. If not, keep this album id as canon
            # for this single. If there are more than one,
            # choose the first one (arbirtrarily)
            if len(explicit_track) == 1 :            
                keep_ids.append(explicit_track.album_id.values[0])
            else:
                keep_ids.append(explicit_track.iloc[0, :].album_id)
        # If no explicit tracks, just choose the first copy of
        # the album
        else:
            keep_ids.append(album_slice.album_id[0])
    # Set drop ids to the list of ids that are in
    # all_ids but not in keep_ids
    drop_ids = list(set(all_ids).difference(set(keep_ids)))
    df_refined = df.set_index(['album_id'], drop=False).drop(drop_ids)
    df_refined = df_refined.set_index(np.array(range(len(df_refined))))
    
    return df_refined

def singles_df(**kwargs):
    """
    Return a dataframe with a row for each of the last 20 (limited
    by spotify api) singles released by the artist_name or artist_id
    passed to singles_df. 

    This function uses artits.drop_clean_and_dup_tracks() to remove
    duplicated and clean versions of singles albums

    Should be tested by passing kwarg artist_name = nonsense ('asdlfkj'), 
    artist with no singles ("Infinity Crush") which will return either an 
    empty dataframe or None. Then artist name that's not in playlist.dataframe(),
    and finally real artist who is in the archive ("TOPS").

    Right now all of these situations are handled in artist.all_artists_singles_df()
    which compiles all singles albums from all artists found in playlist.dataframe()
    """
    
    # Get objects from topspot
    pldf = playlist.dataframe()
    pldb = playlist.database()
    sp = kwargs.get('sp', utilities.get_user_sp())
    # Parse keyword args
    artist_name = kwargs.get('artist_name', None)
    artist_id = kwargs.get('artist_id', None)

    if artist_name != None:

        if artist_name not in pldf.track_artist_name.values:
            print("Must pass an artist name that exists in playlist.dataframe().track_artist_name")
            return None
        else:
            pass

        artist_slice = pldf.set_index('track_artist_name', drop=False).loc[artist_name, :]
        try:
            # Works if there are multiple appearances of this artist 
            # across user playlists
            artist_id = artist_slice.track_artist_id.unique()[0]
        except:
            # Works if there's only one appearance of this artst
            # across user playlists
            artist_id = artist_slice.track_artist_id
    else:
        artist_id = kwargs.get('artist_id', pldf.track_artist_id[0])
        artist_slice = pldf.set_index('track_artist_id', drop=False).loc[artist_id, :]
        artist_name = artist_slice.track_artist_name[0]
    try:
        albums = sp.artist_albums(artist_id, album_type='single')['items']
    except:
        print(f"No singles found for artist {artist_name}")
        return None
     # We need to scan each album for the explicit version
    # Since album objects are not tagged with the 'explicit'
    # key, we have to look through each track in each album
    # to find whether the album was explicit
    df = pd.DataFrame()
    for i, album in enumerate(albums):
        album_title = album['name']
        album_id = album['id']
        album_uri = album['uri']
        albums_tracks = sp.album_tracks(album_id, limit=50)['items']
        explicit_tracks = False
        release_date = album['release_date']
        for track in albums_tracks:
            if track['explicit'] == True:
                explicit_tracks = True

        df.loc[i, 'artist_name'] = artist_name
        df.loc[i, 'artist_id'] = artist_id
        df.loc[i, 'album_title'] = album_title
        df.loc[i, 'album_id'] = album_id
        df.loc[i, 'explicit_tracks'] = explicit_tracks
        df.loc[i, 'release_date'] = release_date
        df.loc[i, 'album_uri'] = album_uri
        
    print(f'Compiled singles DataFrame for {artist_name}')
    singles_df = drop_clean_and_dup_tracks(df)

    return singles_df

def all_artists_singles_df(save_file=False, **kwargs):
    """
    Return a dataframe containing the 20 most recent singles
    for every first artist featured in playlist.dataframe()
    """
    pldf = playlist.dataframe()
    artist_names = kwargs.get('artist_names', list(pldf.track_artist_name.unique()[0:2]))
    singles_dfs = []
    for i, artist_name in enumerate(artist_names):

        print(f"Collecting for singles from artist: {artist_name} (Artist {i+1} of {len(artist_names)})")
        # singles_df could be None at this point
        sdf= singles_df(artist_name=artist_name)
        # making a dataframe out of a dataframe will return the same dataframe.
        # If that "dataframe" passed to pd.DataFrame() is None, then a dataframe
        # with dataframe.emtpy = True will be returned
        sdf = pd.DataFrame(sdf)    
        if sdf.empty == False:
            singles_dfs.append(sdf)

        elif singles_df.empty == True:
            print(f"No singles found for artist: {artist_name}")
            pass

        else:
            pass

    all_artists_singles_df = pd.concat(singles_dfs, ignore_index=True)
    if save_file:
        all_artists_singles_df.to_csv(f"all_artists_singles_df_{str(datetime.now())}.csv", index=False)
    return all_artists_singles_df