import asyncio
from typing import Final
import os

import nest_asyncio
from dotenv import load_dotenv
from discord import Intents
from discord.ext import commands


from config import Config

Config.load_config()

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.presences = True  # NOQA
intents.members = True  # NOQA

bot = commands.Bot(command_prefix="/", intents=intents)

div_roles = Config.get_div_roles_id()


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
