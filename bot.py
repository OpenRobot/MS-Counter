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
from utils import Roman, Octal, Binary, Hexadecimal

intents = discord.Intents.all()
bot = commands.Bot(commands.when_mentioned_or('rc!', 'rc?', '?rc ', '!rc ', '?rc', '!rc'), intents=intents, help_command=commands.MinimalHelpCommand(no_category="Misc"), description="A cool counter bot!", owner_ids=[699839134709317642, 621266489596444672])

db = Database(asyncio.get_event_loop(), DATABASE_URI)
bot.db = db

def padding(d: dict, *, separator: str = ': '):
    return "\n".join(f"{k.rjust(len(max(d.keys(), key=len)))}{separator}{v}" for k, v in d.items())

bot.padding = padding
bot.roman = Roman(db.roman)
bot.binary = Binary(db.binary)
bot.hexadecimal = Hexadecimal(db.hexadecimal)
bot.octal = Octal(db.octal)

@bot.event
async def on_ready():
    print(f'{bot.user} (Counter Bot) Is Ready!') 

bot.load_extension('jishaku')
bot.load_extension('cogs.roman')
bot.load_extension('cogs.hexa')
bot.load_extension('cogs.binary')
bot.load_extension('cogs.octal')

bot.run(TOKEN)