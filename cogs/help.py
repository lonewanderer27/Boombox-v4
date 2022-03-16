from unittest.mock import DEFAULT
import discord
from discord.commands import slash_command
from discord.ext import commands
from app import TESTING_SERVERS, FRIENDLY_BOT_NAME, DEFAULT_COMMAND_PREFIX

class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def help_text(self, command_prefix):
        f'''
**__{FRIENDLY_BOT_NAME.title()} Guide:__**
`{command_prefix}h` or `{command_prefix}help` : sends this help message!


**Music Commands:**
`{command_prefix}join` : joins the bot to the voice channel
`{command_prefix}play <Youtube link or Song Title>` : plays a youtube link or video name
`{command_prefix}pause` : pauses the current playing song
`{command_prefix}resume` : resumes the paused song
`{command_prefix}skip` or `{command_prefix}next` : skips to the next song
`{command_prefix}playing-now` : shows the currently playing song
`{command_prefix}lyrics <Title>` : shows the lyrics for a song, if parameter is empty it will display the lyrics of the currently playing song
`{command_prefix}move <Channel ID or Name>` : moves the bot to another voice channel, if parameter is empty it will move to the user's current voice channel
`{command_prefix}queue` : displays the queued songs
`{command_prefix}disconnect` or `{command_prefix}dc` : disconnects the bot from the voice channel

**Other Commands:**
`{command_prefix}prefix` : shows the currently set prefix
`{command_prefix}prefix-change` : changes the prefix
`{command_prefix}Hi` : says "Hello"
`{command_prefix}Hello` : says "Hi"
`{command_prefix}simon-says` or `{command_prefix}repeat after me` : says back what the user will say

**Debug Commands:**
`{command_prefix}guild-info` : returns the server id & name'''

    @slash_command(description=f"Show {FRIENDLY_BOT_NAME} help message", name="help")
    async def help(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Type `/` and it will show you all of the available commands of {FRIENDLY_BOT_NAME}")

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     bot = self.bot
    #     channel = message.channel
    #     guild_id = str(message.guild.id)
    #     guild_name = message.guild.name

    #     if not message.author.bot:
    #         print(f"{message.author.name}#{message.author.discriminator}: {message.content}")

    #     if message.content.startswith(f"{DEFAULT_COMMAND_PREFIX}help"):
    #         ht = self.help_text(DEFAULT_COMMAND_PREFIX)
    #         await channel.send(ht)

def setup(bot):
    print(f"Added {__file__} cog!")
    bot.add_cog(Help(bot))