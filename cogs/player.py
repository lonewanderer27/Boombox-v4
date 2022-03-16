import discord
from discord import FFmpegPCMAudio
from discord.commands import slash_command, Option, SlashCommandGroup
from discord.ext import commands
from youtube_dl import YoutubeDL
import requests
import asyncio
from pprint import pprint
from app import TESTING_SERVERS, FRIENDLY_BOT_NAME, DEFAULT_COMMAND_PREFIX, data
from cogs.player_utils import playing_now_embed, added_to_queue_embed, verify_yt_link

# SET FFMPEG OPTIONS
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def verify_if_boombox_can_join_vc(self, ctx):
        bot_vc_to_join_permissions_obj = ctx.author.voice.channel.permissions_for(ctx.guild.me)
        if not bot_vc_to_join_permissions_obj.connect:
            return False
        return True


    def error_playing_song(self, e, ctx):
        if e:
            ctx.guild.voice_client.stop()
            asyncio.run_coroutine_threadsafe(ctx.channel.send(f"There was an error playing {data[ctx.guild.id]['songs'][0]['title']}. Skipping"), self.bot.loop)

    
    async def play_song(self, ctx):
        print(f"{len(data[ctx.guild.id]['songs'])} song(s) left")

        if len(data[ctx.guild.id]['songs']) > 0:
            title = data[ctx.guild.id]['songs'][0]['title']                     # title of the video
            webpage_url = data[ctx.guild.id]['songs'][0]['webpage_url']         # normal youtube url
            source = data[ctx.guild.id]['songs'][0]['source']                   # streamable youtube url by FFMPEG
            thumbnail_url = data[ctx.guild.id]['songs'][0]['thumbnail_url']     # thumbnail url

            # it's ctx.channel.send here because ctx.respond causes invalid webhook token.
            await ctx.channel.send(embed=playing_now_embed(ctx))    
            ctx.guild.voice_client.play(FFmpegPCMAudio(source, **FFMPEG_OPTIONS), after = lambda e: self.error_playing_song(e, ctx))

            while ctx.guild.voice_client.is_playing() or ctx.guild.voice_client.is_paused():
                await asyncio.sleep(2)  # wait for 2 seconds before checking to avoid playing the next song too fast

            loop = data[ctx.guild.id]['loop_current_music']                     # do we loop the song?
            print(f"{title} finished playing! Loop: {loop}")
            if len(data[ctx.guild.id]['songs']) != 0 and not loop:
                print(f"Removing {title} from the queue")
                data[ctx.guild.id]['songs'].pop(0)

            await self.play_song(ctx)
        else:
            await ctx.channel.send(embed=discord.Embed(title="Queue", description="There are no more songs in the queue."))

    
    @slash_command(description=f"Show what's currently playing on vc")
    async def playing_now(self, ctx):
        try:
            if len(data[ctx.guild.id]['songs']) > 0 & ctx.guild.voice_client.is_playing():
                return await ctx.respond(embed=playing_now_embed(ctx))
            await ctx.respond("Nothing is playing right now")
        except KeyError:
            await ctx.respond("Nothing is playing right now")


    @slash_command(description=f"Play music on vc")
    async def play(self, ctx, title: Option(str, "Song's title or Youtube Link"), artist: Option(str, "Song's artist", default="")):
        if artist == "":
            song_display = title
        else:
            song_display = f"{title} - {artist}"
        await ctx.respond(f"Searching for {song_display}")

        with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
            try: 
                requests.get(title)
            except: 
                info = ydl.extract_info(f"ytsearch:{song_display} lyrics", download=False)['entries'][0]
            else:
                info = ydl.extract_info(title, download=False)        

        if not verify_yt_link(info['formats'][0]['url']):
            await ctx.delete()
            await ctx.respond(f"I apologize, {song_display} song cannot be added to queue. Please try again..")
            return

        video, source = (info, info['formats'][0]['url'])

        data[ctx.guild.id]['songs'].append({
                'title': info['title'],
                'uploader': info['uploader'],
                'channel_url': info['channel_url'],
                'webpage_url': info['webpage_url'],
                'source': info['formats'][0]['url'],
                'thumbnail_url': info['thumbnails'][0]['url'],
                'loop': False
            },)

        await ctx.delete()
        if not ctx.guild.voice_client.is_playing():
            
            await self.play_song(ctx)
        else:
            await ctx.channel.send(embed=added_to_queue_embed(info['title'], info['webpage_url'], info['thumbnails'][0]['url'], info['uploader']))

    
    @slash_command(description=f"Pauses the music on vc")
    async def pause(self, ctx):
        if ctx.author.voice.channel.id == ctx.guild.voice_client.channel.id:

            if ctx.guild.voice_client.is_playing():
                ctx.guild.voice_client.pause()
                await ctx.respond("Paused ⏸")
            elif ctx.guild.voice_client.is_paused():
                await ctx.respond("Already Paused ⏸")
            else:
                await ctx.respond("Nothing is playing right now")

    
    @slash_command(description=f"Resumes the music on vc")
    async def resume(self, ctx):
        if ctx.author.voice.channel.id == ctx.guild.voice_client.channel.id:

            if ctx.guild.voice_client.is_paused():
                ctx.guild.voice_client.resume()
                await ctx.respond("Resumed ▶️")
            elif ctx.guild.voice_client.is_playing():
                await ctx.respond("Already Playing ▶️")
            else:
                await ctx.respond("Nothing is playing right now")

    
    @slash_command(description=f"Skips over the current music on vc")
    async def skip(self, ctx):
        if ctx.author.voice.channel.id == ctx.guild.voice_client.channel.id:

            if ctx.guild.voice_client.is_playing():
                loop_state = data[ctx.guild.id]['loop_current_music']
                data[ctx.guild.id]['loop_current_music'] = False
                ctx.guild.voice_client.stop()
                await ctx.respond("Skip ⏭️")
                data[ctx.guild.id]['loop_current_music'] = loop_state
                
            else:
                await ctx.respond("Nothing is playing right now")         

    
    @slash_command(description=f"Loop the current music")
    async def loop(self, ctx):
        if ctx.author.voice.channel.id == ctx.guild.voice_client.channel.id:
            pprint(data)
            if ctx.guild.voice_client.is_playing():
                if data[ctx.guild.id]['loop_current_music']:
                    data[ctx.guild.id]['loop_current_music'] = False
                    return await ctx.respond(f"{data[ctx.guild.id]['songs'][0]['title']} is going to stop looping")
                else:
                    data[ctx.guild.id]['loop_current_music'] = True
                    await ctx.respond(f"{data[ctx.guild.id]['songs'][0]['title']} is going to loop now!")
            else:
                await ctx.respond("Nothing is playing right now")

    
    @slash_command(description=f"Disconnects the bot from the vc")
    async def disconnect(self, ctx):
        if ctx.author.voice.channel.id == ctx.guild.voice_client.channel.id:
            await ctx.respond(f"Disconnecting from {ctx.guild.voice_client.channel.mention}")
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.respond(f"Join {ctx.guild.voice_client.channel.mention} and then you can disconnect me")

    
    @slash_command(description=f"Moves the bot to a voice channel")
    async def move(self, ctx, voice_channel: Option(discord.VoiceChannel, "Select a voice channel")):
        bot_vc_to_join_permissions_obj = voice_channel.permissions_for(ctx.guild.me)
        if not bot_vc_to_join_permissions_obj.connect:
            await ctx.respond(f"Oops, please give me permission to join {voice_channel.mention}")
            raise discord.ApplicationCommandInvokeError(f"{FRIENDLY_BOT_NAME} is not allowed to connect to {voice_channel.mention}")

        await ctx.guild.voice_client.move_to(voice_channel)
        await ctx.respond(f"Moved to {voice_channel.mention}")
        await ctx.guild.change_voice_state(channel=ctx.guild.voice_client.channel, self_deaf=True)    
         

    @slash_command(description=f"Join user voice channel")
    async def join(self, ctx):
        print(ctx.voice_client)

        if ctx.author.voice == None:
            return await ctx.respond("Connect to a voice channel first")
        
        if not self.verify_if_boombox_can_join_vc(ctx):
            await ctx.respond(f"Oops, please give me permission to join {ctx.author.voice.channel.mention}")
            raise discord.ApplicationCommandError(f"{FRIENDLY_BOT_NAME} is not allowed to connect to {ctx.author.voice.voice_channel.mention}")

        if ctx.guild.voice_client == None:
            await ctx.respond(f"Joining {ctx.author.voice.channel.mention}")
            await ctx.author.voice.channel.connect()
            print(f"ctx.guild.voice_client [{ctx.guild.name}]: {ctx.guild.voice_client}")
            await ctx.guild.change_voice_state(channel=ctx.guild.voice_client.channel, self_deaf=True)    
            await ctx.interaction.edit_original_message(content=f"Connected to {ctx.guild.voice_client.channel.mention}")
            return

        if ctx.author.voice.channel.id != ctx.guild.voice_client.channel.id:
            if ctx.guild.voice_client.is_playing():
                await ctx.respond(f"{FRIENDLY_BOT_NAME} is playing in {ctx.voice_client.channel.mention}\nStop all currently playing songs or move the bot.")
                return
            else:
                print(ctx.author.voice.channel)
                print(f"Moving to {ctx.author.voice.channel.name}")
                await ctx.respond(f"Moving to {ctx.author.voice.channel.mention}")
                await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
                await ctx.interaction.edit_original_message(content=f"Connected to {ctx.author.voice.channel.mention}")
                await ctx.guild.change_voice_state(channel=ctx.guild.voice_client.channel, self_deaf=True)
                print(f"ctx.guild.voice_client [{ctx.guild.name}]: {ctx.guild.voice_client}")
                return
        else:
            await ctx.respond(f"I'm already connected in {ctx.guild.voice_client.channel.mention}")


    @play.after_invoke
    @pause.after_invoke
    @resume.after_invoke
    async def set_last_channel_that_triggered_command(self, ctx):
        print(f"{ctx.author.name} last triggered slash command in {ctx.interaction.channel}")
        data[ctx.guild.id]['last_channel_that_triggered_command'] = ctx.interaction.channel
        

    @loop.before_invoke
    @play.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    @move.before_invoke
    @disconnect.before_invoke
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
    print("Added Player cog!")
    bot.add_cog(Player(bot))