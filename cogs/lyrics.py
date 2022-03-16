import os
import discord
from discord.commands import slash_command, Option
from discord.ext import commands
from app import TESTING_SERVERS, data
import textwrap
from lyrics_extractor import SongLyrics
from functools import cache

class Lyrics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.song_lyrics = SongLyrics(os.environ['BOOMBOX_PROGRAMMABLE_SEARCH_ENGINE_KEY'], os.environ['BOOMBOX_PROGRAMMABLE_SEARCH_ENGINE_ID'])

    @cache
    def get_song_lyrics(self, title):
        return self.song_lyrics.get_lyrics(title)

    @cache
    def lyrics_splitter(self, song_data):
        return textwrap.wrap(song_data['lyrics'], width=2500,break_long_words=False,break_on_hyphens=False,replace_whitespace=False)

    def song_lyrics_embed(self, title, lyrics):
        '''Creates an Discord Embed that shows the lyrics of the currently playing song.'''
        return discord.Embed(color=0x44a8de, title=title, description=lyrics)

    def song_lyrics_embed_list_maker(self, song_data, lyrics_splitted):
        embed_list = []
        n = 0
        for lyrics_part in lyrics_splitted:
            n += 1
            if n != len(lyrics_splitted):
                lyrics = lyrics_part+"..."
            else:
                lyrics = lyrics_part
            embed = self.song_lyrics_embed(f"{song_data['title']}...   Part {n}", lyrics)
            embed_list.append(embed)
        return embed_list

    # for each slash command inside a cog, it needs to have the self argument! please!
    @slash_command(description="Get the lyrics of a song. Leave empty to fetch the lyrics of the current music.")
    async def lyrics(
        self, ctx, 
        title: Option(str, "Song's title", default=""),
        artist: Option(str, "Song's artist", default="")):

        if title == "":
            if not ctx.guild.voice_client.is_playing():
                await ctx.respond("Nothing is playing")
                return
            if ctx.guild.voice_client.is_playing():
                title = data[ctx.guild.id]['songs'][0]['title']

        if artist == "":
            song_display = title
        else:
            song_display = f"{title} - {artist}"

        await ctx.respond(f"Searching the lyrics of {song_display}")
        try:
            song_data = self.get_song_lyrics(song_display)
        except:
            await ctx.interaction.edit_original_message(content="I apologize there has been error. Please try again later.")

        embed_list = []
        if len(song_data['lyrics']) < 4000:
            embed_list.append(self.song_lyrics_embed(song_data['title'], song_data['lyrics']))

        else:
            lyrics_splitted = self.lyrics_splitter(song_data)
            embed_list = self.song_lyrics_embed_list_maker(song_data, lyrics_splitted)
        
        print("proof that this reloaded!")
        await ctx.interaction.edit_original_message(content=None,embeds=embed_list)


def setup(bot):
    print("Added Lyrics cog!")
    bot.add_cog(Lyrics(bot))
