import datetime

from hypixel.utils.functions import *


class Quake(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenQuake(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "Quake" not in playerJSON["stats"] or len(playerJSON['stats']['Quake']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Quake before.")
        embeds = self.Quake(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def Quake(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerQuake = playerJSON["stats"]["Quake"]
        if playerRank["rank"] == 'Youtuber': colour = self.utils.rank["RED"]
        elif "rankPlusColor" in playerJSON: colour = self.utils.rank[playerJSON["rankPlusColor"]][0]
        else: colour = 0x55FFFF
        if playerSession and 'gameType' in playerSession: footer = f'Currently in a {playerSession["gameType"].title()} game'; onlineStatus = True
        else: footer = self.bot.footer
        if onlineStatus: footer_url = 'https://image.ibb.co/h9VNfq/image.png'
        else: footer_url = 'https://image.ibb.co/hwheRV/image.png'
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
            'thumbnail': 'https://image.ibb.co/bvfKBV/ze6z82i.png',
            'pages': {
                '0': [
                    {'description': 'Quake - **Overall**'},
                    {'name': 'Coins', 'value': f'{playerQuake["coins"] if "coins" in playerQuake else 0:,}'},
                    {'name': 'Highest Killstreak', 'value': f'{playerQuake["highest_killstreak"] if "highest_killstreak" in playerQuake else 0:,}'},
                    {'name': 'Kills', 'value': (playerQuake["kills"] if 'kills' in playerQuake else 0) + (playerQuake["kills_teams"] if 'kills_teams' in playerQuake else 0)},
                    {'name': 'Deaths', 'value': (playerQuake["deaths"] if 'deaths' in playerQuake else 0) + (playerQuake["deaths_teams"] if 'deaths_teams' in playerQuake else 0)},
                    {'name': 'Wins', 'value': (playerQuake["wins"] if 'wins' in playerQuake else 0) + (playerQuake["wins_teams"] if 'wins_teams' in playerQuake else 0)},
                    {'name': 'KDR', 'value': f'{int((playerQuake["kills"] if "kills" in playerQuake else 0) + (playerQuake["kills_teams"] if "kills_teams" in playerQuake else 0)) / int((playerQuake["deaths"] if "deaths" in playerQuake else 1) + (playerQuake["deaths_teams"] if "deaths_teams" in playerQuake else 1)):.2f}'},
                    {'name': 'Dash Power', 'value': playerQuake["dash_power"] if "dash_power" in playerQuake else 0},
                    {'name': 'Dash Cooldown', 'value': playerQuake["dash_cooldown"] if "dash_cooldown" in playerQuake else 0}
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
    h = Quake(bot)
    bot.add_cog(h)
