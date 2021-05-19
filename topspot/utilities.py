import os
from tkinter import Tk
import spotipy
from spotipy import util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import oauth2
from topspot import constants

def set_env_vars():

    for key, value in constants.env_vars.items():
        os.environ[key] = value

def get_user_sp(**kwargs):
    """
    Instantiate and return a spotipy.Spotify object using my
    credentials from topspot.constants by default

    scope is set to 'user-
    """
    set_env_vars()
    scope = kwargs.get('scope', constants.scope)
    cache_path = kwargs.get('cache_path', constants.user_vars['cache_path'])
    username = kwargs.get('username', constants.user_vars['username'])
    # Look for a chached token in the path specified in constants.user_vars
    # If None, prompt the user to authenticate
    sp_oauth = oauth2.SpotifyOAuth(scope=scope,cache_path=cache_path)
    token_info = sp_oauth.get_cached_token()
    if token_info == None:
        token = util.prompt_for_user_token(scope=scope, cache_path=cache_path, username=username)
    else:
        token = token_info['access_token']

    sp = spotipy.Spotify(auth=token)
    return sp

def get_client_sp(**kwargs):
    """
    Instantaite and return a spotipy.Spotify object using my client
    credentials (as long as they are set as environment variables)
    """
    set_env_vars()
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    return sp

def get_clipboard(clean_clipboard=True):
    """
    Return the contents of the OS clipboard
    using tkinter
    """
    root = Tk()
    root.withdraw()
    clipboard = root.clipboard_get()

    # Remove irrelevant text from text
    # so that it returns good results 
    # in spotify search
    if clean_clipboard:
        # Patterns text to drop are in
        # topspot.constants.patterns.bad_search_text
        pass
    else:
        pass 
    return clipboard

def get_clipboard_track():
    """
    Return the track found first in search results for 
    whatever is on the clipboard

    If no results, None is returned
    """
    sp = get_user_sp()
    # Also remove the english dash symbol if its
    # there (need to specify with unicode)
    query = query.replace(' \u2013 ', ' ')
    results = sp.search(q=query, type='track')

    items = results['tracks']['items']
    # If there was a result of the search, get that track's 
    # spotify id and uri (more commonly used)
    if len(items) > 0:
        track = items[0]
        track_id = track['id']
        track_uri = track['uri']
        track_name = track['name']
        print(f'Found track_uri: {track_uri}\nTrack name: {track_name}\nfor query: {query}')
    else:
        print(f"Couldn't find a matching track for search:\n{query}")
        track = None
        track_id = None
        track_uri = None
        track_name = None
        
    return track

def get_clipboard_uri(**kwargs):
    """
    Search spotify for whatever's on the clipboard and
    return the uri of the first track in search results.

    If no results, return None
    """
    sp = get_client_sp()
    # Remove the hyphen typically between artist and 
    # song name in headlines
    query = get_clipboard().replace(' - ', ' ')
    # Also remove the english dash symbol if its
    # there (need to specify with unicode)
    query = query.replace(' \u2013 ', ' ')
    results = sp.search(q=query, type='track')
    
    items = results['tracks']['items']
    # If there was a result of the search, get that track's 
    # spotify id and uri (more commonly used)
    if len(items) > 0:
        track = items[0]
        track_id = track['id']
        track_uri = track['uri']
        track_name = track['name']
        print(f'\nFound track_uri: {track_uri}\nTrack name: {track_name}\nfor query: {query}')
    else:
        print(f"Couldn't find a matching track for search:\n{query}")
        track_id = None
        track_uri = None
        track_name = None
        
    return track_uri

def get_track_release_dt(track):
    """
    Return the release date of the album containing
    the track matching track_uri
    """
    try:
        release_date = track['album']['release_date']
    except:
        release_date = None
        print("Failed to find release date for this track")
        try:
            print(f"track_name: {track['name']}")
        except:
            pass
        
    return release_date