"""
MIT License

Copyright (c) 2020 Victor Cortez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from discord.ext import commands, tasks
from config import Config
from os import path

import aiohttp
import aiofiles
import asyncio
import logging
import random
import discord
import re

class Killfeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reported = {}
        self.headers = {'Authorization': f'Bearer {Config.NITRADO_TOKEN}'}
        logging.basicConfig(level=logging.INFO)
    
    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Started bot | Made by vic#1337 (https://killfeed.me)")
        self.fetch_logs.start()

    async def run_loop(self):
        servers = list(Config.SERVERS.keys())

        for nitrado_id in servers:
            log = await self.download_logfile(nitrado_id)

            if log:
                asyncio.ensure_future(self.check_log(nitrado_id))
    
    @tasks.loop(minutes=5)
    async def fetch_logs(self):
        await self.run_loop()
    
    async def check_log(self, nitrado_id: int):
        logging.info(f"Checking logfile for {nitrado_id}")
        fp = path.abspath(path.join(path.dirname(__file__), "..", "files", f'{nitrado_id}.ADM'))
        channel = self.bot.get_channel(Config.SERVERS[nitrado_id])

        if channel is None:
            logging.error(f"Failed to get channel of channel ID: {Config.SERVERS[nitrado_id]}")
            return
        
        if nitrado_id not in self.reported:
            self.reported[nitrado_id] = []

        async with aiofiles.open(fp, mode="r") as f:
            async for line in f:
                if str(line) in self.reported[nitrado_id]:
                    continue

                self.reported[nitrado_id].append(str(line))

                if "(DEAD)" in line or "committed suicide" in line:
                    timestamp = str(re.search('(\\d+:\\d+:\\d+)', line).group(1))
                    player_killed = str(re.search(r'[\'"](.*?)[\'"]', line).group(1))

                    if "committed suicide" in line:
                        embed = discord.Embed(
                            title=f"💀 Suicide | {timestamp}",
                            description=f"**{player_killed}** commited suicide",
                            color=0x7a00ff
                        )
                        await channel.send(embed=embed)
                        await asyncio.sleep(2) # Avoid rate limits
                    elif "hit by explosion" in line:
                        explosion = str(re.search(r'\[HP: 0\] hit by explosion \((.*)\)', line).group(1))
                        embed = discord.Embed(
                            title=f"💀 Exploded | {timestamp}",
                            description=f"**{player_killed}** died from explosion ({explosion})",
                            color=0x7a00ff
                        )
                        await channel.send(embed=embed)
                        await asyncio.sleep(2) # Avoid rate limits
                    elif "killed by Player" in line:
                        player_killer = str(re.search(r'killed by Player "(.*?)"', line).group(1))
                        coords = str(re.search(r'pos=<(.*?)>', line).group(1))
                        weapon = re.search(r' with (.*) from', line) or re.search(r'with (.*)', line)
                        weapon = str(weapon.group(1))
                        try:
                            distance = round(float(re.search(r'from ([0-9.]+) meters', line).group(1)), 2)
                        except AttributeError:
                            distance = 0.0

                        embed = discord.Embed(
                            title=f"💀 PvP Kill | {timestamp}",
                            description=f"**{player_killer}** killed **{player_killed}**\n**Weapon**: `{weapon}` ({distance}m)\n**Location**: {coords}",
                            color=0x7a00ff
                        ).set_thumbnail(url=Config.EMBED_IMAGE)
                        rand_num = random.randint(1, 20)
                        if rand_num <= 2:
                            embed.description += "\n\nMade with :heart: by [Killfeed.me](https://killfeed.me)"
                        await channel.send(embed=embed)
                        await asyncio.sleep(2) # Avoid rate limits
                    elif "bled out" in line:
                        embed = discord.Embed(
                            title=f"🩸 Bled Out | {timestamp}",
                            description=f"**{player_killed}** bled out",
                            color=0x7a00ff
                        )
                        await channel.send(embed=embed)
                        await asyncio.sleep(2) # Avoid rate limits
                    elif "Animal_CanisLupus_Grey" in line or "Animal_CanisLupus_White" in line:
                        embed = discord.Embed(
                            title=f"🐺 Wolf Kill | {timestamp}",
                            description=f"**{player_killed}** killed by Wolf!",
                            color=0x7a00ff
                        )
                        await channel.send(embed=embed)
                        await asyncio.sleep(2) # Avoid rate limits
                    elif "Animal_UrsusArctos" in line or "Brown Bear" in line:
                        embed = discord.Embed(
                            title=f"🐻 Bear Kill | {timestamp}",
                            description=f"**{player_killed}** killed by Bear!",
                            color=0x7a00ff
                        )
                        await channel.send(embed=embed)
                        await asyncio.sleep(2) # Avoid rate limits
                    elif "hit by FallDamage" in line:
                        embed = discord.Embed(
                            title=f"💀 Fall Death | {timestamp}",
                            description=f"**{player_killed}** fell to their death!",
                            color=0x7a00ff
                        )
                        await channel.send(embed=embed)
                        await asyncio.sleep(2) # Avoid rate limits
            logging.info(f"Finished checking logfile for {nitrado_id}")
    
    async def download_logfile(self, nitrado_id):
        logging.info(f"Downloading logfile for {nitrado_id}")

        async with aiohttp.ClientSession() as ses:
            async with ses.get(f'https://api.nitrado.net/services/{nitrado_id}/gameservers', headers=self.headers) as r:
                if r.status != 200:
                    logging.error(f"Failed to get gameserver information ({nitrado_id}) ({r.status})")
                    return False
                else:
                    json = await r.json()
                    
                    username = json['data']['gameserver']['username']
                    game = json["data"]["gameserver"]["game"].lower()

                    if game == "dayzps":
                        logpath = "dayzps/config/DayZServer_PS4_x64.ADM"
                    elif game == "dayzxb":
                        logpath = "dayzxb/config/DayZServer_X1_x64.ADM"
                    else:
                        log_path = ""
                        logging.error("This bot only supports: DayZ PS4 and DayZ Xbox")
                        return False
                    
                    async with ses.get(f'https://api.nitrado.net/services/{nitrado_id}/gameservers/file_server/download?file=/games/{username}/noftp/{logpath}', headers=self.headers) as resp:
                        if resp.status != 200:
                            logging.error(f"Failed to get nitrado download URL! ({nitrado_id}) ({resp.status})")
                            return False
                        else:
                            json = await resp.json()
                            url = json["data"]["token"]["url"]

                            async with ses.get(url, headers=self.headers) as res:
                                if res.status != 200:
                                    logging.error(f'Failed to download nitrado log file! ({nitrado_id}) ({res.status})')
                                    return False
                                else:
                                    fp = path.abspath(path.join(path.dirname(__file__), "..", "files", f'{nitrado_id}.ADM'))
                                    async with aiofiles.open(fp, mode="wb+") as f:
                                        await f.write(await res.read())
                                        await f.close()
                                    logging.info(f"Successfully downloaded logfile for ({nitrado_id})")
                                    return True

def setup(bot):
    bot.add_cog(Killfeed(bot))
