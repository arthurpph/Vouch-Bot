import asyncio
from typing import Final
import os

import nest_asyncio
from dotenv import load_dotenv
from discord import Intents, Message, User, Role, app_commands, Forbidden
from discord.ext import commands

from exceptions import InsufficientPermission, InvalidChannelId

from config import config

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.presences = True  # NOQA
intents.members = True  # NOQA

bot = commands.Bot(command_prefix="/", intents=intents)

div_roles = [int(config["div1RoleId"]),
             int(config["div2RoleId"]),
             int(config["div3RoleId"]),
             int(config["div4RoleId"])]


@bot.event
async def on_ready():
    print(f'{bot.user} está online')
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizado {len(synced)} comando(s)")
    except Exception as e:
        print(e)


async def load_extensions():
    for filename in os.listdir("./"):
        if filename.endswith(".py") and filename.startswith("commands"):
            await bot.load_extension(f"{filename[:-3]}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


nest_asyncio.apply()
asyncio.run(main())
