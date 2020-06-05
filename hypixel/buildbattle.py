import datetime

from hypixel.utils.functions import *


class BuildBattle(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenBuildBattle(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "BuildBattle" not in playerJSON["stats"] or len(playerJSON['stats']['BuildBattle']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Build Battle before.")
        embeds = self.BuildBattle(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def BuildBattle(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        BuildBattle = playerJSON['stats']['BuildBattle']
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
            'thumbnail': 'https://i.ibb.co/RvVj5LT/Build-Battle-64.png',
            'pages': {
                '0': [
                    {'description': 'BuildBattle - **Overall**'},
                    {'name': 'Score', 'value': f"{BuildBattle['score']:,}" if 'score' in BuildBattle else '0'},
                    {'name': 'Coins', 'value': f"{BuildBattle['coins']:,}" if 'coins' in BuildBattle else '0'},
                    {'name': 'Total Wins', 'value': f"{BuildBattle['wins']:,}" if 'wins' in BuildBattle else '0'},
                    {'name': 'Games Played', 'value': f"{BuildBattle['games_played']:,}" if 'games_played' in BuildBattle else '0'},
                    {'name': 'Wins Solo', 'value': f"{BuildBattle['wins_solo_normal']:,}" if 'wins_solo_normal' in BuildBattle else '0'},
                    {'name': 'Wins Solo Pro', 'value': f"{BuildBattle['wins_solo_pro']:,}" if 'wins_solo_pro' in BuildBattle else '0'},
                    {'name': 'Wins Teams', 'value': f"{BuildBattle['wins_teams_normal']:,}" if 'wins_teams_normal' in BuildBattle else '0'},
                    {'name': 'Wins Guess The Build', 'value': f"{BuildBattle['wins_guess_the_build']:,}" if 'wins_guess_the_build' in BuildBattle else '0'},
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
                elif field:
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
    h = BuildBattle(bot)
    bot.add_cog(h)
