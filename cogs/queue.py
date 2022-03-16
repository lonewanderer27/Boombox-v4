from discord import slash_command, Embed
from discord.ext import commands
from app import TESTING_SERVERS, data
import random

class Queue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.is_shuffled = False

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

    
    @slash_command(description=f"Shuffle queue of songs")
    async def shuffle_queue(self, ctx):
        await self.shuffle_queue_func(ctx)
        self.is_shuffled = True
        await self.queue(ctx)
            

    @slash_command(description=f"Show queue of songs")
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


def setup(bot):
    print(f"Added {__file__} cog!")
    bot.add_cog(Queue(bot))