"""
:author: Shau
:date: 2023-02-07

https://github.com/arthurpph
"""

import asyncio
from typing import Final
import os
import platform

import nest_asyncio
import discord
from discord.ext.commands import Context, errors
from dotenv import load_dotenv
from discord import Intents
from discord.ext import commands

from config import Config
from vouch import Vouch
import logger

Config.load_config()
Vouch.load_vouches()
logger.load_logger()
load_dotenv()

TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.presences = True  # NOQA
intents.members = True  # NOQA

div_roles = Config.get_div_roles_id()


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="/", activity=discord.Game(name="The Bridge"), intents=intents,
                         help_command=None)

        self.logger = logger.get_logger()

    async def load_cogs(self) -> None:
        cogs = ["commands.py"]
        for filename in os.listdir("./"):
            if filename.endswith(".py") and filename in cogs:
                extension = filename[:-3]
                try:
                    await self.load_extension(f"{extension}")
                    self.logger.info(f"Loaded extension {filename}")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(f"Failed to load extension {extension}\n{exception}")

    async def setup_hook(self) -> None:
        self.logger.info(f"Logged in as {bot.user}")

        await self.load_cogs()

        try:
            synced = await bot.tree.sync()

            self.logger.info(f"Synced {len(synced)} command(s)")
            self.logger.info(f"discord.py API version: {discord.__version__}")
            self.logger.info(f"Python version: {platform.python_version()}")
            self.logger.info(
                f"Running on: {platform.system()} {platform.release()} ({os.name})"
            )
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            self.logger.error(f"Error while syncing commands: {exception}")


bot = Bot()
nest_asyncio.apply()
asyncio.run(bot.start(TOKEN))
