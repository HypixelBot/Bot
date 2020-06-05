import datetime

from hypixel.utils.functions import *


class CrazyWalls(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenCrazyWalls(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "TrueCombat" not in playerJSON["stats"] or len(playerJSON['stats']['TrueCombat']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Crazy Walls before.")
        embeds = self.CrazyWalls(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def CrazyWalls(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerTC = playerJSON["stats"]["TrueCombat"]
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
            'thumbnail': 'https://image.ibb.co/fdaKBV/BUgpGKB.png',
            'pages': {
                '0': [
                    {'description': 'Crazy Walls - **Overall**'},
                    {'name': 'Coins', 'value': f'{playerTC["coins"] if "coins" in playerTC else 0:,}'},
                    {'name': 'Win Streak', 'value': playerTC["win_streak"] if 'win_streak' in playerTC else 0},
                    {'name': 'Kills', 'value': playerTC["kills"] if 'kills' in playerTC else 0},
                    {'name': 'Deaths', 'value': playerTC["deaths"] if 'deaths' in playerTC else 0},
                    {'name': 'Wins', 'value': playerTC["wins"] if 'wins' in playerTC else 0},
                    {'name': 'Losses', 'value': playerTC["losses"] if 'losses' in playerTC else 0},
                    {'name': 'KDR', 'value': f'{int(playerTC["kills"] if "kills" in playerTC else 0) / int(playerTC["deaths"] if "deaths" in playerTC else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerTC["wins"] if "wins" in playerTC else 0) / int(playerTC["losses"] if "losses" in playerTC else 1):.2f}'},
                ],
                '1': [
                    {'description': 'Crazy Walls - **Solo Normal**'},
                    {'name': 'Kills', 'value': playerTC["crazywalls_kills_solo"] if 'crazywalls_kills_solo' in playerTC else 0},
                    {'name': 'Deaths', 'value': playerTC["crazywalls_deaths_solo"] if 'crazywalls_deaths_solo' in playerTC else 0},
                    {'name': 'Wins', 'value': playerTC["crazywalls_wins_solo"] if 'crazywalls_wins_solo' in playerTC else 0},
                    {'name': 'Losses', 'value': playerTC["crazywalls_losses_solo"] if 'crazywalls_losses_solo' in playerTC else 0},
                    {'name': 'KDR', 'value': f'{int(playerTC["crazywalls_kills_solo"] if "crazywalls_kills_solo" in playerTC else 0) / int(playerTC["crazywalls_deaths_solo"] if "crazywalls_deaths_solo" in playerTC else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerTC["crazywalls_wins_solo"] if "crazywalls_wins_solo" in playerTC else 0) / int(playerTC["crazywalls_losses_solo"] if "crazywalls_losses_solo" in playerTC else 1):.2f}'},
                ],
                '2': [
                    {'description': 'Crazy Walls - **Solo Lucky**'},
                    {'name': 'Kills', 'value': playerTC["crazywalls_kills_solo_chaos"] if 'crazywalls_kills_solo_chaos' in playerTC else 0},
                    {'name': 'Deaths', 'value': playerTC["crazywalls_deaths_solo_chaos"] if 'crazywalls_deaths_solo_chaos' in playerTC else 0},
                    {'name': 'Wins', 'value': playerTC["crazywalls_wins_solo_chaos"] if 'crazywalls_wins_solo_chaos' in playerTC else 0},
                    {'name': 'Losses', 'value': playerTC["crazywalls_losses_solo_chaos"] if 'crazywalls_losses_solo_chaos' in playerTC else 0},
                    {'name': 'KDR', 'value': f'{int(playerTC["crazywalls_kills_solo_chaos"] if "crazywalls_kills_solo_chaos" in playerTC else 0) / int(playerTC["crazywalls_deaths_solo_chaos"] if "crazywalls_deaths_solo_chaos" in playerTC else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerTC["crazywalls_wins_solo_chaos"] if "crazywalls_wins_solo_chaos" in playerTC else 0) / int(playerTC["crazywalls_losses_solo_chaos"] if "crazywalls_losses_solo_chaos" in playerTC else 1):.2f}'},
                ],
                '3': [
                    {'description': 'Crazy Walls - **Team Normal**'},
                    {'name': 'Kills', 'value': playerTC["crazywalls_kills_team"] if 'crazywalls_kills_team' in playerTC else 0},
                    {'name': 'Deaths', 'value': playerTC["crazywalls_deaths_team"] if 'crazywalls_deaths_team' in playerTC else 0},
                    {'name': 'Wins', 'value': playerTC["crazywalls_wins_team"] if 'crazywalls_wins_team' in playerTC else 0},
                    {'name': 'Losses', 'value': playerTC["crazywalls_losses_team"] if 'crazywalls_losses_team' in playerTC else 0},
                    {'name': 'KDR', 'value': f'{int(playerTC["crazywalls_kills_team"] if "crazywalls_kills_team" in playerTC else 0) / int(playerTC["crazywalls_deaths_team"] if "crazywalls_deaths_team" in playerTC else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerTC["crazywalls_wins_team"] if "crazywalls_wins_team" in playerTC else 0) / int(playerTC["crazywalls_losses_team"] if "crazywalls_losses_team" in playerTC else 1):.2f}'},
                ],
                '4': [
                    {'description': 'Crazy Walls - **Team Lucky**'},
                    {'name': 'Kills', 'value': playerTC["crazywalls_kills_team_chaos"] if 'crazywalls_kills_team_chaos' in playerTC else 0},
                    {'name': 'Deaths', 'value': playerTC["crazywalls_deaths_team_chaos"] if 'crazywalls_deaths_team_chaos' in playerTC else 0},
                    {'name': 'Wins', 'value': playerTC["crazywalls_wins_team_chaos"] if 'crazywalls_wins_team_chaos' in playerTC else 0},
                    {'name': 'Losses', 'value': playerTC["crazywalls_losses_team_chaos"] if 'crazywalls_losses_team_chaos' in playerTC else 0},
                    {'name': 'KDR', 'value': f'{int(playerTC["crazywalls_kills_team_chaos"] if "crazywalls_kills_team_chaos" in playerTC else 0) / int(playerTC["crazywalls_deaths_team_chaos"] if "crazywalls_deaths_team_chaos" in playerTC else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerTC["crazywalls_wins_team_chaos"] if "crazywalls_wins_team_chaos" in playerTC else 0) / int(playerTC["crazywalls_losses_team_chaos"] if "crazywalls_losses_team_chaos" in playerTC else 1):.2f}'},
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
    h = CrazyWalls(bot)
    bot.add_cog(h)
