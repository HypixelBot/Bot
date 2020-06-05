import datetime

from hypixel.utils.functions import *


class MurderMystery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenMurderMystery(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "MurderMystery" not in playerJSON["stats"] or len(playerJSON['stats']['MurderMystery']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Murder Mystery before.")
        embeds = self.MurderMystery(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds=embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def MurderMystery(self, playerMM):
        playerJSON = playerMM.JSON
        playerRank = playerMM.getRank()
        playerName = playerMM.getName()
        playerSession = playerMM.getSession()
        onlineStatus = playerMM.getOnlineStatus()
        playerMM = playerJSON["stats"]["MurderMystery"]
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
                'url': f"https://hypixel.net/playerMM/{playerName}",
                'description': '',
                'color': colour
            },
            'footer': {
                'text': footer,
                'icon_url': footer_url
            },
            'thumbnail': 'https://image.ibb.co/h7CAJA/image.png',
            'pages': {
                '0': [
                    {'description': 'Murder Mystery - **Overall**'},
                    {'name': 'Coins', 'value': f'{playerMM["coins"] if "coins" in playerMM else 0:,}', 'inline': False},
                    {'name': 'Kills', 'value': f'{playerMM["kills"] if "kills" in playerMM else 0:,}'},
                    {'name': 'Deaths', 'value': f'{playerMM["deaths"] if "deaths" in playerMM else 0:,}'},
                    {'name': 'Bow Kills', 'value': f'{playerMM["bow_kills"] if "bow_kills" in playerMM else 0:,}'},
                    {'name': 'Knife Kills', 'value': f'{playerMM["knife_kills"] if "knife_kills" in playerMM else 0:,}'},
                    {'name': 'Thrown Knife Kills', 'value': f'{playerMM["thrown_knife_kills"] if "thrown_knife_kills" in playerMM else 0:,}'},
                    {'name': 'Wins', 'value': f'{playerMM["wins"] if "wins" in playerMM else 0:,}'},
                ],
                '1': [
                    {'description': 'Murder Mystery - **Classic**'},
                    {'name': 'Kills', 'value': f'{playerMM["kills_MURDER_CLASSIC"] if "kills_MURDER_CLASSIC" in playerMM else 0:,}'},
                    {'name': 'Deaths', 'value': f'{playerMM["deaths_MURDER_CLASSIC"] if "deaths_MURDER_CLASSIC" in playerMM else 0:,}'},
                    {'name': 'Bow Kills', 'value': f'{playerMM["bow_kills_MURDER_CLASSIC"] if "bow_kills_MURDER_CLASSIC" in playerMM else 0:,}'},
                    {'name': 'Knife Kills', 'value': f'{playerMM["knife_kills_MURDER_CLASSIC"] if "knife_kills_MURDER_CLASSIC" in playerMM else 0:,}'},
                    {'name': 'Thrown Knife Kills', 'value': f'{playerMM["thrown_knife_kills_MURDER_CLASSIC"] if "thrown_knife_kills_MURDER_CLASSIC" in playerMM else 0:,}'},
                    {'name': 'Wins', 'value': f'{playerMM["wins_MURDER_CLASSIC"] if "wins_MURDER_CLASSIC" in playerMM else 0:,}'},
                ],
                '2': [
                    {'description': 'Murder Mystery - **Hardcore**'},
                    {'name': 'Kills', 'value': f'{playerMM["kills_MURDER_HARDCORE"] if "kills_MURDER_HARDCORE" in playerMM else 0:,}'},
                    {'name': 'Deaths', 'value': f'{playerMM["deaths_MURDER_HARDCORE"] if "deaths_MURDER_HARDCORE" in playerMM else 0:,}'},
                    {'name': 'Bow Kills', 'value': f'{playerMM["bow_kills_MURDER_HARDCORE"] if "bow_kills_MURDER_HARDCORE" in playerMM else 0:,}'},
                    {'name': 'Knife Kills', 'value': f'{playerMM["knife_kills_MURDER_HARDCORE"] if "knife_kills_MURDER_HARDCORE" in playerMM else 0:,}'},
                    {'name': 'Thrown Knife Kills', 'value': f'{playerMM["thrown_knife_kills_MURDER_HARDCORE"] if "thrown_knife_kills_MURDER_HARDCORE" in playerMM else 0:,}'},
                    {'name': 'Wins', 'value': f'{playerMM["wins_MURDER_HARDCORE"] if "wins_MURDER_HARDCORE" in playerMM else 0:,}'},
                ],
                '3': [
                    {'description': 'Murder Mystery - **Assassins**'},
                    {'name': 'Kills', 'value': f'{playerMM["kills_MURDER_ASSASSINS"] if "kills_MURDER_ASSASSINS" in playerMM else 0:,}'},
                    {'name': 'Deaths', 'value': f'{playerMM["deaths_MURDER_ASSASSINS"] if "deaths_MURDER_ASSASSINS" in playerMM else 0:,}'},
                    {'name': 'Bow Kills', 'value': f'{playerMM["bow_kills_MURDER_ASSASSINS"] if "bow_kills_MURDER_ASSASSINS" in playerMM else 0:,}'},
                    {'name': 'Knife Kills', 'value': f'{playerMM["knife_kills_MURDER_ASSASSINS"] if "knife_kills_MURDER_ASSASSINS" in playerMM else 0:,}'},
                    {'name': 'Thrown Knife Kills', 'value': f'{playerMM["thrown_knife_kills_MURDER_ASSASSINS"] if "thrown_knife_kills_MURDER_ASSASSINS" in playerMM else 0:,}'},
                    {'name': 'Wins', 'value': f'{playerMM["wins_MURDER_ASSASSINS"] if "wins_MURDER_ASSASSINS" in playerMM else 0:,}'},
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
