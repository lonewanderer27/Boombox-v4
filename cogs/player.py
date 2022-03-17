from pprint import pprint
import discord
from discord.commands import slash_command, Option
from discord.ext import commands
from app import FRIENDLY_BOT_NAME, DEFAULT_COMMAND_PREFIX, data
from cogs.utils import playing_now_embed


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def verify_if_boombox_can_join_vc(self, ctx):
        bot_vc_to_join_permissions_obj = ctx.author.voice.channel.permissions_for(ctx.guild.me)
        if not bot_vc_to_join_permissions_obj.connect:
            return False
        return True

    
    @slash_command(description="Show what's currently playing on vc")
    async def playing_now(self, ctx):
        try:
            if len(data[ctx.guild.id]['songs']) > 0 & ctx.guild.voice_client.is_playing():
                return await ctx.respond(embed=playing_now_embed(ctx))
            await ctx.respond("Nothing is playing right now")
        except KeyError:
            await ctx.respond("Nothing is playing right now")

    
    @slash_command(description="Pauses the music on vc")
    async def pause(self, ctx):
        if ctx.author.voice.channel.id == ctx.guild.voice_client.channel.id:

            if ctx.guild.voice_client.is_playing():
                ctx.guild.voice_client.pause()
                await ctx.respond("Paused ⏸")
            elif ctx.guild.voice_client.is_paused():
                await ctx.respond("Already Paused ⏸")
            else:
                await ctx.respond("Nothing is playing right now")

    
    @slash_command(description="Resumes the music on vc")
    async def resume(self, ctx):
        if ctx.author.voice.channel.id == ctx.guild.voice_client.channel.id:

            if ctx.guild.voice_client.is_paused():
                ctx.guild.voice_client.resume()
                await ctx.respond("Resumed ▶️")
            elif ctx.guild.voice_client.is_playing():
                await ctx.respond("Already Playing ▶️")
            else:
                await ctx.respond("Nothing is playing right now")

    
    @slash_command(description="Skips over the current music on vc")
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

    
    @slash_command(description="Loop the current music")
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

    
    @slash_command(description="Disconnects the bot from the vc")
    async def disconnect(self, ctx):
        if ctx.author.voice.channel.id == ctx.guild.voice_client.channel.id:
            await ctx.respond(f"Disconnecting from {ctx.guild.voice_client.channel.mention}")
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.respond(f"Join {ctx.guild.voice_client.channel.mention} and then you can disconnect me")

    
    @slash_command(description="Moves the bot to a voice channel")
    async def move(self, ctx, voice_channel: Option(discord.VoiceChannel, "Select a voice channel")):
        bot_vc_to_join_permissions_obj = voice_channel.permissions_for(ctx.guild.me)
        if not bot_vc_to_join_permissions_obj.connect:
            await ctx.respond(f"Oops, please give me permission to join {voice_channel.mention}")
            raise discord.ApplicationCommandInvokeError(f"{FRIENDLY_BOT_NAME} is not allowed to connect to {voice_channel.mention}")

        await ctx.guild.voice_client.move_to(voice_channel)
        await ctx.respond(f"Moved to {voice_channel.mention}")
        await ctx.guild.change_voice_state(channel=ctx.guild.voice_client.channel, self_deaf=True)    
         

    @slash_command(description="Join user voice channel")
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


    @pause.after_invoke
    @resume.after_invoke
    async def set_last_channel_that_triggered_command(self, ctx):
        print(f"{ctx.author.name} last triggered slash command in {ctx.interaction.channel}")
        data[ctx.guild.id]['last_channel_that_triggered_command'] = ctx.interaction.channel
        

    @loop.before_invoke
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
    print(f"Added {__file__} cog!")
    bot.add_cog(Player(bot))
    