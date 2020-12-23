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

from discord.ext import commands
from config import Config

import logging
import asyncio

def main():
    # Setup logging config
    logging.basicConfig(level=logging.INFO)

    # Setup bot
    bot = commands.Bot(
        command_prefix=Config.BOT_PREFIX,
        description="Killfeed.me - OSS Version"
    )

    # Killfeed cog
    cogs = [
        'cogs.killfeed',
    ]

    logging.debug("Loading cogs...")

    for extension in cogs:
        try:
            bot.load_extension(extension)
            logging.debug(f"Cog: {extension} loaded!")
        except Exception as e:
            logging.exception('Failed to load cog {}\n{}: {}'.format(extension, type(e).__name__, e))

    # Start bot loop
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(bot.start(Config.DISCORD_TOKEN))
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()