import datetime

from hypixel.utils.functions import *


class MurderMystery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenSkyWars(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "SkyWars" not in playerJSON["stats"] or len(playerJSON['stats']['SkyWars']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Skywars before.")
        embeds = self.SkyWars(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def SkyWars(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerSkywars = playerJSON["stats"]["SkyWars"]

        lvl = playerSkywars['levelFormatted'][2:-1] if 'levelFormatted' in playerSkywars else '0'
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
                'title': (f'{"[" + playerRank["prefix"] + "]" if playerRank["prefix"] else "[" + playerRank["rank"] + "]"} {playerName}' if playerRank["rank"] != 'Non' else playerName),
                'url': f'https://hypixel.net/player/{playerName}',
                'description': '',
                'color': colour
            },
            'footer': {
                'text': footer,
                'icon_url': footer_url
            },
            'thumbnail': 'https://image.ibb.co/htOT5q/liUywIa.png',
            'pages': {
                '0': [
                    {'description': 'Sky Wars - **Overall**'},
                    {'name': 'Coins', 'value': f'{(playerSkywars["coins"] if "coins" in playerSkywars else 0):,}'},
                    {'name': 'Level', 'value': f'{lvl}**⋆**'},
                    {'name': 'Win Streak', 'value': playerSkywars["win_streak"] if 'win_streak' in playerSkywars else 0},
                    {'name': 'Souls', 'value': f'{(playerSkywars["souls"] if "souls" in playerSkywars else 0):,}'},
                    {'name': 'Kills', 'value': playerSkywars["kills"] if 'kills' in playerSkywars else 0},
                    {'name': 'Deaths', 'value': playerSkywars["deaths"] if 'deaths' in playerSkywars else 0},
                    {'name': 'Wins', 'value': playerSkywars["wins"] if 'wins' in playerSkywars else 0},
                    {'name': 'Losses', 'value': playerSkywars["losses"] if 'losses' in playerSkywars else 0},
                    {'name': 'Kill/Death Ratio', 'value': f'{int(playerSkywars["kills"] if "kills" in playerSkywars else 0) / int(playerSkywars["deaths"] if "deaths" in playerSkywars else 1):.2f}'},
                    {'name': 'Win/Loss Ratio', 'value': f'{int(playerSkywars["wins"] if "wins" in playerSkywars else 0) / int(playerSkywars["losses"] if "losses" in playerSkywars else 1):.2f}'},
                ],
                '1': [
                    {'description': 'Sky Wars - **Solo**'},
                    {'name': 'Normal Kills', 'value': playerSkywars["kills_solo_normal"] if 'kills_solo_normal' in playerSkywars else 0},
                    {'name': 'Normal Deaths', 'value': playerSkywars["deaths_solo_normal"] if 'deaths_solo_normal' in playerSkywars else 0},
                    {'name': 'Normal Wins', 'value': playerSkywars["wins_solo_normal"] if 'wins_solo_normal' in playerSkywars else 0},
                    {'name': 'Normal Losses', 'value': playerSkywars["losses_solo_normal"] if 'losses_solo_normal' in playerSkywars else 0},
                    {'name': 'Normal Kill/Death Ratio', 'value': f'{int(playerSkywars["kills_solo_normal"] if "kills_solo_normal" in playerSkywars else 0) / int(playerSkywars["deaths_solo_normal"] if "deaths_solo_normal" in playerSkywars else 1):.2f}'},
                    {'name': 'Normal Win/Loss Ratio', 'value': f'{int(playerSkywars["wins_solo_normal"] if "wins_solo_normal" in playerSkywars else 0) / int(playerSkywars["losses_solo_normal"] if "losses_solo_normal" in playerSkywars else 1):.2f}'},

                    {'name': 'Insane Kills', 'value': playerSkywars["kills_solo_insane"] if 'kills_solo_insane' in playerSkywars else 0},
                    {'name': 'Insane Deaths', 'value': playerSkywars["deaths_solo_insane"] if 'deaths_solo_insane' in playerSkywars else 0},
                    {'name': 'Insane Wins', 'value': playerSkywars["wins_solo_insane"] if 'wins_solo_insane' in playerSkywars else 0},
                    {'name': 'Insane Losses', 'value': playerSkywars["losses_solo_insane"] if 'losses_solo_insane' in playerSkywars else 0},
                    {'name': 'Insane Kill/Death Ratio', 'value': f'{int(playerSkywars["kills_solo_insane"] if "kills_solo_insane" in playerSkywars else 0) / int(playerSkywars["deaths_solo_insane"] if "deaths_solo_insane" in playerSkywars else 1):.2f}'},
                    {'name': 'Insane Win/Loss Ratio', 'value': f'{int(playerSkywars["wins_solo_insane"] if "wins_solo_insane" in playerSkywars else 0) / int(playerSkywars["losses_solo_insane"] if "losses_solo_insane" in playerSkywars else 1):.2f}'},
                ],
                '2': [
                    {'description': 'Sky Wars - **Teams**'},
                    {'name': 'Normal Kills', 'value': playerSkywars["kills_team_normal"] if 'kills_team_normal' in playerSkywars else 0},
                    {'name': 'Normal Deaths', 'value': playerSkywars["deaths_team_normal"] if 'deaths_team_normal' in playerSkywars else 0},
                    {'name': 'Normal Wins', 'value': playerSkywars["wins_team_normal"] if 'wins_team_normal' in playerSkywars else 0},
                    {'name': 'Normal Losses', 'value': playerSkywars["losses_team_normal"] if 'losses_team_normal' in playerSkywars else 0},
                    {'name': 'Normal Kill/Death Ratio', 'value': f'{int(playerSkywars["kills_team_normal"] if "kills_team_normal" in playerSkywars else 0) / int(playerSkywars["deaths_team_normal"] if "deaths_team_normal" in playerSkywars else 1):.2f}'},
                    {'name': 'Normal Win/Loss Ratio', 'value': f'{int(playerSkywars["wins_team_normal"] if "wins_team_normal" in playerSkywars else 0) / int(playerSkywars["losses_team_normal"] if "losses_team_normal" in playerSkywars else 1):.2f}'},

                    {'name': 'Insane Teams Kills', 'value': playerSkywars["kills_team_insane"] if 'kills_team_insane' in playerSkywars else 0},
                    {'name': 'Insane Teams Deaths', 'value': playerSkywars["deaths_team_insane"] if 'deaths_team_insane' in playerSkywars else 0},
                    {'name': 'Insane Teams Wins', 'value': playerSkywars["wins_team_insane"] if 'wins_team_insane' in playerSkywars else 0},
                    {'name': 'Insane Teams Losses', 'value': playerSkywars["losses_team_insane"] if 'losses_team_insane' in playerSkywars else 0},
                    {'name': 'Insane Kill/Death Ratio', 'value': f'{int(playerSkywars["kills_team_insane"] if "kills_team_insane" in playerSkywars else 0) / int(playerSkywars["deaths_team_insane"] if "deaths_team_insane" in playerSkywars else 1):.2f}'},
                    {'name': 'Insane Win/Loss Ratio', 'value': f'{int(playerSkywars["wins_team_insane"] if "wins_team_insane" in playerSkywars else 0) / int(playerSkywars["losses_team_insane"] if "losses_team_insane" in playerSkywars else 1):.2f}'},
                ],
                '3': [
                    {'description': 'Sky Wars - **Ranked**'},
                    {'name': 'Ranked Kills', 'value': playerSkywars["kills_ranked"] if 'kills_ranked' in playerSkywars else 0},
                    {'name': 'Ranked Deaths', 'value': playerSkywars["deaths_ranked"] if 'deaths_ranked' in playerSkywars else 0},
                    {'name': 'Ranked Wins', 'value': playerSkywars["wins_ranked"] if 'wins_ranked' in playerSkywars else 0},
                    {'name': 'Ranked Losses', 'value': playerSkywars["losses_ranked"] if 'losses_ranked' in playerSkywars else 0},
                    {'name': 'Kill/Death Ratio', 'value': f'{int(playerSkywars["kills_ranked"] if "kills_ranked" in playerSkywars else 0) / int(playerSkywars["deaths_ranked"] if "deaths_ranked" in playerSkywars else 1):.2f}'},
                    {'name': 'Win/Loss Ratio', 'value': f'{int(playerSkywars["wins_ranked"] if "wins_ranked" in playerSkywars else 0) / int(playerSkywars["losses_ranked"] if "losses_ranked" in playerSkywars else 1):.2f}'},
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
