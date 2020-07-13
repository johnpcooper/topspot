from datetime import datetime

import pandas as pd

from topspot import utilities, track, constants

def track_history_df(**kwargs):
    """
    Return the DataFrame residing at 
    constants.user_vars['track_history_path'].
    If no file there, return an empty DataFrame    
    """
    track_history_path = track_history_path = constants.user_vars['track_history_path']
    try:
        track_history_df = pd.read_json(track_history_path)
        print(f"Found track_history_df at: {track_history_path}")
    except ValueError:
        print(f"No file at: {track_history_path}")
        print(f"Returning empty DataFrame")
        track_history_df = pd.DataFrame()

    return track_history_df

def update_track_history(**kwargs):
    """
    Return nothing. Create a recently_played DataFrame using
    track.tracks_df() with no arguments => gets 50 recently
    played tracks. Then add that tracks_df to track_history_df whose
    path is defined in constants.user_vars['track_history_path']

    Duplicate tracks are not screened (because I want play counts),
    however duplicate 'played_at' datetimes are screened.
    """
    track_history_path = track_history_path = constants.user_vars['track_history_path']
    history_df = track_history_df()
    recently_df = track.tracks_df()

    if history_df.empty == True:
        recently_df.to_json(track_history_path)
        print(f"track_history_df updated at {datetime.now()}")
        return
    else:
        # Make sure the data types in both dataframes
        # played_at columns are the same, otherwise
        # we can't compare them to see which tracks
        # in recently_df are already in history_df
        if history_df.played_at.dtype != recently_df.played_at.dtype:
            raise Exception(f"""
                            dtypes in history and recently dataframes
                            played_at columns must be the same.

                            history_df dtype: {history_df.played_at.dtype}
                            recently_df dtype: {recently_df.played_at.dtype}
                            """)
        else:
            to_add = recently_df[~recently_df.played_at.isin(history_df.played_at)]
            updated_df = pd.concat([history_df, to_add], ignore_index=True)
            updated_df.to_json(track_history_path)
            print(f"track_history_df updated at {datetime.now()}")
            return

def merge_track_histories():
    """
    Add everything in temp_history_df() that's not in track_history_df()
    to track_history_df(), save that merged dataframe at 
    constants.user_vars.['track_history_df']. If, for some reason
    finaldf is shorter than histdf or empty, don't save the new file.
    I don't want to overwrite the WSL local master history_df 
    accidentally

    Return nothing
    """
    histdf = track_history_df()
    tempdf = temp_history_df()

    boolindex = ~tempdf.played_at.isin(histdf.played_at)
    to_add = tempdf[boolindex]
    finaldf = pd.concat([histdf, to_add], ignore_index=True)

    if len(finaldf) < len(histdf) or finaldf.empty == True:
        raise("merge_track_histories is losing data! Aborting")

    elif len(finaldf) <= len(histdf):
        print("No new tracks to add")

    else:
        print(f"Adding {len(finaldf) - len(histdf)} new tracks to history")
        writepath = constants.user_vars['track_history_path']
        finaldf.to_json(writepath)