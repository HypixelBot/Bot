import logging
import sys

import aiohttp
import time as t
from discord import Webhook, AsyncWebhookAdapter
from trello import TrelloClient

from cogs.utils.checks import *
from cogs.utils.mojang import *
from cogs.utils.time import human_timedelta

log = logging.getLogger(__name__)

class Misc(commands.Cog):
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot
        config = load_config()
        self.nickCache = {}
        self.client = TrelloClient(
            api_key=config["trelloApiKey"],
            api_secret=config["trelloApiSecret"],
            token=config["trelloToken"],
            token_secret=config["trelloTokenSecret"])

    async def cog_before_invoke(self, ctx):
        # if ctx.command.name != 'updates':
        #     try: await ctx.message.delete()
        #     except: pass
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages:
            return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')

    @commands.command(aliases=["feedback", "report"])
    @commands.cooldown(rate = 1, per = 10, type = commands.BucketType.user)
    async def suggest(self, ctx, *, msg):
        """Sends a suggestion directly to the owner.

        This is a quick way to request features or bug fixes
        without being in the bot's server.
        """
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.bot.webhooks['suggestions'], adapter=AsyncWebhookAdapter(session))
            em = discord.Embed(color=discord.Color.orange().value)
            if type(ctx.channel) is discord.channel.DMChannel: em.description = f'**Channel**: {ctx.channel} ({ctx.channel.id})\n```{msg}```'
            else: em.description = f'**Guild**: {ctx.guild} ({ctx.guild.id})\n**Channel**: {ctx.channel} ({ctx.channel.id})\n```{msg}```'
            em.set_author(name=f'{ctx.author}', url=ctx.author.avatar_url)
            em.set_footer(text='Received').timestamp = datetime.datetime.utcnow()
            em.set_thumbnail(url=ctx.author.avatar_url)
            await webhook.send(embed=em, username=str(self.bot.user), avatar_url=self.bot.user.avatar_url)
        board = self.client.get_board("HFoxfHPs")
        feedback = board.get_list('5aac4dd0d90abc853b0a5a97')
        feedback.add_card(name=f'{ctx.author.name}#{ctx.author.discriminator} - Feedback', desc=msg)
        await ctx.send(f'Feedback logged onto <https://trello.com/b/HFoxfHPs>')

    @commands.command(name = 'about')
    async def about(self, ctx):
        """Information about the bot right here."""
        await ctx.trigger_typing()
        uptime = (datetime.datetime.now() - self.bot.uptime)
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        days, hours = divmod(hours, 24)
        if days: time = f'{days} day{"s" if days != 1 else ""}, {t.strftime("%H:%M:%S", t.gmtime(uptime.seconds))}'
        else: time = t.strftime("%H:%M:%S", t.gmtime(uptime.seconds))
        em = discord.Embed(color = 0xd4702c, title="📊 Hypixel Bot Statistics",
                           description = f'**[Support Server](http://hypixelbot.fun/discord) | '
                                         f'[Patreon](https://www.patreon.com/bePatron?c=916813) | '
                                         f'[Invite](http://hypixelbot.fun/add) | '
                                         f'[Website](https://www.hypixelbot.fun/)**\n\n'
                                         f'<:python:495784509565042699>Python version: **{sys.version[:5]}**\n'
                                         f'<:books64:498126669270220811> Library version: **{discord.__version__}**\n'
                                         f'<:watch64:498126669295648788> Uptime: **{time}**\n'
                                         f'<:radar64:498127771642363906> Average Ping: **{int(self.bot.latency*1000)} ms**\n'
                                         f'<:server64:498126669324746762> Total Servers: **{len(self.bot.guilds)}**\n'
                                         f'<:italianpizza64:498126669425672192> Shard count: **{self.bot.shard_count}**\n'
                                         f'<:couple64:498126669136003094> Users: **{len(self.bot.users)}**\n\n'
                                         # f'```fix\n'
                                         # f'• Epic support for Pit!\n'
                                         # f'• PIT Leaderboards, last kills, and much more.\n'
                                         # f'• Skyblock Magma Boss and Dark Auction timers\n'
                                         # f'• h!hypixel skyblock darkauction/magmaboss\n'
                                         # f'• h!help hypixel pit to view what else you can do now\n```'
                           )
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url).timestamp = datetime.datetime.now()
        await ctx.send(embed = em)

    @commands.command()
    async def uptime(self, ctx):
        """Shows the bot's uptime!"""
        uptime = (datetime.datetime.now() - self.bot.uptime).total_seconds()
        await ctx.send(f"Uptime: **{human_timedelta(datetime.datetime.utcfromtimestamp(self.bot.uptime.timestamp()+uptime*2))}**")

    @commands.command()
    async def invite(self, ctx):
        """Invitation link for you to add me."""
        try:
            """Joins a server."""
            url = f'🔧 Want to invite me to your server? Click the link below!\nhttp://hypixelbot.fun/add'
            await ctx.author.send(url)
        except discord.Forbidden as e:
            await ctx.send(e.text.replace('this user', f'<@{ctx.author.id}>'))

    @commands.command()
    async def support(self, ctx):
        """Join the support server"""
        try:
            await ctx.author.send("🔧 | Looking for support? My support channel is here:\nhttps://hypixelbot.fun/discord")
        except discord.Forbidden as e:
            await ctx.send(e.text.replace('this user', f'<@{ctx.author.id}>'))

    @commands.command()
    async def donate(self, ctx):
        """Donate to help fund me!"""
        try:
            embed = discord.Embed(description='**You want to donate?**\n\nThat\'s awesome! [PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=LKX397WRTG2D69) [Patreon](https://www.patreon.com/bePatron?c=916813)')
            await ctx.author.send(embed=embed)
        except discord.Forbidden as e:
            await ctx.send(e.text.replace('this user', f'<@{ctx.author.id}>'))

    @commands.command(aliases=["vote"])
    async def upvote(self, ctx):
        """Upvote me for motivation :D"""
        try:
            await ctx.author.send("http://hypixelbot.fun/vote")
        except discord.Forbidden as e:
            await ctx.send(e.text.replace('this user', f'<@{ctx.author.id}>'))

    # @commands.command()
    # async def partners(self, ctx):
    #     em = discord.Embed()
    #     em.set_thumbnail(url='https://cdn.discordapp.com/avatars/543974987795791872/6e20cfecaba51762a511c39f68a73de5.png?size=128')
    #     em.set_author(name='Hypixel Bot partners', icon_url=self.bot.user.avatar_url)
    #     em.add_field(name='Upgrade.Chat', value='Upgrade.Chat (https://upgrade.chat/) is a STRIPE VERIFIED Partner Bot that allows server owners to sell roles and subscriptions via Discord. Want to make money with your Discord server? Invite Upgrade.Chat now!')
    #     em.add_field(name='Link', value='https://discord.gg/ZC3egaM')
    #     await ctx.send(embed=em)

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def autonick(self, ctx):
        data = await self.bot.pool.fetchrow(f"select * from hypixel where userID={ctx.author.id}")
        if not data:
            return await ctx.send(f'It appears that you haven\'t verified yourself yet.\nRun `{ctx.prefix}verify [in game name]` and try again.')
        nickStatus = data['autonick']
        userUUID = data['useruuid']
        if nickStatus:
            await self.bot.pool.execute(f'update hypixel set autonick=False where userID={ctx.author.id}')
            return await ctx.send(f'{ctx.author.mention}, Autonick has been **disabled** for you!')
        else:
            if userUUID not in self.nickCache:
                ign = await Mojang(self.bot.session).getUser(userUUID)
                self.nickCache.update({userUUID: ign})
                logging.info(self.nickCache)
            else:
                ign = self.nickCache[userUUID]
            try:
                await ctx.author.edit(nick=ign)
            except Exception as error:
                logging.error(error)
            await self.bot.pool.execute(f'update hypixel set autonick=True where userID={ctx.author.id}')
            return await ctx.send(f'{ctx.author.mention}, Autonick has been **enabled** for you!')

def setup(bot):
    bot.add_cog(Misc(bot))
