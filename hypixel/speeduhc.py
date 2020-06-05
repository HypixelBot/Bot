import datetime

from hypixel.utils.functions import *


class MurderMystery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenSpeedUHC(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "SpeedUHC" not in playerJSON["stats"] or len(playerJSON['stats']['SpeedUHC']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Speed UHC before.")
        embeds = self.SpeedUHC(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def SpeedUHC(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerSpeedUHC = playerJSON["stats"]["SpeedUHC"]
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
            'thumbnail': 'https://image.ibb.co/mXwRrV/SEXXWIW.png',
            'pages': {
                '0': [
                    {'description': 'Speed UHC'},
                    {'name': 'Coins', 'value': f'{playerSpeedUHC["coins"]:,}' if 'coins' in playerSpeedUHC else 0, 'inline': False},
                    {'name': 'Kills', 'value': playerSpeedUHC["kills"] if 'kills' in playerSpeedUHC else 0},
                    {'name': 'Deaths', 'value': playerSpeedUHC["deaths"] if 'deaths' in playerSpeedUHC else 0},

                    {'name': 'Wins', 'value': playerSpeedUHC["wins"] if 'wins' in playerSpeedUHC else 0},
                    {'name': 'Losses', 'value': playerSpeedUHC["losses"] if 'losses' in playerSpeedUHC else 0},
                    {'name': 'Kill/Death Ratio', 'value': f'{int(playerSpeedUHC["kills"] if "kills" in playerSpeedUHC else 0) / int(playerSpeedUHC["deaths"] if "deaths" in playerSpeedUHC else 1):.2f}'},
                    {'name': 'Win/Loss Ratio', 'value': f'{int(playerSpeedUHC["wins"] if "wins" in playerSpeedUHC else 0) / int(playerSpeedUHC["losses"] if "losses" in playerSpeedUHC else 1):.2f}'},
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
