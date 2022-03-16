import discord
from discord.commands import slash_command, Option
from discord.ext import commands
from app import DEFAULT_COMMAND_PREFIX, TESTING_SERVERS, FRIENDLY_BOT_NAME


class Greeting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        bot = self.bot
        channel = message.channel
        guild_id = str(message.guild.id)
        guild_name = message.guild.name

        if not message.author.bot:
            print(f"{message.author.name}#{message.author.discriminator}: {message.content}")

        if message.content.startswith(f"{DEFAULT_COMMAND_PREFIX}Hi"):
            await channel.send("Hello!")

        elif message.content.startswith(f"{DEFAULT_COMMAND_PREFIX}Hello"):
            await channel.send("Hi!")

    @slash_command(description=f"Makes {FRIENDLY_BOT_NAME} say a message for you!", name="simon_says")
    async def simon_says(
        self, 
        ctx: discord.ApplicationContext, 
        message: Option(str, f"Message that you want {FRIENDLY_BOT_NAME} to repeat")):
        await ctx.respond(message)


def setup(bot):
    print("Added Greeting cog!")
    bot.add_cog(Greeting(bot))