import datetime

from hypixel.utils.functions import *


class MurderMystery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenSkyClash(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "SkyClash" not in playerJSON["stats"] or len(playerJSON['stats']['SkyClash']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Sky Clash before.")
        embeds = self.SkyClash(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds=embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def SkyClash(self, player):
        # @TODO
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerSkyClash = playerJSON["stats"]["SkyClash"]
        if playerRank["rank"] == 'Youtuber': colour = self.utils.rank["RED"][0]
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
            'thumbnail': 'https://image.ibb.co/fL2cyA/I9z6FWN.png',
            'pages': {
                '0': [
                    {'description': 'Sky Clash - **Overall**'},
                    {'name': 'Coins', 'value': f'{playerSkyClash["coins"] if "coins" in playerSkyClash else 0:,}', 'inline': False},
                    {'name': 'Kills', 'value': playerSkyClash["kills"] if 'kills' in playerSkyClash else 0},
                    {'name': 'Deaths', 'value': playerSkyClash["deaths"] if 'deaths' in playerSkyClash else 0},
                    {'name': 'Wins', 'value': playerSkyClash["wins"] if 'wins' in playerSkyClash else 0},
                    {'name': 'Losses', 'value': playerSkyClash["losses"] if 'losses' in playerSkyClash else 0},
                    {'name': 'KDR', 'value': f'{int(playerSkyClash["kills"] if "kills" in playerSkyClash else 0) / int(playerSkyClash["deaths"] if "deaths" in playerSkyClash else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerSkyClash["wins"] if "wins" in playerSkyClash else 0) / int(playerSkyClash["losses"] if "losses" in playerSkyClash else 1):.2f}'},

                    {'name': 'Solo Kills', 'value': playerSkyClash["kills_solo"] if 'kills_solo' in playerSkyClash else 0},
                    {'name': 'Solo Deaths', 'value': playerSkyClash["deaths_solo"] if 'deaths_solo' in playerSkyClash else 0},
                    {'name': 'Solo Wins', 'value': playerSkyClash["wins_solo"] if 'wins_solo' in playerSkyClash else 0},
                    {'name': 'Solo Losses', 'value': playerSkyClash["losses_solo"] if 'losses_solo' in playerSkyClash else 0},
                    {'name': 'Solo KDR', 'value': f'{int(playerSkyClash["kills_solo"] if "kills_solo" in playerSkyClash else 0) / int(playerSkyClash["deaths_solo"] if "deaths_solo" in playerSkyClash else 1):.2f}'},
                    {'name': 'Solo WLR', 'value': f'{int(playerSkyClash["wins_solo"] if "wins_solo" in playerSkyClash else 0) / int(playerSkyClash["losses_solo"] if "losses_solo" in playerSkyClash else 1):.2f}'},
                ],
                '1': [

                    {'name': 'Doubles Kills', 'value': playerSkyClash["kills_doubles"] if 'kills_doubles' in playerSkyClash else 0},
                    {'name': 'Doubles Deaths', 'value': playerSkyClash["deaths_doubles"] if 'deaths_doubles' in playerSkyClash else 0},
                    {'name': 'Doubles Wins', 'value': playerSkyClash["wins_doubles"] if 'wins_doubles' in playerSkyClash else 0},
                    {'name': 'Doubles Losses', 'value': playerSkyClash["losses_doubles"] if 'losses_doubles' in playerSkyClash else 0},
                    {'name': 'Doubles KDR', 'value': f'{int(playerSkyClash["kills_doubles"] if "kills_doubles" in playerSkyClash else 0) / int(playerSkyClash["deaths_doubles"] if "deaths_doubles" in playerSkyClash else 1):.2f}'},
                    {'name': 'Doubles WLR', 'value': f'{int(playerSkyClash["wins_doubles"] if "wins_doubles" in playerSkyClash else 0) / int(playerSkyClash["losses_doubles"] if "losses_doubles" in playerSkyClash else 1):.2f}'},

                    {'name': 'Team War Kills', 'value': playerSkyClash["kills_team_war"] if 'kills_team_war' in playerSkyClash else 0},
                    {'name': 'Team War Deaths', 'value': playerSkyClash["deaths_team_war"] if 'deaths_team_war' in playerSkyClash else 0},
                    {'name': 'Team War Wins', 'value': playerSkyClash["wins_team_war"] if 'wins_team_war' in playerSkyClash else 0},
                    {'name': 'Team War Losses', 'value': playerSkyClash["losses_team_war"] if 'losses_team_war' in playerSkyClash else 0},
                    {'name': 'Team War KDR', 'value': f'{int(playerSkyClash["kills_team_war"] if "kills_team_war" in playerSkyClash else 0) / int(playerSkyClash["deaths_team_war"] if "deaths_team_war" in playerSkyClash else 1):.2f}'},
                    {'name': 'Team War WLR', 'value': f'{int(playerSkyClash["wins_team_war"] if "wins_team_war" in playerSkyClash else 0) / int(playerSkyClash["losses_team_war"] if "losses_team_war" in playerSkyClash else 1):.2f}'},
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
