from discord import Embed
import urllib
from app import data

def playing_now_embed(ctx):
        '''Creates an Discord Embed that shows the currently playing song.'''
        embed= Embed(color=0x44a8de, title="Playing Now")
        embed.set_thumbnail(url=data[ctx.guild.id]['songs'][0]['thumbnail_url'])
        title= data[ctx.guild.id]['songs'][0]['title']
        webpage_url = data[ctx.guild.id]['songs'][0]['webpage_url']
        uploader = data[ctx.guild.id]['songs'][0]['uploader']
        embed.add_field(
            name=uploader, 
            value=f"[{title}]({webpage_url})",
            inline=True)
        embed.set_footer(text=f"Looping: {'Yes' if data[ctx.guild.id]['loop_current_music'] else 'No'}", icon_url=Embed.Empty)
        return embed


def added_to_queue_embed(title, webpage_url, thumbnail_url, uploader):
    '''Creates an Discord Embed that shows the song has been added to queue.'''
    embed=Embed(color=0x44a8de, title="Added to queue")
    embed.set_thumbnail(url=thumbnail_url)
    embed.add_field(name=uploader, value=f"[{title}]({webpage_url})", inline=False)
    return embed


def verify_yt_link(source):
    print(f"verifies if this link works:\n{source}")
    try:
        urllib.request.urlopen(source).getcode()
    except:
        print("Link did not worked :/")
        return False
    else:
        print("Link worked!")
        return True