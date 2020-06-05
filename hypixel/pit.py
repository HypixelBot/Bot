import gzip
import math
import random

import datetime
import re
import zlib
from ast import literal_eval
from collections import Counter
from uuid import UUID

import cogs.utils.hypixelcommands as Hypixel
from cogs.utils import jnbt
from cogs.utils.checks import *
from cogs.utils.dataIO import dataIO
from hypixel.utils.functions import *


def lbFooter(ctx):
    return f"\n\n__Note__: If a user doesn't show up, run `{ctx.prefix}pit [user]`."

class Pit(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)
        self.usernameCache = []
        self.pitMaster = dataIO.load_json('settings/pitMaster.json')
        self.config = load_config()
        self.footer = 'Hypixel Bot | Made with ❤ by Ice#5555 and McPqndq#1055'

    @commands.command(hidden=True, enabled=False)
    async def HiddenPit(self, ctx, user):
        async with ctx.typing():
            start = datetime.datetime.now()
            player = await self.utils.findUser(ctx, user)
            if type(player) != Player: return
            playerJSON = player.JSON
            if "stats" not in playerJSON or "Pit" not in playerJSON["stats"]: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Pit before.")
            position = await self.bot.pool.fetchrow(f"""select *
                                                                from (
                                                                   select uuid,
                                                                          row_number() over( order by xp desc ) as "Exp",
                                                                          row_number() over( order by cash_earned desc ) as "Lifetime Gold",
                                                                          row_number() over( order by playtime_minutes desc ) as "Playtime",
                                                                          row_number() over( order by kills desc ) as "Kills",
                                                                          row_number() over( order by deaths desc ) as "Deaths",
                                                                          row_number() over( order by renown desc ) as "Renown Earned",
                                                                          row_number() over( order by left_clicks desc ) as "Left Clicks",
                                                                          row_number() over( order by contracts_completed desc ) as "Contracts Completed",
                                                                          row_number() over( order by chat_messages desc ) as "Chat Messages",
                                                                          row_number() over( order by max_streak desc ) as "Highest Streak",
                                                                          row_number() over( order by bounty desc ) as "Bounty"
                                                                   from pit.leaderboards
                                                                ) result
                                                                where uuid = '{playerJSON["uuid"]}';""")
            if position: position = dict(position)
            else: position = {}
            playerJSON = player.JSON
            playerRank = player.getRank()
            playerName = player.getName()
            playerSession = player.getSession()
            onlineStatus = player.getOnlineStatus()
            p = PIT(playerJSON['stats']['Pit'])
            stats = p.stats()
            if playerRank["rank"] == 'Youtuber': colour = Hypixel.Commands(self.bot).rank["RED"]
            else: colour = stats.getColour()
            if playerSession and 'gameType' in playerSession: footer = f'Currently in a {playerSession["gameType"].title()} game'; onlineStatus = True
            else: footer = self.footer
            if onlineStatus: footer_url = 'https://image.ibb.co/h9VNfq/image.png'
            else: footer_url = 'https://image.ibb.co/hwheRV/image.png'
            emb = {
                'embed': {
                    'title': f'{"[" + playerRank["prefix"] + "]" if playerRank["prefix"] else "[" + playerRank["rank"] + "]"} {stats.aliance + " "}{playerName}' if playerRank["rank"] != 'Non' else playerName,
                    'url': f'https://pitpanda.rocks/players/{UUID(player.UUID)}',
                    'description': '',
                    'color': colour
                },
                'footer': {
                    'text': footer,
                    'icon_url': footer_url
                },
                'thumbnail': 'https://i.ibb.co/pvLDbLR/Prototype-64.png',
                'pages': {
                    '0': [
                        {'name': 'Level', 'value': (f"[{int_to_Roman(stats.prestige)}-{stats.level}] " if stats.prestige else stats.level)},
                        {'name': 'Total XP' + (f" `#{position['Exp']}`" if 'Exp' in position else ''), 'value': f"{stats.xp:,}"},
                        {'name': 'Remaining XP to 120', 'value': f"{stats.xpRemaining:,}"} if stats.xpRemaining != 0 else {},
                        {'name': 'Gold' + (f" `#{position['Lifetime Gold']}`" if 'Lifetime Gold' in position else ''), 'value': f"{stats.cash:,.2f}g"},
                        {'name': 'Prestige Gold Req', 'value': f"{stats.goldOnPrestige:,.2f}/{stats.goldRequired:,}"} if stats.goldRequired else {},
                        {'name': 'Kills'+ (f" `#{position['Kills']}`" if 'Kills' in position else ''), 'value': f"{stats.kills:,}" if stats.kills else 'N/A'},
                        {'name': 'Deaths' + (f" `#{position['Deaths']}`" if 'Deaths' in position else ''), 'value': f"{stats.deaths:,}" if stats.deaths else 'N/A'},
                        {'name': 'KDR', 'value': f"{(int(stats.kills) / int(stats.deaths)):.2f}" if stats.kills and stats.deaths else 'N/A'},
                        {'name': 'Renown / Total' + (f" `#{position['Renown Earned']}`" if 'Renown Earned' in position else ''), 'value': (f"{stats.renown:,}" if stats.renown else '0') + (f" [{stats.totalRenown:,}]" if stats.totalRenown else "")},
                        {'name': 'Playtime' + (f" `#{position['Playtime']}`" if 'Playtime' in position else ''), 'value': stats.playtime},
                        {'name': 'Trade Limit', 'value': f'{stats.tradeGold:,}/50,000g ({stats.tradeCount}/12)'},
                        {'name': 'Bounty' + (f" `#{position['Bounty']}`" if 'Bounty' in position else ''), 'value': f"{stats.bounty:,}g"} if stats.bounty else {},
                    ],
                },
                # 'image': f'https://visage.surgeplay.com/full/256/{playerName}'
            }
            embeds = {}
            embed = discord.Embed(**emb["embed"])
            embed.set_thumbnail(url=emb["thumbnail"])
            for page in range(len(emb["pages"])):
                for field in emb["pages"][str(page)]:
                    if 'description' in field:
                        embed.description = field["description"]
                    elif field:
                        embed.add_field(**field)
                if 'image' in emb:
                    embed.set_image(url=emb["image"])
                embed.set_footer(text=emb["footer"]["text"], icon_url=emb["footer"]["icon_url"])
                embeds[page] = embed
                del embed
                embed = discord.Embed(**emb["embed"])
                embed.set_thumbnail(url=emb["thumbnail"])
            time_taken = datetime.datetime.now() - start
            logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds=embeds)
        await self.updateLeaderboard(player)
        await self.bot.pool.execute("""with upsert as (update usernames set username=$1, uuid=$2  where uuid=$2 returning *)
                                        insert into usernames(username, uuid) select $1, $2 where not exists (select * from upsert)""", player.getName(), playerJSON['uuid'])

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitContract(self, ctx, user):
        async with ctx.typing():
            start = datetime.datetime.now()
            permissions = ctx.channel.permissions_for(ctx.me)
            if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
            if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
            if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
            if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
            if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
                data = await self.utils._get_user(ctx)
                if not data: return
                user = data['useruuid']
            try: player = self.bot.hypixel.Player(user)
            except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
            except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
            playerJSON = player.JSON
            if "quests" not in playerJSON: return await ctx.send(f"Doesn't look like `{user}` has completed quests.")
            quests = playerJSON['quests']
            quests = dict(filter(lambda x: 'pit' in x[0], quests.items()))
            if not quests: return await ctx.send(f"Doesn't look like `{user}` has completed quests.")
            txt = ''
            for k, v in quests.items():
                newK = vars(self.pitMaster.Contracts)[k]
                txt += f'\n**{newK.title}**:'
                if 'completions' in v: txt += f"\n\tCompletions: {len(v['completions'])}"
                if 'active' in v:
                    txt += f"\n\tStarted: {time.human_timedelta(datetime.datetime.fromtimestamp(v['active']['started'] / 1000), short=True)}"
                    if v['active']['objectives']:
                        txt += '\n\t' + '\n\t'.join([f"{newK.objectives.title}: {y}/{newK.objectives.goal}" for x, y in v['active']['objectives'].items()])
                txt+='\n'
            # @todo actually do contracts instead of only quests
            await ctx.send(txt)
            # embeds = Hypixel.Commands(self.bot).pit(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
            # await self.utils.send(ctx, embeds=embeds)
            # await Hypixel.Commands(self.bot).updateLeaderboard(player)

    # @commands.command(hidden=True, enabled=False)
    # async def HiddenPitKills(self, ctx, user):
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
    #         data = await self.utils._get_user(ctx)
    #         if not data: return
    #         user = data['useruuid']
    #     try: player = self.bot.hypixel.Player(user)
    #     except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
    #     except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
    #     playerJSON = player.JSON
    #     playerRank = player.getRank()
    #     if "stats" not in playerJSON or "Pit" not in playerJSON["stats"]: return await ctx.send(f"Doesn't look like `{user}` has played Pit before.")
    #     p = PIT(playerJSON['stats']['Pit'])
    #     stats = p.stats()
    #     if playerRank["rank"] == 'Youtuber': colour = Hypixel.Commands(self.bot).rank["RED"]
    #     else: colour = stats.getColour()
    #     pStats = playerJSON['stats']['Pit']['profile']
    #     if 'recent_kills' not in pStats: return await ctx.send('No recent kills found.')
    #     rKills = sorted(pStats['recent_kills'], key=lambda x: -x['timestamp'])[:15]
    #     async def getStats(uuid, client):
    #         async def get_json(client, url):
    #             async with client.get(url) as response:
    #                 assert response.status == 200
    #                 return await response.read()
    #         data = await get_json(client, f'https://api.hypixel.net/player?uuid={uuid}&key={random.choice(self.config["hypixel"])}')
    #         j = json.loads(data.decode('utf-8'))
    #         p = PIT(j['player']['stats']['Pit'])
    #         stats = p.stats()
    #         lvl = f"[{int_to_Roman(stats.prestige)}-{stats.level}] " if stats.prestige else f'[{stats.level}] '
    #         username = j['player']['displayname']
    #         return f"{lvl}[{username}](https://pitpanda.rocks/players/{UUID(j['player']['uuid'])})"
    #     em = discord.Embed(title='Recent Kills', colour=colour)
    #     em.description = ''
    #     em.set_author(name=player.getName(), url=f'https://pitpanda.rocks/players/{UUID(player.UUID)}', icon_url=f'https://crafatar.com/avatars/{playerJSON["uuid"]}?overlay=true')
    #     msg = await ctx.send(embed=em)
    #     cStart = datetime.datetime.now()
    #     for i in rKills:
    #         x = await getStats(i['victim'], self.bot.session)
    #         em.description += x+'\n'
    #         cTaken = (datetime.datetime.now() - cStart).total_seconds()
    #         if cTaken > 1:
    #             cStart = datetime.datetime.now()
    #             await msg.edit(embed=em)
    #     await msg.edit(embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitPosition(self, ctx, user):
        async with ctx.typing():
            start = datetime.datetime.now()
            permissions = ctx.channel.permissions_for(ctx.me)
            if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
            if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
            if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
            if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
            if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
                data = await self.utils._get_user(ctx)
                if not data: return
                user = data['useruuid']
            try: player = self.bot.hypixel.Player(user)
            except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
            except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
            playerJSON = player.JSON
            playerRank = player.getRank()
            if "stats" not in playerJSON or "Pit" not in playerJSON["stats"]: return await ctx.send(f"Doesn't look like `{user}` has played Pit before.")
            p = PIT(playerJSON['stats']['Pit'])
            stats = p.stats()
            if playerRank["rank"] == 'Youtuber': colour = Hypixel.Commands(self.bot).rank["RED"]
            else: colour = stats.getColour()
            data = await self.bot.pool.fetchrow(f"""select *
                                                    from (
                                                       select uuid,
                                                              row_number() over( order by xp desc ) as "Exp",
                                                              row_number() over( order by cash_earned desc ) as "Lifetime Gold",
                                                              row_number() over( order by playtime_minutes desc ) as "Playtime",
                                                              row_number() over( order by kills desc ) as "Kills",
                                                              row_number() over( order by deaths desc ) as "Deaths",
                                                              row_number() over( order by renown desc ) as "Renown Earned",
                                                              row_number() over( order by left_clicks desc ) as "Left Clicks",
                                                              row_number() over( order by contracts_completed desc ) as "Contracts Completed",
                                                              row_number() over( order by chat_messages desc ) as "Chat Messages",
                                                              row_number() over( order by max_streak desc ) as "Highest Streak",
                                                              row_number() over( order by bounty desc ) as "Bounty"
                                                       from pit.leaderboards
                                                    ) result
                                                    where uuid = '{playerJSON["uuid"]}';""")
            if not data: return await ctx.send(f"Oops, looks like I don't have any information about {player.getName()} position.")
            data = dict(data)
            data.pop('uuid')
            if data['Bounty'] > 5: data.pop('Bounty')
            em = discord.Embed(title='Leaderboard Positions', description='\n'.join([f"{y}: `#{z}`" for y, z in sorted(data.items(), key=lambda x: (x[1], len(x[0])))]), colour=colour)
            em.set_author(name=player.getName(), url=f'https://pitpanda.rocks/players/{UUID(player.UUID)}', icon_url=f'https://crafatar.com/avatars/{playerJSON["uuid"]}?overlay=true')
            await ctx.send(embed=em)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitProgress(self, ctx, user):
        async with ctx.typing():
            start = datetime.datetime.now()
            permissions = ctx.channel.permissions_for(ctx.me)
            if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
            if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
            if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
            if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
            if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
                data = await self.utils._get_user(ctx)
                if not data: return
                user = data['useruuid']
            try: player = self.bot.hypixel.Player(user)
            except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
            except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
            playerJSON = player.JSON
            playerRank = player.getRank()
            if "stats" not in playerJSON or "Pit" not in playerJSON["stats"]: return await ctx.send(f"Doesn't look like `{user}` has played Pit before.")
            p = PIT(playerJSON['stats']['Pit'])
            stats = p.stats()
            if playerRank["rank"] == 'Youtuber': colour = Hypixel.Commands(self.bot).rank["RED"]
            else: colour = stats.getColour()
            em = discord.Embed(title=f'{player.getName()} progression',  colour=colour)
            em.set_thumbnail(url='https://i.ibb.co/pvLDbLR/Prototype-64.png')
            em.set_author(name=player.getName(), url=f'https://pitpanda.rocks/players/{UUID(player.UUID)}', icon_url=f'https://crafatar.com/avatars/{playerJSON["uuid"]}?overlay=true')
            gold = stats.JSON['pit_stats_ptl']['cash_earned']/(stats.JSON['pit_stats_ptl']['playtime_minutes']/60)
            exp = stats.JSON['profile']['xp']/(stats.JSON['pit_stats_ptl']['playtime_minutes']/60)
            em.add_field(name='Level', value=(f"[{int_to_Roman(stats.prestige)}-{stats.level}] " if stats.prestige else stats.level), inline=False)
            em.add_field(name='Gold/Hour', value=f"{gold:,.2f}")
            em.add_field(name='Exp/Hour', value=f"{exp:,.2f}")
            # if stats.xpRemaining: em.add_field(name='Exp to 120', value=stats.xpRemaining)
            em.add_field(name='Gold Progress', value=f"{(stats.goldOnPrestige*100)/stats.goldRequired:,.2f}%" if stats.goldRequired else '∞')
            em.add_field(name='Exp Progress', value=f"{((stats.xp - stats.xp_on_prestige)*100)/stats.expRequired:,.2f}%")
            goldLeft = stats.goldRequired-stats.goldOnPrestige
            expLeft = stats.expRequired-(stats.xp - stats.xp_on_prestige)
            em.add_field(name='Gold Left', value=f"{goldLeft:,.2f}\n[~{goldLeft/gold:,.1f} hours]" if goldLeft > 0 else 'Completed')
            em.add_field(name='Exp Left', value=f"{expLeft:,.0f}\n[~{expLeft/exp:,.1f} hours]" if expLeft > 0 else 'Completed')
        await ctx.send(embed=em)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    ### Leaderboards ###

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopExp(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select A.uuid, B.username, A.xp
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.xp desc, A.punlock limit 15""")
        data = [{'uuid': x['uuid'], 'username': x['username'], 'exp': x['xp']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["exp"]:,}' for i, m in enumerate(data)])
        await ctx.send(f"Top **Experience** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopCash(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select A.uuid, B.username, A.cash_earned
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.cash_earned desc limit 10""")
        data = [{'uuid': x['uuid'], 'username': x['username'], 'gold': x['cash_earned']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["gold"]:,}g' for i, m in enumerate(data)])
        await ctx.send(f"Top **Gold** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopPlaytime(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select B.username, A.playtime_minutes as playtime
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.playtime_minutes desc limit 10""")
        data = [{'username': x['username'], 'playtime': '{:,}h {:02d}m'.format(*divmod(x['playtime'], 60))} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["playtime"]}' for i, m in enumerate(data)])
        await ctx.send(f"Top **Playtime** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopKills(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select B.username, A.kills
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.kills desc limit 10""")
        data = [{'username': x['username'], 'kills': x['kills']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["kills"]:,}' for i, m in enumerate(data)])
        await ctx.send(f"Top **Kills** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopRenown(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select B.username, A.renown
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.renown desc limit 10""")
        data = [{'username': x['username'], 'renown': x['renown']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["renown"]:,}' for i, m in enumerate(data)])
        await ctx.send(f"Top **Renown** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopClicks(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select B.username, A.left_clicks
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.left_clicks desc limit 10""")
        data = [{'username': x['username'], 'clicks': x['left_clicks']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["clicks"]:,}' for i, m in enumerate(data)])
        await ctx.send(f"Top **Clicks** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopMessages(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select B.username, A.chat_messages
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.chat_messages desc limit 10""")
        data = [{'username': x['username'], 'messages': x['chat_messages']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["messages"]:,}' for i, m in enumerate(data)])
        await ctx.send(f"Top **Messages** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopStreak(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select B.username, A.max_streak
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.max_streak desc limit 10""")
        data = [{'username': x['username'], 'streak': x['max_streak']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["streak"]:,}' for i, m in enumerate(data)])
        await ctx.send(f"Top **Streak** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopContracts(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select B.username, A.contracts_completed
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.contracts_completed desc limit 10""")
        data = [{'username': x['username'], 'contracts': x['contracts_completed']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["contracts"]:,}' for i, m in enumerate(data)])
        await ctx.send(f"Top **Completed Contracts** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopBounty(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select A.uuid, B.username, A.bounty
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.bounty desc limit 10""")
        data = [{'uuid': x['uuid'], 'username': x['username'], 'bounty': x['bounty']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["bounty"]:,}g' for i, m in enumerate(data)])
        await ctx.send(f"Top **BOUNTIES** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitTopDeaths(self, ctx):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        data = await self.bot.pool.fetch("""select A.uuid, B.username, A.deaths
                                            from pit.leaderboards A, usernames B
                                            where A.uuid = B.uuid
                                            order by A.deaths desc limit 10""")
        data = [{'uuid': x['uuid'], 'username': x['username'], 'deaths': x['deaths']} for x in data]
        top = '\n'.join([f'**[{i + 1}]** {m["username"]}: {m["deaths"]:,}' for i, m in enumerate(data)])
        await ctx.send(f"Top **DEATHS** Leaderboard\n\n{top}{lbFooter(ctx)}")
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    async def updateLeaderboard(self, player):
        pJSON = player.JSON
        pPIT = pJSON['stats']['Pit'] if 'stats' in pJSON and 'Pit' in pJSON['stats'] else None
        if not pPIT: return
        pProfile = pPIT['profile']
        pStats = Stats(pPIT)
        pSTATS = pPIT['pit_stats_ptl'] if 'pit_stats_ptl' in pPIT else {}
        y = {'uuid': pJSON['uuid'],
             'xp': pStats.xp, 'cash_earned': pStats.cash_earned, 'playtime_minutes': pStats.playtime_minutes, 'kills': pStats.kills, 'mystics': pStats.enchanted_tier1+pStats.enchanted_tier2+pStats.enchanted_tier3,
             'renown': pStats.totalRenown, 'dark_pants_crated': pSTATS['dark_pants_crated'] if 'dark_pants_crated' in pSTATS else 0, 'left_clicks': pStats.left_clicks, 'chat_messages': pStats.chat_messages,
             'max_streak': pStats.max_streak, 'contracts_completed': pStats.contracts_completed,
             'bounty': sum([x['amount'] for x in pProfile['bounties']]) if 'bounties' in pProfile else 0,
             'punlock': datetime.datetime.fromtimestamp(pProfile['prestiges'][-1]['timestamp']/1000) if 'prestiges' in pProfile else None,
             'deaths': pStats.deaths}
        await self.bot.pool.execute("""INSERT INTO pit.leaderboards
                                        VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                                        ON CONFLICT (uuid) DO UPDATE
                                          SET xp = excluded.xp,
                                              cash_earned = excluded.cash_earned, playtime_minutes = excluded.playtime_minutes, kills = excluded.kills,
                                               mystics = excluded.mystics, renown = excluded.renown, dark_pants_crated = excluded.dark_pants_crated, 
                                               left_clicks = excluded.left_clicks, chat_messages = excluded.chat_messages, max_streak = excluded.max_streak,
                                               contracts_completed = excluded.contracts_completed, bounty = excluded.bounty, punlock = excluded.punlock, deaths = excluded.deaths;
                                        """, *(x for x in y.values()))
        print(f'Updated: {pJSON["displayname"]}', end=' ')

class PIT:

    def __init__(self, JSON):
        self.JSON = JSON
        if 'profile' not in self.JSON:
            raise Exception('Not a valid json.')
        self.Array = None
        self.NBT = None

    def twoscomplement_to_unsigned(self, i):
        return i % 256

    def decompress(self):
        result = bytes(map(self.twoscomplement_to_unsigned, self.Array))
        decompressed_data = zlib.decompress(result, 16 + zlib.MAX_WBITS)

        # write bytes to zip file in memory
        myio = BytesIO()
        g = gzip.GzipFile(fileobj=myio, mode='wb')
        g.write(decompressed_data)
        g.close()
        myio.seek(0)
        # read bytes from zip file in memory
        g = gzip.GzipFile(fileobj=myio, mode='rb')

        self.NBT = jnbt.read(g)

        return self.NBT

    def death_recap(self):
        msg = b''
        if not self.NBT: self.decompress()
        for a in self.NBT.values():
            for b in a:
                for c in b.values():
                    if type(c) != jnbt.tag.TAG_Compound:
                        continue
                    else:
                        for d in c.values():
                            if type(d) != jnbt.tag.TAG_List: continue
                            for e in d:
                                e = literal_eval(re.sub('(§.)+', '', str(e)).replace('false', 'False').replace('true', 'True'))
                                for f in e:
                                    if type(f) == str:
                                        x = str.encode(f)
                                        if x in [b'']: continue
                                        msg += x
                                    else:
                                        if 'hoverEvent' in f:
                                            for g in f.values():
                                                if type(g) == bool: continue
                                                if type(g) == str:
                                                    str.encode(g)
                                                    continue
                                                for h in g.values():
                                                    if type(h) == str: continue
                                                    if 'text' in h:
                                                        msg += str.encode(h['text'])
                                                    if 'extra' in h:
                                                        for i in h['extra']:
                                                            msg += str.encode(i['text'])
                                        else:
                                            if type(f) == str: continue
                                            if 'text' in f:
                                                msg += str.encode(f['text'])
                                            if 'extra' in f:
                                                for g in f['extra']:
                                                    msg += str.encode(g['text'])
        return msg

    def inv_armor(self):
        items = []
        if not self.NBT: self.decompress()
        for a in self.NBT.values():
            for b in a:
                if len(b) < 1: continue
                item = {}
                for c in b:
                    if type(b.get(c)) != jnbt.tag.TAG_Compound:
                        item[c] = b.get(c).value
                    else:
                        c = b.get(c)
                        for d in c:
                            if 'tag' not in item: item['tag'] = {}
                            if type(c.get(d)) != jnbt.tag.TAG_Compound:
                                item['tag'][d] = c.get(d).value
                            else:
                                for x in c.get(d):
                                    print(x)
                                    x = c.get(d).get(x)
                                    print(x)
                                # print(c.get(d))
                items.append(item)
        return items

    def stats(self):
        return Stats(self.JSON)

def int_to_Roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

class Stats:

    def __init__(self, JSON):
        self.pitMaster = dataIO.load_json('settings/pitMaster.json')

        self.JSON = JSON
        self.profileJSON = self.JSON['profile']
        if 'pit_stats_ptl' in self.JSON: self.statJSON = self.JSON['pit_stats_ptl']
        else: self.statJSON = {}
        self.kills = self.statJSON['kills'] if 'kills' in self.statJSON else 0
        self.assists = self.statJSON['assists'] if 'assists' in self.statJSON else 0
        self.deaths = self.statJSON['deaths'] if 'deaths' in self.statJSON else 0
        self.xp = self.profileJSON['xp'] if 'xp' in self.profileJSON else 0
        self.prestige = len(self.profileJSON['prestiges']) if 'prestiges' in self.profileJSON else 0
        self.goldRequired = self.pitMaster.Prestiges[self.prestige].GoldReq
        self.expRequired = self.pitMaster.Prestiges[self.prestige].TotalXp
        self.goldOnPrestige = self.profileJSON[f"cash_during_prestige_{self.prestige}"] if f"cash_during_prestige_{self.prestige}" in self.profileJSON else 0
        self.xp_on_prestige = self.profileJSON['prestiges'][self.prestige - 1]['xp_on_prestige'] if self.prestige else 0
        self.xpRemaining = self.pitMaster.Prestiges[self.prestige].TotalXp - (self.xp - self.xp_on_prestige)
        self.level = self.getLevel(self.xp, self.prestige, self.xp_on_prestige) if 'xp' in self.profileJSON else 0
        self.cash = self.profileJSON['cash'] if 'cash' in self.profileJSON else 0
        self.bounty = sum([x['amount'] for x in self.profileJSON['bounties']]) if 'bounties' in self.profileJSON else 0
        self.renown = self.profileJSON['renown'] if 'renown' in self.profileJSON else 0
        if 'renown_unlocks' in self.profileJSON:
            self.totalRenown = self.renown
            for k, v in Counter([k['key'] for k in self.profileJSON['renown_unlocks']]).items():
                self.totalRenown += sum(vars(self.pitMaster.RenownUpgrades)[k].Costs[0:v])
            if 'dark_pants_crated' in self.statJSON:
                self.totalRenown += self.statJSON['dark_pants_crated']*2
        else: self.totalRenown = 0
        self.cash_earned = self.statJSON['cash_earned'] if 'cash_earned' in self.statJSON else 0
        self.enchanted_tier1 = self.statJSON['enchanted_tier1'] if 'enchanted_tier1' in self.statJSON else 0
        self.enchanted_tier2 = self.statJSON['enchanted_tier2'] if 'enchanted_tier2' in self.statJSON else 0
        self.enchanted_tier3 = self.statJSON['enchanted_tier3'] if 'enchanted_tier3' in self.statJSON else 0
        if 'playtime_minutes' in self.statJSON:
            self.playtime_minutes = self.statJSON['playtime_minutes']
            offset_h, offset_m = divmod(self.statJSON['playtime_minutes'], 60)
            self.playtime = '{:}h {:02d}m'.format(abs(offset_h), offset_m)
        else: self.playtime = 'N/A'; self.playtime_minutes = 0
        self.chat_messages = self.statJSON['chat_messages'] if 'chat_messages' in self.statJSON else 0
        self.contracts_completed = self.statJSON['contracts_completed'] if 'contracts_completed' in self.statJSON else 0
        self.left_clicks = self.statJSON['left_clicks'] if 'left_clicks' in self.statJSON else 0
        self.max_streak = self.statJSON['max_streak'] if 'max_streak' in self.statJSON else 0
        self.tradeCount = len([x for x in self.profileJSON['trade_timestamps'] if self.past24hours(x)]) if 'trade_timestamps' in self.profileJSON else 0
        self.tradeGold = sum([x['amount'] for x in self.profileJSON['gold_transactions'] if self.past24hours(x['timestamp'])]) if 'gold_transactions' in self.profileJSON else 0
        self.aliance = self.profileJSON['genesis_allegiance'].title() if 'genesis_allegiance' in self.profileJSON else ''

    def past24hours(self, timestamp):
        seconds = timestamp/1000
        now = datetime.datetime.now().timestamp()
        if (now-seconds) > 86400: return False
        return True

    def getColour(self):
        return discord.Colour(int(self.pitMaster.Prestiges[self.prestige].Color, 0))

    def getStats(self, profile):
        # pprint(profile)
        prestige = len(profile['prestiges']) if 'prestiges' in profile else 0
        xp_on_prestige = profile['prestiges'][prestige - 1]['xp_on_prestige'] if prestige else 0
        exp = profile['xp']
        lvl = self.getLevel(exp, prestige, xp_on_prestige)
        return f"[{int_to_Roman(prestige) + ('-' if prestige else '')}{lvl}]"

    def getLevel(self, exp, prestige, xp_on_prestige):
        if prestige < 3: exp -= prestige * 15
        if prestige in [3, 5, 8]: exp -= 15
        if prestige == 6: exp -= 27.5
        if prestige != 0: exp -= xp_on_prestige  # xp_on_prestige
        sum = lvl = 0
        while exp >= sum:
            if lvl == 120: return lvl
            sum += self.pitMaster.Prestiges[prestige].Multiplier * self.pitMaster.Levels[math.floor(lvl / 10)].Xp
            lvl += 1
        return lvl - 1

def setup(bot):
    u = Pit(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(u.statsUpdate())
    bot.add_cog(u)
