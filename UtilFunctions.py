import sys
import pandas as pd
import spotipy
from spotipy import SpotifyClientCredentials
from sklearn import preprocessing
import numpy as np
import seaborn as sn
from IPython.display import IFrame
from matplotlib.pyplot import figure

try:
    client_credentials_manager = SpotifyClientCredentials(
        client_id=cid,
        client_secret=secret )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

except:
    print("Spotipy credentials not found.")

# Functions:
# - get_features(trackid)
# Returns audio features and track information
def get_features(tracks):
    allTrackFeatures = []
    for _,album in enumerate(tracks):
        for _, name in enumerate(tracks[album]):
            trackFeatures = sp.audio_features(tracks[album][name])[0]
            
            trackInformation = sp.track(tracks[album][name])
            trackFeatures['popularity'] = trackInformation['popularity']
            trackFeatures['track_number'] = trackInformation['track_number']
            trackFeatures['duration_ms'] = trackInformation['duration_ms']
            trackFeatures['album'] = album
            trackFeatures['track'] = name
            allTrackFeatures.append(trackFeatures)

    return pd.DataFrame(allTrackFeatures)

# collects all tracks on a album
def get_album_tracks(albumId):
    tracks = {}
    batch_size = 10
    
    offset = 0
    while True:
        new_tracks = sp.album_tracks(albumId, limit=batch_size, offset=offset)["items"]
        for i in range(len(new_tracks)):
            
            tracks[new_tracks[i]['name']] = new_tracks[i]['id']
        if not len(new_tracks):
            break        
        offset += batch_size
    return tracks

# collects all tracks from a given artist
def collect_all_tracks(query, t):
    N = 10
    search_result = sp.search(query, N, 0, t)
    albumsNames = []
    tracks = []
    Alltracks = {}
    for i in range(N):
        artist = search_result['albums']['items'][i]['artists'][0]['name']
        if artist == query:
            album = search_result['albums']['items'][i]['name']
            Alltracks[album] = get_album_tracks(search_result['albums']['items'][i]['id'])
    return Alltracks

# Alltracks = collect_all_tracks('Daft Punk', 'album')

# Removes unnecessary columns and merges key columns 
def cleanData(Alltracks):
    Audiofeatures = get_features(Alltracks)
    Audiofeatures = Audiofeatures.drop(['analysis_url','track_href','type','uri'],axis=1)

    keyDict = {0:'c',1:'c#',2:'d',3:'d#',4:'e',5:'f',6:'f#',7:'g',8:'g#',9:'a',10:'a#',11:'b'}
    modeDict = {0:'minor',1:'major'}
    Audiofeatures[['key','mode']] = Audiofeatures[['key','mode']].replace({'key':keyDict, 'mode':modeDict})

    # # Audiofeatures2.groupby(['key','mode']).size().reset_index().rename(columns={0:'count'})
    Audiofeatures["TonalQuality"] = Audiofeatures["key"]+" " + Audiofeatures["mode"]
    # Audiofeatures = Audiofeatures.drop(['key','mode'],axis=1)
    return Audiofeatures

# Collect all tracks of given artist's
def AllTracksArtist(names):
    trackDict = {}
    for artist in names:
        trackDict[artist]=cleanData(collect_all_tracks(artist, 'album'))
    
    return trackDict
alltracks = AllTracksArtist(['Daft Punk', "Kanye West"])


def scaleMinMax(df):

    x = df
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    dfNormalised =  pd.DataFrame(x_scaled)
    dfNormalised.index = df.index
    dfNormalised.columns = df.columns  
    return dfNormalised
