import os
import textwrap
import discord
from discord.commands import Option
from discord.ext import commands
from app import data
from lyrics_extractor import SongLyrics
from functools import cache


class Lyrics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.song_lyrics = SongLyrics(
            os.environ['BOOMBOX_PROGRAMMABLE_SEARCH_ENGINE_KEY'], os.environ['BOOMBOX_PROGRAMMABLE_SEARCH_ENGINE_ID'])

    def verify_if_english(self, text):
        return text.isascii()

    @cache
    def get_song_lyrics(self, title):
        return self.song_lyrics.get_lyrics(title)

    @cache
    def lyrics_splitter(self, song_data):
        return textwrap.wrap(song_data['lyrics'], width=2500, break_long_words=False, break_on_hyphens=False, replace_whitespace=False)

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
            embed = self.song_lyrics_embed(
                f"{song_data['title']}...   Part {n}", lyrics)
            embed_list.append(embed)
        return embed_list

    # for each slash command inside a cog, it needs to have the self argument! please!
    @commands.slash_command(description="shows lyrics of currently playing song, alternatively you can search by entering the song title")
    async def lyrics(
            self,
            ctx: discord.ApplicationContext,
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
            print(song_data)
        except:
            await ctx.interaction.edit_original_response(content="I apologize I cannot find lyrics for that song.")

        embed_list = []
        if len(song_data['lyrics']) < 4000:
            embed_list.append(self.song_lyrics_embed(
                song_data['title'], song_data['lyrics']))

        else:
            lyrics_splitted = self.lyrics_splitter(song_data)
            embed_list = self.song_lyrics_embed_list_maker(
                song_data, lyrics_splitted)

        print("proof that this module was reloaded!!!/p")
        await ctx.interaction.edit_original_response(content=None, embeds=embed_list)


def setup(bot: commands.Bot):
    print(f"Added {__file__} cog!")
    bot.add_cog(Lyrics(bot))
