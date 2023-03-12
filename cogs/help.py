import discord
from discord.ext import commands
from app import TESTING_SERVERS, FRIENDLY_BOT_NAME, DEFAULT_COMMAND_PREFIX


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.slash_help = f'''
**__{FRIENDLY_BOT_NAME.title()} Guide:__**
`/help` : sends this help message!

**Music Commands:**
`/join` : make {FRIENDLY_BOT_NAME} to your current voice channel
`/play <Song Title | Optionals: Youtube Link [Song or Playlist], Artist Name>` : searches the music and plays it, alternatively single or playlist link also works
`/pause` : pauses the currently playing song
`/resume` : resumes the paused song
`/skip` : skips to the next song
`/loop` : loop the current song
`playing_now` : shows the currently playing song
`/lyrics <Optionals: Song Title, Artist>` : shows the lyrics of currently playing song, alternatively you can also search by entering the song title
`/move <Voice Channel>` : moves {FRIENDLY_BOT_NAME} to another voice channel
`/queue` : displays the songs in queue
`/shuffle` : shuffles the songs in queue
`/disconnect` : disconnects {FRIENDLY_BOT_NAME} from voice channel

**Other Commands:**
`/simon_says` : make {FRIENDLY_BOT_NAME} say a message on behalf of you
`/ping` : ping {FRIENDLY_BOT_NAME}
`/debug` : shows guild id, guild name, text channel and optionally voice channel if {FRIENDLY_BOT_NAME} is connected to voice channel
'''

    def help_prefix(self, command_prefix):
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

    @commands.slash_command(description=f"Show {FRIENDLY_BOT_NAME} help message", name="help")
    async def help(self, ctx: discord.ApplicationContext):
        await ctx.respond(self.slash_help, ephemeral=True)


def setup(bot):
    print(f"Added {__file__} cog!")
    bot.add_cog(Help(bot))
