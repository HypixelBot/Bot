from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
from collections import Counter
from cogs.utils.checks import *
from cogs.utils import context
from datetime import datetime
from cogs.utils.misc import *
import traceback
import asyncio
import logging
import discord

log = logging.getLogger(__name__)

def percentage(whole, part):
    return 100 * float(part)/float(whole)

def tick(opt):
    emoji = 'Yes' if opt else 'No'
    return emoji

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.HypixelGuild = 385954529557872640
        self.HypixelRole = 403538532926488587
        self.channels = ["general", "chat", "lobby", "main", "lounge"]
        self.allowed = False
        self.invites = ['discord.gg/', 'discordapp.com/invite/']
        self.invite_domains = ['discord.gg', 'discordapp.com']

    async def hastebin(self, content):
        async with self.bot.session.post("https://hastebin.com/documents", data=content.encode('utf-8')) as resp:
            if resp.status == 200:
                result = await resp.json()
                return "https://hastebin.com/" + result["key"]
            else:
                return "Error with creating Hastebin. Status: %s" % resp.status

    def tick(self, opt, label = None):
        emoji = '\✔ ' if opt else '\❌'
        if label is not None:
            return f'{emoji}: {label}'
        return emoji

    async def cog_check(self, ctx):
        if ctx.message.author.id == 98141664303927296: return True
        return True

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.wait_until_ready()
        channel = discord.utils.find(lambda c: type(c) == discord.TextChannel and c.name in self.channels and c.permissions_for(guild.me).send_messages, guild.channels) # Main Chat
        invite = None
        try: invite = (await guild.invites())[0]
        except Exception: pass
        if channel:
            if channel.permissions_for(guild.me).embed_links:
                em = discord.Embed(color=discord.Color.green())
                em.description = f"Hello! This is an unofficial Hypixel Bot! :wave::skin-tone-1:\n\n" \
                                 f"Thank you for adding me to the #{len(self.bot.guilds)} server!\n" \
                                 f"I provide multiple features that range from automatic management of Hypixel Rank roles to displaying personal stats.\n\n" \
                                 f"For a full list of commands, just type `h!help`.\n" \
                                 f"You can also use `h!help [command]` for help about a specific command.\n\n" \
                                 f"Support, feedback and reporting of bugs can be sent on [my support server](https://hypixelbot.fun/discord)!\n\n" \
                                 f"If you like the bot remember to [upvote](http://hypixelbot.fun/vote) it, that helps a lot.\n\n"
                await channel.send(embed=em)
            else:
                message = f'Hello! This is an unofficial Hypixel Bot! :wave::skin-tone-1:\n\n' \
                          f'Thank you for adding me to the #{len(self.bot.guilds)} server!\n' \
                          f'I provide multiple features that range from managing Hypixel Rank\'s roles to displaying personal stats.\n\n' \
                          f'For a full list of commands, just type `h!help`.\n' \
                          f'You can also use `h!help [command]` for help about a specific command.\n\n' \
                          f'Support, feedback and reporting of bugs can be sent on my support server! `<https://hypixelbot.fun/discord>`\n\n' \
                          f'If you like the bot remember to upvote it, that helps a lot.\n' \
                          f'<http://hypixelbot.fun/vote>'
                await channel.send(message)
        members = Counter([m.bot for m in guild.members])
        em = discord.Embed(colour=discord.Colour.orange())
        em.title = f"✅ I've joined a guild! [{len(self.bot.guilds)}]"
        if guild.icon: em.set_thumbnail(url=guild.icon_url)
        else: em.set_thumbnail(url='https://image.ibb.co/bV1jBV/image.png')
        em.set_footer(text='⏱').timestamp = datetime.utcnow()

        webhook = Webhook.from_url(self.bot.webhooks['guilds-joined2'], adapter=AsyncWebhookAdapter(self.bot.session))
        em.description = f"\💬 **{guild.name}** ({guild.id})\n" \
                         f"\👑 **{guild.owner}**\n" \
                         f"\👥 **{guild.member_count-members[True]}** Member{'s' if guild.member_count-members[True] != 1 else ''}\n" \
                         f"\🤖 **{members[True]}** Robot{'s' if members[True] != 1 else ''}\n"
        await webhook.send(embed=em, username=str(self.bot.user), avatar_url=self.bot.user.avatar_url)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.wait_until_ready()
        members = Counter([m.bot for m in guild.members])
        webhook = Webhook.from_url(self.bot.webhooks['guilds-joined'], adapter=AsyncWebhookAdapter(self.bot.session))
        em = discord.Embed(colour=discord.Colour.red())
        em.title = f"❌ I've left a guild! [{len(self.bot.guilds)}]"
        em.description = f"\💬 **{guild.name}** ({guild.id})\n" \
                  f"\👑 **{guild.owner}**\n" \
                  f"\👥 **{guild.member_count-members[True]}** Member{'s' if guild.member_count-members[True] != 1 else ''}\n"
        if members[True] > 0:
            link = await self.hastebin('\n'.join(f"{b} ({b.id})" for b in guild.members if b.bot))
            if str(link).startswith('http'): em.description += f"\🤖 [**{members[True]}** Robot{'s' if members[True] != 1 else ''}]({link})\n"
            else: em.description += f"\🤖 **{members[True]}** Robot{'s' if members[True] != 1 else ''}\n"
        else: em.description += f"\🤖 **{members[True]}** Robot{'s' if members[True] != 1 else ''}\n"
        if guild.icon: em.set_thumbnail(url=guild.icon_url)
        else: em.set_thumbnail(url='https://image.ibb.co/bV1jBV/image.png')
        em.set_footer(text='⏱').timestamp = datetime.utcnow()
        await webhook.send(embed=em, username=str(self.bot.user), avatar_url=self.bot.user.avatar_url)
        await self.bot.pool.execute('delete from prefixes where guildid=$1', guild.id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.wait_until_ready()
        if member.guild.id in await self.bot.settings().hypixelRoles():
            guild = member.guild
            user = await self.bot.pool.fetchrow('select useruuid from public.hypixel where userid=$1', member.id)
            ranksdb = await self.bot.pool.fetchrow('select * from settings.hypixelroles where guildid=$1', guild.id)
            if str(member.id) in self.bot.rankCache:
                rank = self.bot.rankCache[str(member.id)].lower()
                logging.info('DEBUG: OnJoin Cached Rank - ' + rank)
                try: await member.add_roles(discord.utils.get(guild.roles, id=ranksdb[rank]))
                except: await member.add_roles(discord.utils.get(guild.roles, id=ranksdb['member']))
            elif user:
                uuid = user['useruuid']
                async with  self.bot.session.get(f"https://api.hypixel.net/player?uuid={uuid}&key={random.choice(load_config()['hypixel'])}") as r:
                    json = await r.json()
                    if json['success']:
                        rank = getRank(json['player'])['rank'].lower()
                        if rank in ['helper', 'mod', 'admin']: rank = 'hypixel ' + rank
                        logging.info('DEBUG: OnJoin Rank - ' + rank)
                        self.bot.rankCache[str(member.id)] = rank
                        try: await member.add_roles(discord.utils.get(guild.roles, id=ranksdb[rank.lower()]))
                        except: await member.add_roles(discord.utils.get(guild.roles, id=ranksdb['member']))
        if member.guild.id != self.HypixelGuild: return
        if member.bot: return await member.add_roles(discord.Object(id=self.HypixelRole))
        await member.add_roles(discord.Object(id=424280966174081044))
        webhook = Webhook.from_url(self.bot.webhooks['welcome-goodbye'], adapter=AsyncWebhookAdapter(self.bot.session))
        em = discord.Embed(color=discord.Color.green(), description=f'**{member.name}#{member.discriminator}** has joined the server.')
        em.set_footer(text=f'User Join ({member.guild.member_count})', icon_url=member.avatar_url).timestamp = datetime.utcnow()
        await webhook.send(embed=em, username=str(self.bot.user), avatar_url=self.bot.user.avatar_url)
        await member.send('Thank you for joining my server.\n'
                          '**Note**: Neither the Discord Server or Discord bot are owned by Hypixel Inc.\n'
                          'If you need help with the Hypixel Server itself, refer to the forums instead.\n'
                          '<https://hypixel.net/forums/>')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.bot.wait_until_ready()
        if member.id == 350320214262677504: return
        if member.guild.id != self.HypixelGuild: return
        webhook = Webhook.from_url(self.bot.webhooks['welcome-goodbye'], adapter=AsyncWebhookAdapter(self.bot.session))
        em = discord.Embed(color=discord.Color.red(), description=f'**{member.name}#{member.discriminator}** has left the server.')
        em.timestamp = datetime.utcnow()
        await webhook.send(embed=em, username=str(self.bot.user), avatar_url=self.bot.user.avatar_url)

    # Extra on message events
    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()

        if message.author.bot: return

        # Ignore
        if type(message.channel) != discord.channel.DMChannel and \
                message.guild.id in self.bot.ignored.list and message.channel.id in self.bot.ignored.list[message.guild.id]:
            return

        # Converts a mention into help command.
        if message.mentions and message.mentions[0].id == self.bot.user.id and type(message.channel) == discord.TextChannel:
            if len(message.mentions) == 1 and len(message.content.split()) == 1:
                message.content = f'<@{self.bot.user.id}> help'
                ctx = await self.bot.get_context(message, cls = context.Context)
                await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            if before.guild.id != self.HypixelGuild: return
            if before.roles == after.roles: return
            lr_diff = lambda l, r: list(set(l).difference(r))
            added, removed = lr_diff(after.roles, before.roles), lr_diff(before.roles, after.roles)
            if len(added) > len(removed):
                if 'Tier' not in added[0].name: return
                await self.bot.pool.execute(f"INSERT INTO donators(userid, tier, active) VALUES({before.id}, {int(added[0].name[-1])}, true) "
                                            f"ON CONFLICT (userid) DO UPDATE SET tier = excluded.tier, active=true")
            elif len(added) < len(removed):
                if 'Tier' not in removed[0].name: return
                await self.bot.pool.execute('update donators set active=false where userid=$1', before.id)
        except Exception as error: print(error)

    # Set/cycle game
    async def loop_game(self):
        await self.bot.wait_until_ready()
        next_game = 0
        # for shard in self.bot.shards: next_game[shard] = 0
        while True:
            try:
                games = ['h!help | @hypixel', f'over {len(self.bot.guilds)} servers.']
                if next_game + 1 == len(games): next_game = 0
                else: next_game += 1
                await self.bot.change_presence(activity=discord.Activity(name=games[next_game], type=3))
                await asyncio.sleep(300)
                # guilds = Counter([g.shard_id for g in self.bot.guilds])
                # for shard in self.bot.shards:
                #     games = ['h!help | @hypixel', f'over {guilds[shard]} servers.']
                #     if next_game[shard] + 1 == len(games): next_game[shard] = 0
                #     else: next_game[shard] += 1
                #     await self.bot.change_presence(activity = discord.Activity(name = games[next_game[shard]], type = 3), shard_id=shard)
                #     await asyncio.sleep(60)
            except Exception: continue

def setup(bot):
    if bot.platform == 'Windows': return
    e = Events(bot)
    # bot.loop.create_task(e.loop_game())
    bot.add_cog(e)
