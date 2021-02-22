from __future__ import unicode_literals
import pandas as pd
from googleapiclient.discovery import build
import youtube_dl
import os

from youtuberipper.config import api_key, playlist_name, MAX_REQUESTS

def get_channel_videos(youtube):
    videos = []
    next_page_token = None

    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_name,
                                           part='snippet',
                                           maxResults=MAX_REQUESTS,
                                           pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break

    return videos


def get_videos_stats(video_ids, youtube):
    stats = []

    for i in range(0, len(video_ids), MAX_REQUESTS):
        res = youtube.videos().list(id=','.join(video_ids[i:i + MAX_REQUESTS]),
                                    part='statistics').execute()
        stats += res['items']

    return stats


def rip_URLs():
    youtube = build('youtube', 'v3', developerKey=api_key)

    videos = get_channel_videos(youtube)

    video_ids = list(map(lambda x: x['snippet']['resourceId']['videoId'], videos))

    stats = get_videos_stats(video_ids, youtube)

    d = []
    if len(stats) != len(videos):
        i = 1
        j = 0
    else:
        i = 0
        j = 0
    len_video = len(videos)
    len_stats = len(stats)
    for video in videos:
        if i >= len_video:
            break
        Url_video = 'https://www.youtube.com/watch?v=' + videos[i]['snippet']['resourceId'][
            'videoId']
        # + '&list=' + playlist_name
        d.append((videos[i]['snippet']['title'],
                  videos[i]['snippet']['resourceId']['videoId'],
                  Url_video,
                  ))

        i += 1
        j += 1

    df = pd.DataFrame(d, columns=('Title_video', 'ID_video', 'Url_video'))
    df.index += 1

    df.to_csv("data/youtube-playlist.csv", index=False)

    return df


def rip_AUDIO(df_urls_):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.getcwd()+'/data/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    for url in df_urls_['Url_video'].values.tolist():
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

