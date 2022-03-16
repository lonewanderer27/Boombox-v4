import youtube_dl
from youtube_dl import YoutubeDL
from functools import cache
import json


class YoutubeExtractor:

    def __init__(self):
        self.ydl_options = {
            'format': 'bestaudio',
            'yes-playlist': True
        }
        self.ydl = YoutubeDL(self.ydl_options)

    @cache
    def ydl_extract_info_search_cached(self, song, amount):
        return self.ydl.extract_info(f"ytsearch{amount}: {song}", download=False)

    @cache
    def ydl_extract_info_link_cached(self, song):
        info = self.ydl.extract_info(song, download=False)

    def get_raw_ydl_response(self, song, amount):
        try:
            info = self.ydl_extract_info_link
            print("Playlist Link detected")
        except youtube_dl.utils.DownloadError:
            print("Name / Link detected")
            info = self.ydl_extract_info_search_cached(song, amount)
        # with open('ydl_playlist_test.json', 'w') as json_file:
        #     json.dump(info, json_file)
        return info

    def get_songs_from_ydl_response(self, info):
        songs = []
        for entry in info['entries']:
            songs.append({
                'title': entry['title'],
                'uploader': entry['uploader'],
                'channel_url': entry['channel_url'],
                'webpage_url': entry['webpage_url'],
                'thumbnail_url': entry['thumbnails'][0]['url'],
                'source': entry['formats'][0]['url'],
                'loop': False
            })
        return songs

    def main(self, songname, amount=1):
        raw_ydl_response = self.get_raw_ydl_response(songname, amount)
        songs = self.get_songs_from_ydl_response(raw_ydl_response)
        return songs