from discord.commands import slash_command, Option
from discord.ext import commands
from app import DEFAULT_COMMAND_PREFIX, FRIENDLY_BOT_NAME


class Greeting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):

        if not ctx.author.bot:
            return

        if ctx.message.content.startswith(f"{DEFAULT_COMMAND_PREFIX}ping"):
            await ctx.send("pong!")
    
    @slash_command
    async def ping(
        self,
        ctx,
    ):
        await ctx.respond("pong!")

    @slash_command(description=f"Makes {FRIENDLY_BOT_NAME} say a message for you!")
    async def simon_says(
        self, 
        ctx,
        message: Option(str, f"Message that you want {FRIENDLY_BOT_NAME} to repeat")):
        await ctx.respond(message)


def setup(bot):
    print(f"Added {__file__} cog!")
    bot.add_cog(Greeting(bot))