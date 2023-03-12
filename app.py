import os
import logging
import discord
from discord import Option
from keep_alive import keep_alive

# SET DEFAULT BOT SETTINGS & GLOBAL VARS
# used for DB, do not absolutely change or you will lose access to prefixes previously changed by servers using this bot
BOT_NAME = "boombox_v4"
FRIENDLY_BOT_NAME = "Boombox v4"
DESCRIPTION = "Next major version of Boombox, rewritten to utilize cogs and slash commands feature!"
INVALID_COMMAND_PREFIXES = ('@', '#', '/')
DEFAULT_COMMAND_PREFIX = "!"    # Default command prefix
TESTING_SERVERS = [997532964659404910]  # JLabs
data = {}

# SET LOGGING
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
# dump logs to boombox_v4.log
handler = logging.FileHandler(
    filename=f'{BOT_NAME}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = discord.Bot(description=DESCRIPTION,
                  debug_guilds=TESTING_SERVERS, help_command=None)

for file in os.listdir('./cogs'):
    if file.endswith('utils.py') or file == "__init__.py":
        print(f"Ignoring {file}")
        continue
    if file.endswith('.py'):
        bot.load_extension("cogs." + file[:-3])


@bot.event
async def on_ready():
    print(f"Name: {bot.user}")
    print(f"ID: {bot.user.id}")
    print(f"Logged in and ready!")


@bot.slash_command(description="Reloads a cog module")
async def reload(ctx, extension: Option(str, "The name of the cog module you want to load")):
    try:
        bot.reload_extension(f"cogs.{extension}")
        await bot.sync_commands(guild_ids=TESTING_SERVERS)
        await ctx.respond(f"`{extension}` cog was successfully reloaded!")
    except:
        await ctx.respond(f"`{extension}` cog does not exist")


if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ['BOOMBOX_V4_TOKEN'])
