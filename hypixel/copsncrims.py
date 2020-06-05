import datetime

from hypixel.utils.functions import *


class CopsAndCrims(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenCopsAndCrims(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "MCGO" not in playerJSON["stats"] or len(playerJSON['stats']['MCGO']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Cops & Crimes before.")
        embeds = self.CopsAndCrims(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def CopsAndCrims(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerMCGO = playerJSON["stats"]["MCGO"]
        if playerRank["rank"] == 'Youtuber':
            colour = self.utils.rank["RED"][0]
        elif "rankPlusColor" in playerJSON:
            colour = self.utils.rank[playerJSON["rankPlusColor"]][0]
        else:
            colour = 0x55FFFF
        if playerSession and 'gameType' in playerSession:
            footer = f'Currently in a {playerSession["gameType"].title()} game'; onlineStatus = True
        else:
            footer = self.bot.footer
        if onlineStatus:
            footer_url = 'https://image.ibb.co/h9VNfq/image.png'
        else:
            footer_url = 'https://image.ibb.co/hwheRV/image.png'
        embeds = {}
        emb = {
            'embed': {
                'title': f'{"[" + playerRank["prefix"] + "]" if playerRank["prefix"] else "[" + playerRank["rank"] + "]"} {playerName}' if playerRank["rank"] != 'Non' else playerName,
                'url': f'https://hypixel.net/player/{playerName}',
                'description': '',
                'color': colour
            },
            'footer': {
                'text': footer,
                'icon_url': footer_url
            },
            'thumbnail': 'https://image.ibb.co/i591Qq/BrNpK5l.png',
            'pages': {
                '0': [
                    {'description': 'Cops & Crims'},
                    {'name': 'Coins', 'value': f'{playerMCGO["coins"] if "coins" in playerMCGO else 0:,}', 'inline': False},
                    {'name': 'Kills', 'value': playerMCGO["kills"] if 'kills' in playerMCGO else 0},
                    {'name': 'Headshots', 'value': playerMCGO["headshot_kills"] if 'headshot_kills' in playerMCGO else 0},
                    {'name': 'Deaths', 'value': playerMCGO["deaths"] if 'deaths' in playerMCGO else 0},
                    {'name': 'Game Wins', 'value': playerMCGO["game_wins"] if 'game_wins' in playerMCGO else 0},
                    {'name': 'Round Wins', 'value': playerMCGO["round_wins"] if 'round_wins' in playerMCGO else 0},

                    {'name': 'Shots Fired', 'value': playerMCGO["shots_fired"] if 'shots_fired' in playerMCGO else 0},
                    {'name': 'Cop Kills', 'value': playerMCGO["cop_kills"] if 'cop_kills' in playerMCGO else 0},
                    {'name': 'Criminal Kills', 'value': playerMCGO["criminal_kills"] if 'criminal_kills' in playerMCGO else 0},
                    {'name': 'Deathmatch Kills', 'value': playerMCGO["kills_deathmatch"] if 'kills_deathmatch' in playerMCGO else 0},
                    {'name': 'Bombs Planted', 'value': playerMCGO["bombs_planted"] if 'bombs_planted' in playerMCGO else 0},
                    {'name': 'Bombs Defused', 'value': playerMCGO["bombs_defused"] if 'bombs_defused' in playerMCGO else 0},
                ]
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
    h = CopsAndCrims(bot)
    bot.add_cog(h)
