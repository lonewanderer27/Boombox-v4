# from discord.commands import slash_command
from discord.ext import commands
import discord
from app import FRIENDLY_BOT_NAME


class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def get_latency(self):
        return f"{round(self.bot.latency * 1000)}ms"

    @commands.slash_command(description=f"ping {FRIENDLY_BOT_NAME}")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"pong! in {self.get_latency()}")

    @commands.slash_command(description=f"shows various debug information")
    async def debug(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="Debug Info")
        embed.add_field(name="Guild Name", value=ctx.interaction.guild.name)
        embed.add_field(name="Guild ID", value=ctx.interaction.guild.id)
        embed.add_field(name="Text Channel",
                        value=ctx.interaction.channel.mention, inline=True)
        if ctx.guild.voice_client != None:
            embed.add_field(name="Voice Channel",
                            value=ctx.guild.voice_client.channel.mention)
        embed.add_field(name="Latency", value=self.get_latency())
        embed.set_footer(
            text="Note: Guild is the internal name of Server. They're the same.", icon_url=discord.Embed.Empty)
        await ctx.respond(embed=embed)


def setup(bot):
    print(f"Added {__file__} cog!")
    bot.add_cog(Debug(bot))
