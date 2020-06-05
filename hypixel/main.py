import datetime
import re
from cogs.utils.checks import *

from hypixel.utils.functions import *


class HypixelMain(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenHypixel(self, ctx, user):
        user = user.split()
        if len(user) == 2 and discord.utils.find(lambda c: user[1] in c.aliases or c.name == user[1], discord.utils.find(lambda c: c.name == 'hypixel', self.bot.commands).commands):
            msg = copy.copy(ctx.message)
            msg.content = f'{ctx.prefix}hypixel {user[1]} {user[0]}'

            new_ctx = await self.bot.get_context(msg, cls=context.Context)
            return await self.bot.invoke(new_ctx)

        elif user:
            user = user[0]
        if ctx.invoked_subcommand is None:
            start = datetime.datetime.now()
            data = None
            permissions = ctx.channel.permissions_for(ctx.me)
            if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
            if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
            if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
            if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
                data = await self.utils._get_user(ctx)
                if not data: return
                user = data['useruuid']
            elif not re.fullmatch("([A-Za-z0-9_]+){1,16}", user):
                return await ctx.send("That username doesn't seem to be valid.")
            try:
                player = self.bot.hypixel.Player(user)
            except self.bot.hypixel.PlayerNotFoundException: return await ctx.safe_send(f"Couldn't find the user `{user}`")
            except self.bot.hypixel.HypixelAPIError as error:
                logging.error(error)
                self.bot.hypixel.setKeys(load_config()["hypixel"])
                return await ctx.send('There seems to be an error with the API. Try again later.')
            except self.bot.hypixel.HypixelAPIThrottle: return await ctx.send('There\'s a global throttle. Try again later.')
            playerJSON = player.JSON
            supporter = await self.bot.pool.fetchrow('select B.phrase from hypixel A, donators B where A.userid = B.userid and A.useruuid=$1', playerJSON["uuid"])
            playerRank = player.getRank()
            playerName = player.getName()
            if data:
                txt = f'{"[" + playerRank["prefix"] + "]" if playerRank["prefix"] else "[" + playerRank["rank"] + "]"} {playerName}' if playerRank["rank"] != 'Non' else playerName
                logging.info(txt)
            playerLevel = int(player.getLevel())
            playerLevelPercentage = player.getPercentageToNextLevel()
            playerVersion = player.getMcVersion()
            playerGuildName = player.getGuildName()
            playerKarma = f'{playerJSON["karma"]:,}' if 'karma' in playerJSON else 'Non'
            firstLogin, lastLogin = player.getLogin()
            if firstLogin and lastLogin:
                login = f'`{firstLogin.strftime("%Y-%m-%d")} / {lastLogin.strftime("%Y-%m-%d")}`\n`({time.human_timedelta(lastLogin, short=True)})`'
            else:
                login = '`Non / Non`'
            onlineStatus = player.getOnlineStatus()
            playerSession = player.getSession()
            playerDiscord = await self.utils._get_user_by_uuid(playerJSON['uuid'], ctx)
            if playerRank["rank"] == 'Youtuber':
                colour = self.utils.rank["RED"][0]
            elif playerRank['rank'].title() in ['Helper', 'Moderator', 'Admin']:
                colour = self.utils.rank[playerRank['rank'].upper()][0]
            elif "rankPlusColor" in playerJSON:
                colour = self.utils.rank[playerJSON["rankPlusColor"]][0]
            else:
                colour = 0x55FFFF
            if playerSession and 'gameType' in playerSession:
                footer = f'Currently in a {playerSession["gameType"].title()} game'
                onlineStatus = True
            else:
                footer = self.bot.footer
            if onlineStatus:
                footer_url = 'https://image.ibb.co/h9VNfq/image.png'
            else:
                footer_url = 'https://image.ibb.co/hwheRV/image.png'
            if "socialMedia" in playerJSON and "links" in playerJSON["socialMedia"] and "DISCORD" in playerJSON["socialMedia"]["links"]:
                discordAccount = playerJSON["socialMedia"]["links"]["DISCORD"]
                if re.findall(r'(https?://\S+)', discordAccount):
                    discordAccount = None
            else:
                discordAccount = None
            if "socialMedia" in playerJSON and "links" in playerJSON["socialMedia"] and "HYPIXEL" in playerJSON["socialMedia"]["links"]:
                hypixelAccount = playerJSON["socialMedia"]["links"]["HYPIXEL"]
            else:
                hypixelAccount = None
            embeds = {}
            file = await self.utils.getSkin(playerJSON["uuid"])
            emb = {
                'embed': {
                    'title': f'{"[" + playerRank["prefix"] + "]" if playerRank["prefix"] else "[" + playerRank["rank"] + "]"} {playerName}' if playerRank["rank"] != 'Non' else playerName,
                    'url': f'https://hypixel.net/player/{playerName}',
                    'color': colour,
                    'description': '[Support The Developer](https://www.patreon.com/join/Wonderpants?)'
                },
                'footer': {
                    'text': footer,
                    'icon_url': footer_url
                },
                'thumbnail': 'https://image.ibb.co/emhGrV/Hypixel-Thumbnail.png',
                'pages': {
                    '0': [
                        # {'image': f'attachment://{file.filename}'},
                        {'image': f'https://visage.surgeplay.com/full/256/{player.UUID}'},
                        # {'image': f'https://visage.surgeplay.com/full/256/{playerJSON["uuid"]}'},
                        {'name': 'Rank', 'value': f'`{str(playerRank["rank"]).upper() if playerRank["rank"] not in ["Non", "None"] else playerRank["rank"]}`'},
                        {'name': 'Level', 'value': f'`{playerLevel}.{int(playerLevelPercentage * 100)}`'},
                        {'name': 'Minecraft Version', 'value': f'`{playerVersion}`'},
                        {'name': 'Guild', 'value': f"[{playerGuildName}](https://hypixel.net/guilds/{playerGuildName.replace(' ', '%20')})" if playerGuildName != 'None' else f'`{playerGuildName}`'},
                        {'name': 'Karma', 'value': f'`{playerKarma}`'},
                        {'name': 'First/Last Login', 'value': login},
                        {'name': 'Discord', 'value': playerDiscord} if playerDiscord else {'name': 'Discord', 'value': discordAccount} if discordAccount else None,
                        {'name': 'Forums', 'value': f'[View forum account.]({hypixelAccount})'} if hypixelAccount and hypixelAccount.startswith('https://hypixel.net/members/') else None,
                    ]
                }
            }
            if supporter:
                if supporter['phrase']: emb['embed']['description'] = supporter['phrase']
                emb['thumbnail'] = 'https://i.ibb.co/MPy1s9P/image.png'
            elif playerRank['rank'] in ['MVP+', 'MVP++', 'Helper', 'Moderator', 'Admin']:
                if "rankPlusColor" not in playerJSON: playerJSON["rankPlusColor"] = 'RED'
                if playerRank['rank'].upper() == 'MVP+':
                    emb['thumbnail'] = self.utils.rank[playerJSON["rankPlusColor"]][1]
                elif playerRank['rank'].upper() == 'MVP++':
                    emb['thumbnail'] = self.utils.rank[playerJSON["rankPlusColor"]][2]
                else:
                    emb['thumbnail'] = self.utils.rank[playerRank['rank'].upper()][1]
            if playerJSON["uuid"] in ["9aaad1cac88c4564b95bb18269db19d6"]: emb['thumbnail'] = "https://i.ibb.co/mJ0BTnm/image.png"
            embed = discord.Embed(**emb["embed"])
            embed.set_thumbnail(url=emb["thumbnail"])
            for page in range(len(emb["pages"])):
                for field in emb["pages"][str(page)]:
                    if not field: continue
                    if 'image' in field:
                        embed.set_image(url=field["image"])
                    else:
                        embed.add_field(**field)
                embed.set_footer(text=emb["footer"]["text"], icon_url=emb["footer"]["icon_url"])
                embeds[page] = embed
                # del embed
                embed = discord.Embed(**emb["embed"])
                embed.set_thumbnail(url=emb["thumbnail"])
            time_taken = datetime.datetime.now() - start
            logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
            await self.utils.send(ctx, embeds=embeds)
            await self.utils._discord_account(ctx, playerJSON, playerRank["rank"])
            await self.bot.pool.execute(f"""INSERT INTO usernames VALUES('{playerJSON["uuid"]}', '{playerName}') ON CONFLICT (uuid) DO UPDATE SET username = excluded.username""")

    @commands.command(hidden=True, enabled=False)
    async def HiddenPitKeys(self, ctx):
        keys = load_config()["hypixel"]
        count = queries = 0
        em = discord.Embed(color=discord.Color.orange(), description=f'**Hypixel API Keys Usage**:\n\n')
        message = None
        urls = [f'https://api.hypixel.net/key?key={key}' for key in keys]

        async def get_json(url):
            async with self.bot.session.get(url) as response:
                assert response.status == 200
                return await response.read()

        cStart = datetime.datetime.now()
        for url in urls:
            data = await get_json(url)
            j = json.loads(data.decode('utf-8'))
            if j['success']:
                j = j['record']
                Qpm = 'queriesInPastMin' in [x for x in j]
                # username = await Mojang(self.bot.session).getUser(uuid=j['ownerUuid'])
                username = '||No owner for you||'
                queries += j['totalQueries']
                em.description += f"Owner: {username}\n\u200b\t• Total Queries: {j['totalQueries']:,}\n"
                if Qpm:
                    em.description += f"\u200b\t• Queries in Past Min: {j['queriesInPastMin']}\n\n"
                else:
                    em.description += '\n'
                count += 1
                em.set_footer(text=f"{count}/{len(keys)} Keys working!")
                cTaken = (datetime.datetime.now() - cStart).total_seconds()
                if cTaken > 1:
                    print(cTaken)
                    if not message:
                        message = await ctx.send(embed=em)
                    else:
                        await message.edit(content=None, embed=em)
                    cStart = datetime.datetime.now()
        em.description += f'\nTotal Queries: {queries:,}'
        if not message:
            await ctx.send(embed=em)
        else:
            await message.edit(content=None, embed=em)

def setup(bot):
    h = HypixelMain(bot)
    bot.add_cog(h)
