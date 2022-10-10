"""
yt_search.py
Samuel Lee
10/11/2021

uses yt-dlp (a fork of youtube-dl) to get info of a youtube video
also can search youtube based on an input search phrase
"""
import yt_dlp as youtube_dl
from requests import get

opts = {'format':'bestaudio', 'noplaylist':'True'}

def search(searchterm):
    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            get(searchterm)
        except:
            info = ydl.extract_info(f"ytsearch:{searchterm}", download=False)['entries'][0]
        else:
            info = ydl.extract_info(searchterm, download=False)
    for aformat in info['formats']:
        if aformat['format_id'] == '251':
            return (info, aformat['url'])
    return (info, info['formats'][0]['url'])

if __name__ == '__main__':
    video, url = search("https://www.youtube.com/watch?v=-0Ao4t_fe0I")
    print(url)
    print(video)
    