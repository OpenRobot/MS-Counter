import asyncio
from datetime import datetime
import discord
import asyncpg
import json
from discord.ext import commands
from config import *
from db import Database
from collections import OrderedDict
import jishaku
from roman import Roman

intents = discord.Intents.all()
bot = commands.Bot(commands.when_mentioned_or('rc!', 'rc?', '?rc ', '!rc ', '?rc', '!rc'), intents=intents, help_command=commands.MinimalHelpCommand(no_category="Misc"), description="A roman counter bot!", owner_ids=[699839134709317642, 621266489596444672])

db = Database(asyncio.get_event_loop(), DATABASE_URI)
bot.db = db

def padding(d: dict, *, separator: str = ': '):
    return "\n".join(f"{k.rjust(len(max(d.keys(), key=len)))}{separator}{v}" for k, v in d.items())

bot.padding = padding
bot.roman = Roman(db)

@bot.event
async def on_ready():
    print(f'{bot.user} Is Ready!')

bot.load_extension('jishaku')

bot.run(TOKEN)