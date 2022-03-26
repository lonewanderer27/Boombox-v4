from discord.commands import slash_command
from discord.ext import commands
import discord
from app import FRIENDLY_BOT_NAME

class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description=f"shows guild id, guild name, text channel and optionally voice channel if {FRIENDLY_BOT_NAME} is connected to voice channel")
    async def debug(self, ctx):
        embed = discord.Embed(title="Debug Info")
        embed.add_field(name="Guild Name", value=ctx.interaction.guild.name)
        embed.add_field(name="Guild ID", value=ctx.interaction.guild.id)
        embed.add_field(name="Text Channel", value=ctx.interaction.channel.mention, inline=True)
        if ctx.guild.voice_client != None:
            embed.add_field(name="Voice Channel", value=ctx.guild.voice_client.channel.mention)
        embed.set_footer(text="Note: Guild is the internal name of Server. They're the same.", icon_url=discord.Embed.Empty)
        await ctx.respond(embed=embed)


def setup(bot):
    print(f"Added {__file__} cog!")
    bot.add_cog(Debug(bot))