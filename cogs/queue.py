from pprint import pprint
import discord
from discord import slash_command, Embed, Option, FFmpegPCMAudio
from discord.ext import commands
from app import TESTING_SERVERS, data, FRIENDLY_BOT_NAME, DEFAULT_COMMAND_PREFIX
from cogs.utils import playing_now_embed, LinkVerifier
from cogs.downloader_utils import YoutubeExtractor
import random
import asyncio


class Queue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.is_shuffled = False
        self.youtube_extractor = YoutubeExtractor()
        self.link_verifier = LinkVerifier()
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

    def error_playing_song(self, e, ctx):
        if e:
            ctx.guild.voice_client.stop()
            asyncio.run_coroutine_threadsafe(ctx.channel.send(f"There was an error playing {data[ctx.guild.id]['songs'][0]['title']}. Skipping"), self.bot.loop)

    def added_to_queue_embed(self, title, webpage_url, thumbnail_url, uploader):
        '''Creates an Discord Embed that shows the song has been added to queue.'''
        embed=Embed(color=0x44a8de, title="Added to queue")
        embed.set_thumbnail(url=thumbnail_url)
        embed.add_field(name=uploader, value=f"[{title}]({webpage_url})", inline=False)
        return embed
    
    async def remove_unavailable_links_from_songs(self, songs):
        links = []
        for song in songs:
            source = song['source']
            links.append(source)
        responses = await self.link_verifier.execute_link_verifier(links)
        print(responses)

        num = 0
        available_songs = []
        for song in songs:
            if responses[num] == 200:
                available_songs.append(songs[num])
            num += 1 

        unavailable_songs = []
        for song in songs:
            if song not in available_songs:
                unavailable_songs.append(song)
        return available_songs, unavailable_songs
    
    def add_to_queue(self, ctx, songs):
        data[ctx.guild.id]['songs'].extend(songs)

    async def shuffle_queue_func(self, ctx):
        songs_list = data[ctx.guild.id]['songs']
        
        if len(songs_list) > 2:
            # [song1, song2, song3] = 1, 2, 3
            # shuffled_list = currently playing item + items from index 1 onwards of songs_list
            shuffled_songs_list = [songs_list[0]]
            remaining_songs_from_list = songs_list[1:]
            random.shuffle(remaining_songs_from_list)
            shuffled_songs_list.extend(remaining_songs_from_list)
            data[ctx.guild.id]['songs'] = shuffled_songs_list
        else:
            return await ctx.respond(embed=Embed(color=0x44a8de, title="Queue", description="There aren't enough songs to shuffle."))
    
    async def play_song(self, ctx):
        print(f"{len(data[ctx.guild.id]['songs'])} song(s) left")

        if len(data[ctx.guild.id]['songs']) > 0:
            title = data[ctx.guild.id]['songs'][0]['title']                     # title of the video
            webpage_url = data[ctx.guild.id]['songs'][0]['webpage_url']         # normal youtube url
            source = data[ctx.guild.id]['songs'][0]['source']                   # streamable youtube url by FFMPEG
            thumbnail_url = data[ctx.guild.id]['songs'][0]['thumbnail_url']     # thumbnail url

            # it's ctx.channel.send here because ctx.respond causes invalid webhook token.
            await ctx.channel.send(embed=playing_now_embed(ctx))    
            ctx.guild.voice_client.play(FFmpegPCMAudio(source, **self.FFMPEG_OPTIONS), after = lambda e: self.error_playing_song(e, ctx))

            while ctx.guild.voice_client.is_playing() or ctx.guild.voice_client.is_paused():
                await asyncio.sleep(2)  # wait for 2 seconds before checking to avoid playing the next song too fast

            loop = data[ctx.guild.id]['loop_current_music']                     # do we loop the song?
            print(f"{title} finished playing! Loop: {loop}")
            if len(data[ctx.guild.id]['songs']) != 0 and not loop:
                print(f"Removing {title} from the queue")
                data[ctx.guild.id]['songs'].pop(0)

            await self.play_song(ctx)
        else:
            await ctx.channel.send(embed=Embed(title="Queue", description="There are no more songs in the queue."))
    
    @slash_command(description=f"searches the music and plays it, alternatively single or playlist link also works")
    async def play(self, ctx, title: Option(str, "Song Title or Youtube Link [Song or Playlist]"), artist: Option(str, "Artist Name", default="")):
        if artist == "":
            song_display = title
        else:
            song_display = f"{title} - {artist}"
        await ctx.respond(f"Searching for {song_display}")

        songs = self.youtube_extractor.main(song_display)
        songs, unavailable_songs = await self.remove_unavailable_links_from_songs(songs)
        print("Available Songs: ")
        pprint(songs)
        pprint("Unavailable Songs: ")
        pprint(unavailable_songs)

        self.add_to_queue(ctx, songs)
        
        if not ctx.guild.voice_client.is_playing():
            await self.play_song(ctx)
        else:
            if len(songs) > 1:
                await ctx.channel.send("The playlist has been added!")
            else:
                await ctx.delete()
                fs = songs[0]   # fs = first song in the songs queue
                await ctx.channel.send(embed=self.added_to_queue_embed(fs['title'], fs['webpage_url'], fs['thumbnail_url'], fs['uploader']))  

        # if not verify_yt_link(info['formats'][0]['url']):
        #     
        #     await ctx.channel.send(f"I apologize, {song_display} song cannot be added to queue. Please try again..")
        #     return

        # video, source = (info, info['formats'][0]['url'])

        # data[ctx.guild.id]['songs'].append({
        #         'title': info['title'],
        #         'user_search_term': song_display,
        #         'uploader': info['uploader'],
        #         'channel_url': info['channel_url'],
        #         'webpage_url': info['webpage_url'],
        #         'source': info['formats'][0]['url'],
        #         'thumbnail_url': info['thumbnails'][0]['url'],
        #         'loop': False
        #     },)

        # await ctx.delete()
        # if not ctx.guild.voice_client.is_playing():
            
        #     await self.play_song(ctx)
        # else:
        #     await ctx.channel.send(embed=self.added_to_queue_embed(info['title'], info['webpage_url'], info['thumbnails'][0]['url'], info['uploader']))

    
    @slash_command(description="shuffles the songs in queue")
    async def shuffle(self, ctx):
        await self.shuffle_queue_func(ctx)
        self.is_shuffled = True
        await self.queue(ctx)

    @slash_command(description="displays the songs in queue")
    async def queue(self, ctx):
        songs_list = data[ctx.guild.id]['songs']

        print(f"{ctx.guild.name} Queued Songs: {len(songs_list[1:])}")
        
        if len(songs_list) > 1: # ['current song', 'next song'] 
            next_song = songs_list[1]
            embed=Embed(color=0x44a8de, title="New Queue" if self.is_shuffled else "Queue", description=Embed.Empty)
            self.is_shuffled = False
            embed.add_field(name="Up Next:", value=f"1 song remaining")
            embed.add_field(name=f"[1] - {next_song['title']}", value=next_song['uploader'], inline=False)
        else:   # there is no queued song, only current song
            return await ctx.respond(embed=Embed(color=0x44a8de, title="Queue", description="No songs are queued at the moment."))
        
        if len(songs_list) > 2: # ['current song', 'next song', '2nd next song', '3rd next song'] 
            embed.set_field_at(index=0, name="Up Next:", value=f"{len(songs_list[1:])} songs remaining")
            n = 2
            for song in songs_list[2:]:
                if n < 12:
                    embed.add_field(name=f"[{n}] {song['title']}", value=song['uploader'], inline=False)
                else:
                    if n > 12:
                        embed.set_footer(text=f"{len(songs_list)[10:]} more songs in the queue", icon_url=Embed.Empty)
                    break
                n += 1

            # TODO code the view and buttons for media controls
            # skip_button = Button(emoji="⏭", style=ButtonStyle.success)
            # skip_button.callback = self.skip
            # view = View(skip_button)
            return await ctx.respond(embed=embed)
        else:
            return await ctx.respond(embed=embed)

    @play.before_invoke
    async def ensure_bot_is_connected(self, ctx):
        if ctx.guild.voice_client == None:
            await ctx.respond(f"{FRIENDLY_BOT_NAME} is not connected to any channel")
            raise discord.ApplicationCommandInvokeError(f"{FRIENDLY_BOT_NAME} is not connected to any channel")

        try:
            print("data:")
            pprint(data)
            data[ctx.guild.id]
            print(f"{ctx.guild.name}'s data: OK!")

        except KeyError:
            print(f"{ctx.guild.name} data doesn't exist yet, creating...")
            data[ctx.guild.id] = {
                'guild_name': ctx.guild.name,
                'command_prefix': DEFAULT_COMMAND_PREFIX,
                'songs': [],
                'loop_current_music': False,
            }
            print(f"{ctx.guild.name} has been created!")
            print("data:")
            pprint(data)


def setup(bot):
    print(f"Added {__file__} cog!")
    bot.add_cog(Queue(bot))