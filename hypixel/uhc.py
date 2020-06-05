import datetime

from hypixel.utils.functions import *


class MurderMystery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenUHC(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "UHC" not in playerJSON["stats"] or len(playerJSON['stats']['UHC']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played UHC before.")
        embeds = self.UHC(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def UHC(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerUHC = playerJSON["stats"]["UHC"]
        if playerRank["rank"] == 'Youtuber':
            colour = self.utils.rank["RED"][0]
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
        embeds = {}
        emb = {
            'embed': {
                'title': f'{"["+playerRank["prefix"]+"]" if playerRank["prefix"] else "["+playerRank["rank"]+"]"} {playerName}' if playerRank["rank"] != 'Non' else playerName,
                'url': f'https://hypixel.net/player/{playerName}',
                'description': '',
                'color': colour
            },
            'footer': {
                'text': footer,
                'icon_url': footer_url
            },
            'thumbnail': 'https://image.ibb.co/nfVKBV/IDxWEQr.png',
            'pages': {
                '0': [
                    {'description': 'UHC Champions'},
                    {'name': 'Coins', 'value': f'{playerUHC["coins"]:,}' if "coins" in playerUHC else 0},
                    {'name': 'Score', 'value': playerUHC["score"] if 'score' in playerUHC else 0},
                    {'name': 'Heads Eaten', 'value': playerUHC["heads_eaten"] if 'heads_eaten' in playerUHC else 0, 'inline': False},

                    {'name': 'Solo Kills', 'value': playerUHC["kills_solo"] if 'kills_solo' in playerUHC else 0},
                    {'name': 'Solo Deaths', 'value': playerUHC["deaths_solo"] if 'deaths_solo' in playerUHC else 0},
                    {'name': 'Solo Wins', 'value': playerUHC["wins_solo"] if 'wins_solo' in playerUHC else 0},
                    {'name': 'Solo Kill/Death Ratio', 'value': f'{int(playerUHC["kills_solo"] if "kills_solo" in playerUHC else 0) / int(playerUHC["deaths_solo"] if "deaths_solo" in playerUHC else 1):.2f}'},

                    {'name': 'Team Kills', 'value': playerUHC["kills"] if 'kills' in playerUHC else 0},
                    {'name': 'Team Deaths', 'value': playerUHC["deaths"] if 'deaths' in playerUHC else 0},
                    {'name': 'Team Wins', 'value': playerUHC["wins"] if 'wins' in playerUHC else 0},
                    {'name': 'Team Kill/Death Ratio', 'value': f'{int(playerUHC["kills"] if "kills" in playerUHC else 0) / int(playerUHC["deaths"] if "deaths" in playerUHC else 1):.2f}'},
                ],
            },
            # 'image': f'https://visage.surgeplay.com/full/256/{playerName}'
        }
        embed = discord.Embed(**emb["embed"])
        embed.set_thumbnail(url=emb["thumbnail"])
        for page in range(len(emb["pages"])):
            for field in emb["pages"][str(page)]:
                if 'description' in field:
                    embed.description = field["description"]
                else:
                    embed.add_field(**field)
            if 'image' in emb:
                embed.set_image(url=emb["image"])
            embed.set_footer(text=emb["footer"]["text"], icon_url=emb["footer"]["icon_url"])
            embeds[page] = embed
            del embed
            embed = discord.Embed(**emb["embed"])
            embed.set_thumbnail(url=emb["thumbnail"])
        return embeds

def setup(bot):
    h = MurderMystery(bot)
    bot.add_cog(h)
