import asyncio
import re
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
bot = commands.Bot(commands.when_mentioned_or('!countr ', '!counter ', '!count ', '?countr ', '?counter ', '?count ', '!countr', '!counter', '!count', '?countr', '?counter', '?count', 'countr ', 'counuter ', 'count ', 'countr?', 'counter?', 'count?', 'countr!', 'counter!', 'count!', 'countr', 'counter', 'count'), intents=intents, help_command=commands.MinimalHelpCommand(no_category="Misc"), description="A cool counter bot!", owner_ids=[699839134709317642, 621266489596444672])

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

@bot.event
async def on_message(msg: discord.Message):
    if re.match(rf'^<@(!)?{bot.user.id}>$', msg.content):
        return await msg.channel.send("My prefix is `countr `! To get help, type `counutr help`!")

@bot.command(aliases=['latency'])
async def ping(ctx):
    embed = discord.Embed()
    embed.color = 0x1FB052

    embed.set_author(name='Latency:', icon_url=ctx.author.avatar.url)

    embed.add_field(name='Websocket/Discord Latency:', value=f'`{round(bot.latency * 1000, 2)} ms`')

    latency = await db.latency()

    embed.add_field(name = 'Database Latency:', value=f'`{round(latency * 1000, 2)} ms`')

    await ctx.send(embed=embed)

bot.load_extension('jishaku')
bot.load_extension('cogs.roman')
bot.load_extension('cogs.hexa')
bot.load_extension('cogs.binary')
bot.load_extension('cogs.octal')

bot.run(TOKEN)