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

intents = discord.Intents.all()
bot = commands.Bot(commands.when_mentioned_or('rc!', 'rc?', '?rc ', '!rc ', '?rc', '!rc'), intents=intents, help_command=commands.MinimalHelpCommand(no_category="Roman"), description="A roman counter bot!", owner_ids=[699839134709317642, 621266489596444672])

db = Database(asyncio.get_event_loop(), DATABASE_URI)
bot.db = db

def write_roman(num):

    roman = OrderedDict()
    roman[100000] = "C̅"
    roman[90000] = "X̅C̅"
    roman[50000] = "L̅"
    roman[40000] = "X̅L̅"
    roman[10000] = "X̅"
    roman[9000] = "MX̅"
    roman[5000] = "V̅"
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])

def padding(d: dict, *, separator: str = ': '):
    return "\n".join(f"{k.rjust(len(max(d.keys(), key=len)))}{separator}{v}" for k, v in d.items())

bot.padding = padding
bot.roman = write_roman

@bot.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return
        
    await bot.process_commands(msg)

    if msg.channel.id == 886133032103313458:
        if msg.content.startswith("**NOREPLY**"):
            return

        while True:
            try:
                async with db.db.acquire() as conn:
                    lb = await conn.fetch("SELECT * FROM counter_lb")
            except asyncpg.exceptions._base.InterfaceError:
                pass
            else:
                break

        greatest = None

        for item in lb:
            for i in json.loads(item['recent_counts']):
                if greatest is None:
                    greatest = datetime.fromtimestamp(i['timestamp'])
                else:
                    x = datetime.fromtimestamp(i['timestamp'])

                    if x > greatest:
                        greatest = x

        if lb and greatest is not None:
            user_id = discord.utils.find(lambda d: greatest.timestamp() in [v for r in json.loads(d['recent_counts']) for k, v in r.items() if k == 'timestamp'], lb)

            if user_id:
                if user_id['user_id'] == msg.author.id:
                    return await msg.delete()

        n = await db.get_current_number()
        if str(msg.content).startswith(str(write_roman(n + 1))):
            await db.set_number(msg.author, msg, n + 1)

            if ((n + 1) % 50) == 0:
                try:
                    await msg.pin(reason=f"Counted to {write_roman(n + 1)} ({n + 1}) (Multiple of 100 [current milestone])")
                    await msg.channel.send(f"We hit {write_roman(n + 1)} ({n + 1}) counts! The one who achieved this was {msg.author.mention} - `{msg.author}`!")
                except:
                    pass
        else:
            await msg.delete()

@bot.event
async def on_ready():
    print(f'{bot.user} Is Ready!')

@bot.command(aliases=['lb'])
async def leaderboard(ctx):
    while True:
        try:
            async with db.db.acquire() as conn:
                lb = await conn.fetch("SELECT * FROM counter_lb ORDER BY counts DESC LIMIT 10")
        except asyncpg.exceptions._base.InterfaceError:
            pass
        else:
            break

    embed = discord.Embed().set_author(name="Leaderboard:", icon_url=ctx.author.avatar.url)
    embed.timestamp = datetime.utcnow()
    embed.color = 0x1FB052
    embed.description = ""

    for item in lb:
        if item['user_id'] == ctx.author.id:
            embed.description += f"""
**{bot.get_user(item['user_id'])}:** `{item['counts']} Roman Counts`
**\u200b \u200b \u200b Recent counts: {', '.join([f'[`{write_roman(r["num"])}`]({r["message_url"]})' for r in reversed(json.loads(item['recent_counts'])[-5:])])}**
            """
        else:
            embed.description += f"""
{bot.get_user(item['user_id'])}: `{item['counts']} Roman Counts`
\u200b \u200b \u200b Recent counts: {', '.join([f'[`{write_roman(r["num"])}`]({r["message_url"]})' for r in reversed(json.loads(item['recent_counts'])[-5:])])}
            """

    await ctx.send(embed=embed)

@bot.command(aliases=['r'])
async def rank(ctx, *, target: discord.Member = None):
    target = target or ctx.author

    if target.bot:
        return await ctx.send("Bots are not included in this party, sorry!")
        
    while True:
        try:
            async with db.db.acquire() as conn:
                res = await conn.fetchrow("SELECT * FROM counter_lb WHERE user_id = $1", target.id)
        except asyncpg.exceptions._base.InterfaceError:
            pass
        else:
            break

    if not res:
        if target == ctx.author:
            return await ctx.send("Go count some roman in <#886133032103313458> first!")
        else:
            return await ctx.send(f"{target} hasn't counted any roman numbers in <#886133032103313458> yet!")

    embed = discord.Embed().set_author(name="Leaderboard:", icon_url=ctx.author.avatar.url)
    embed.timestamp = datetime.utcnow()
    embed.color = 0x1FB052
    embed.description = f"""
{'You' if target == ctx.author else target} have counted a total of `{res['counts']} Roman Numbers`.

Recent counts:
    """

    for i in reversed(json.loads(res['recent_counts'])[-5:]):
        embed.description += (('\u200b ' * 3) + f'- [`{write_roman(i["num"])}`]({i["message_url"]})' + '\n')

    await ctx.send(embed=embed)

@bot.command(aliases=['list', 'show', 'chart'])
async def table(ctx):
    embed = discord.Embed().set_author(name = "Roman Table:", icon_url=ctx.author.avatar.url)
    embed.timestamp = datetime.utcnow()
    embed.color = 0x1FB052

    d = {
        "1": "I",
        "5": "V",
        "10": "X",
        "50": "L",
        "100": "C",
        "500": "D",
        "1000": "M",
        "5000": "V̅",
        "10000": "X̅", 
        "50000": "L̅",
        "90000": "X̅C̅",
        "100000": "C̅"
    }

    embed.description = f"```yaml\n{padding(d)}```"

    await ctx.send(embed=embed)

@bot.command()
async def convert(ctx, num):
    try:
        num = int(num)
    except:
        return await ctx.send("That is an Invalid integer.")
        
    if num > 300000:
        return await ctx.send("Chill there bro.")

    return await ctx.reply(f"`{num}` in roman numeral is `{write_roman(num)}`!\n\nFor the full table run `rc?table`")

bot.load_extension('jishaku')

bot.run(TOKEN)