import json, discord, asyncpg
from discord.ext import commands
from datetime import datetime

class Octal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        if msg.channel.id == 887188161594277918:
            if msg.content.startswith("**NOREPLY**"):
                return

            while True:
                try:
                    async with self.bot.db.octal.db.acquire() as conn:
                        lb = await conn.fetch("SELECT * FROM octal_counter_lb")
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

            n = await self.bot.db.octal.get_current_number()
            if str(msg.content).startswith(str(self.bot.octal.encode(n + 1))):
                await self.bot.db.octal.set_number(msg.author, msg, n + 1)

                if ((n + 1) % 50) == 0:
                    try:
                        await msg.pin(reason=f"Counted to {self.bot.octal.encode(n + 1)} ({n + 1}) (Multiple of 50 [current milestone])")
                        await msg.channel.send(f"We hit {self.bot.octal.encode(n + 1)} ({n + 1}) counts! The one who achieved this was {msg.author.mention} - `{msg.author}`!")
                    except:
                        pass
            else:
                await msg.delete()

    @commands.group(name='octal', aliases=['oct'], invoke_without_command=True, case_insensitive=True)
    async def _octal(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.send_help(ctx.command)

    @_octal.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        while True:
            try:
                async with self.bot.db.octal.db.acquire() as conn:
                    lb = await conn.fetch("SELECT * FROM octal_counter_lb ORDER BY counts DESC LIMIT 10")
            except asyncpg.exceptions._base.InterfaceError:
                pass
            else:
                break

        embed = discord.Embed().set_author(name="Leaderboard:", icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.utcnow()
        embed.color = 0x1FB052
        embed.description = ""

        c = 1

        for item in lb:
            if item['user_id'] == ctx.author.id:
                embed.description += f"""
**{c}. {self.bot.get_user(item['user_id'])}:** `{item['counts']} Octal Counts`
**\u200b \u200b \u200b Recent counts: {', '.join([f'[`{self.bot.octal.encode(r["num"])}`]({r["message_url"]})' for r in reversed(json.loads(item['recent_counts'])[-5:])])}**
            """
            else:
                embed.description += f"""
{c}. {self.bot.get_user(item['user_id'])}: `{item['counts']} Octal Counts`
\u200b \u200b \u200b Recent counts: {', '.join([f'[`{self.bot.octal.encode(r["num"])}`]({r["message_url"]})' for r in reversed(json.loads(item['recent_counts'])[-5:])])}
                """

                c += 1

        await ctx.send(embed=embed)

    @_octal.command(aliases=['r'])
    async def rank(self, ctx, *, target: discord.Member = None):
        target = target or ctx.author

        if target.bot:
            return await ctx.send("Bots are not included in this party, sorry!")
            
        while True:
            try:
                async with self.bot.db.octal.db.acquire() as conn:
                    res = await conn.fetchrow("SELECT * FROM octal_counter_lb WHERE user_id = $1", target.id)
            except asyncpg.exceptions._base.InterfaceError:
                pass
            else:
                break

        if not res:
            if target == ctx.author:
                return await ctx.send("Go count some octal in <#887188161594277918> first!")
            else:
                return await ctx.send(f"{target} hasn't counted any octal numbers in <#887188161594277918> yet!")

        embed = discord.Embed().set_author(name="Leaderboard:", icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.utcnow()
        embed.color = 0x1FB052
        embed.description = f"""
{'You' if target == ctx.author else target} have counted a total of `{res['counts']} Octal Numbers`.

Recent counts:
        """

        for i in reversed(json.loads(res['recent_counts'])[-5:]):
            embed.description += (('\u200b ' * 3) + f'- [`{self.bot.octal.encode(i["num"])}`]({i["message_url"]})' + '\n')

        await ctx.send(embed=embed)

    @_octal.command()
    async def convert(self, ctx, num):
        try:
            num = int(num)
        except:
            try:
                return await ctx.reply(f"`{num}` in normal base-10/arabic numeral is `{self.bot.octal.decode(num)}`!")
            except:
                return await ctx.send("That is an invalid integer or Octal numeral!")
            
        if num > 300000:
            return await ctx.send("Chill there bro.")

        return await ctx.reply(f"`{num}` in Octal numeral is `{self.bot.octal.encode(num)}`!")

    @_octal.command()
    async def current(self, ctx):
        num = await self.bot.db.octal.get_current_number()

        await ctx.send(f"The current count is `{self.bot.octal.encode(num)} ({num})`.")

def setup(bot):
    bot.add_cog(Octal(bot))