import youtube_dl
from youtube_dl import YoutubeDL
import json


class YoutubeExtractor:

    def __init__(self):
        self.ydl_options = {
            'format': 'bestaudio',
            'yes-playlist': True
        }

    def get_raw_ydl_response(self, song, amount):
        with YoutubeDL(self.ydl_options) as ydl:
            try:
                info = ydl.extract_info(song, download=False)
                print("Playlist Link detected")
            except youtube_dl.utils.DownloadError:
                print("Name / Link detected")
                info = ydl.extract_info(f"ytsearch{amount}: {song}", download=False)
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