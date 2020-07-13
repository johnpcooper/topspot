from topspot.utilities import get_user_sp, get_clipboard_uri, set_env_vars

def play_clipboard(**kwargs):
    """
    Search spotify for whatever's on the clipboard and
    play the first resulting track
    """
    sp = kwargs.get('sp', get_user_sp())
    track_uri = get_clipboard_uri()
    
    if track_uri:
        sp.start_playback(uris=[track_uri])
        print(f"Playing track")
    else:
        print("Couldn't find a track with this clipboard query")

def get_current_track(**kwargs):
    """
    Return the currently playing track (a dictionary)
    """
    sp = get_user_sp()
    track = sp.current_user_playing_track()
    return track['item']

def seek_for(increment_s=30):
    """
    Seek the currently playing track to current track
    progress in ms + 15 seconds (s)
    """
    increment_ms = increment_s*1000
    sp = get_user_sp()
    current_track = sp.current_playback()
    current_prog_ms = current_track['progress_ms']
    sp.seek_track(current_prog_ms + increment_ms)

def seek_rev(increment_s=15):
    """
    Seek the currently playing track to current track
    progress in ms - 30 seconds (s)
    """
    increment_ms = increment_s*1000
    sp = get_user_sp()
    current_track = sp.current_playback()
    current_prog_ms = current_track['progress_ms']
    target_ms = current_prog_ms - increment_ms
    sp.seek_track(target_ms)

def pseudoskip(fraction=0.001):
    """
    Navigate to the very last 0.1 % of currently
    playing track. If you do this instead of 
    skipping the track, it makes it into recently
    played.
    """
    sp = get_user_sp()
    current_track = sp.current_playback()
    duration_ms = current_track['item']['duration_ms']
    target_ms = duration_ms - round(duration_ms*fraction)
    sp.seek_track(target_ms)

def add_clipboard_to_queue():
    """
    Search spotify for the string on the clipboard
    and add the first track result to queue
    """
    sp = get_user_sp()
    track = get_clipboard_uri()
    clipboard_uri = get_clipboard_uri()
    sp.add_to_queue(clipboard_uri)
    print(f"Added song with uri '{clipboard_uri}' to queue")