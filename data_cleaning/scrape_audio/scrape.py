import pandas as pd
import os
import fnmatch
import urllib
from bs4 import BeautifulSoup
import argparse
#import spotify
import json
from io import StringIO
import subprocess
import traceback
from urllib.parse import quote #from python2 to python3

df_12000=pd.read_csv('/gpfs/scratch/bz957/capstone/Download/df_sampled_12000.csv')

#!/usr/bin/python

#from googleapiclient.discovery import build
#from apiclient.errors import HttpError
#from oauth2client.tools import argparser



RED     = "\033[31m"
GREEN   = "\033[32m"
BLUE    = "\033[34m"
YELLOW  = "\033[36m"
DEFAULT = "\033[0m"

ACTION  = BLUE + "[+] " + DEFAULT
ERROR   = RED + "[+] " + DEFAULT
OK      =  GREEN + "[+] " + DEFAULT

#=======================
#   Spotify application
#=======================
CLIENT_ID=""
CALL_BACK_URL=""

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "REPLACE_ME"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
    q=options.q,
    part="id,snippet",
    maxResults=options.max_results
    ).execute()

    videos = []
    channels = []
    playlists = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                 search_result["id"]["videoId"]))
        elif search_result["id"]["kind"] == "youtube#channel":
            channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                   search_result["id"]["channelId"]))
        elif search_result["id"]["kind"] == "youtube#playlist":
            playlists.append("%s (%s)" % (search_result["snippet"]["title"],
                                    search_result["id"]["playlistId"]))

    print("Videos:\n", "\n".join(videos), "\n")
    print("Channels:\n", "\n".join(channels), "\n")
    print("Playlists:\n", "\n".join(playlists), "\n")

def searchYoutube(trackname):
    textToSearch = trackname
    query = quote(textToSearch) #from python2 to python3
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    #we return the first result
    return "https://youtube.com" + soup.findAll(attrs={'class':'yt-uix-tile-link'})[0]['href']

def getTrackName(id, access_token):
    """ get the spotify track name from id """
    print(ACTION + " getting track name")
    proc = subprocess.Popen('curl -sS -X GET "https://api.spotify.com/v1/tracks/'+ id +'?market=ES" -H "Authorization: Bearer '+ access_token +'"', shell=True, stdout=subprocess.PIPE)
#     print(proc)
    tmp = proc.stdout.read()
    #convert from json to string
    #io = StringIO()
    #json.dump(tmp, io)
    data = json.loads(tmp)
    if 'error' in data:
        print(ERROR + "can't found song name")
        print(ERROR + data['error']['message'])
        return None
    else:
        print(OK + "name is " + data["name"])
        return data["name"]

def genUrl():
    """ gen url for getting access token """
    print(ACTION + " generating url for access token")
    print(OK +  "https://accounts.spotify.com/authorize?client_id="+ CLIENT_ID + "&response_type=token&redirect_uri=" + CALL_BACK_URL)

def getAccessToken():
    """ get access token """
    print(ACTION + " getting access token")
    proc = subprocess.Popen('curl -sS -X GET "https://accounts.spotify.com/authorize?client_id='+ CLIENT_ID +'&response_type=token&redirect_uri='+ CALL_BACK_URL +'" -H "Accept: application/json"', shell=True, stdout=subprocess.PIPE)
    tmp = proc.stdout.read()
    data = json.loads(tmp)

    print(data)

def downloadYoutube(link):
    """ downloading the track """
    print(ACTION + "downloading song ..")
    proc = subprocess.Popen('youtube-dl --extract-audio --audio-format mp3 '+ link, shell=True, stdout=subprocess.PIPE)
    tmp = proc.stdout.read()
    
    print(OK + "Song Downloaded")

def header():
    """ header informations """
    print (RED + "@ spotify-dl.py version 0.0.1")
    print (YELLOW + "@ author : Naper")
    print (BLUE + "@ Designed for OSx/linux")
    print ("" + DEFAULT)

pwd = os.getcwd()
newlist = []
access_token = 'BQASgCHrnCn7EprEfGa9I5zTJEh7U1a3wOL08qNsuvFUbGqUpD7f9ry0NrhSILfMWprbIDC5sTutA3dpoYRRWEgKugMeQm59j-VvYiEkFQLPLonjfXzbtdPxubdWEEdy3gx-yCAGGjeF45VilCzJ9dv5B7pzZtpCSLC3FBO6J6mQIEaAfYJ5137a'
j=0
for i in range(1000,4000):
    try:
        oldlist = [f for f in os.listdir(".") 
           if f not in ['scrape.ipynb','.DS_Store','.ipynb_checkpoints'] and 
           os.path.isfile(os.path.join(pwd,f)) and not f.startswith('.')]
        
        track = df_12000['TITLE'][i] + ' ' + df_12000['ARTIST'][i]
#         name = getTrackName(track, access_token)
        link = searchYoutube(track)
        print(link)
        downloadYoutube(link)
        newlist = [f for f in os.listdir(".") 
           if f not in ['scrape.ipynb','.DS_Store','.ipynb_checkpoints'] and 
           os.path.isfile(os.path.join(pwd,f)) and not f.startswith('.')]
        newsong = [item for item in newlist if item not in oldlist][0]
        newname = df_12000['SPOTIFY_ID'][i]+'.' + df_12000['TITLE'][i] + '.' + df_12000['ARTIST'][i] +'.mp3'
        print(newsong, newname)
        os.rename(newsong, newname)
        print(j)
        
    except:
        print (ERROR + "use --help for help")
        print(i)
        continue 
    j+=1
        
