from discord import Embed
from app import data
import aiohttp
import asyncio


def playing_now_embed(ctx):
    '''Creates an Discord Embed that shows the currently playing song.'''
    embed = Embed(color=0x44a8de, title="Playing Now")
    embed.set_thumbnail(url=data[ctx.guild.id]['songs'][0]['thumbnail_url'])
    title = data[ctx.guild.id]['songs'][0]['title']
    webpage_url = data[ctx.guild.id]['songs'][0]['webpage_url']
    uploader = data[ctx.guild.id]['songs'][0]['uploader']
    embed.add_field(
        name=uploader,
        value=f"[{title}]({webpage_url})",
        inline=True)
    embed.set_footer(
        text=f"Looping: {'Yes' if data[ctx.guild.id]['loop_current_music'] else 'No'}", icon_url=Embed.Empty)
    return embed


class LinkVerifier:

    def __init__(self) -> None:
        self.responses = []

    def display_current_link(self, link):
        print(f"Verifying if link works:\n{link}")

    async def verify_link(self, session, url, num):
        '''Function that verifies a link if it's working'''
        try:
            self.display_current_link(url)
            async with session.get(url, timeout=3) as response:
                self.responses[num] = response.status
                return True
        except asyncio.TimeoutError:
            return False
        except aiohttp.ClientConnectionError:
            return False

    async def execute_link_verifier(self, links):
        self.responses = [404] * len(links)
        async with aiohttp.ClientSession() as session:
            tasks = []
            num = 0
            for link in links:
                # num starts with zero so it matches the index
                task = asyncio.ensure_future(
                    self.verify_link(session, link, num))
                tasks.append(task)
                num += 1

            await asyncio.gather(*tasks)

        return self.responses
