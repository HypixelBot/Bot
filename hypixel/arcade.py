import datetime

from hypixel.utils.functions import *


class Arcade(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenArcade(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "Arcade" not in playerJSON["stats"] or len(playerJSON['stats']['Arcade']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Arcade before.")
        embeds = self.Arcade(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds=embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def Arcade(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerArcade = playerJSON["stats"]["Arcade"]
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
                'title': f'{"[" + playerRank["prefix"] + "]" if playerRank["prefix"] else "[" + playerRank["rank"] + "]"} {playerName}' if playerRank["rank"] != 'Non' else playerName,
                'url': f'https://hypixel.net/player/{playerName}',
                'description': '',
                'color': colour
            },
            'footer': {
                'text': footer,
                'icon_url': footer_url
            },
            'thumbnail': 'https://image.ibb.co/g714dA/GizpzB7.png',
            'pages': {
                '0': [
                    {'description': 'Arcade'},
                    {'name': 'Coins', 'value': f'{playerArcade["coins"] if "coins" in playerArcade else 0:,}', 'inline': False},
                    {'name': 'Wins Blocking Dead', 'value': playerArcade["wins_dayone"] if "wins_dayone" in playerArcade else 0},
                    {'name': 'Kills Blocking Dead', 'value': playerArcade["kills_dayone"] if "kills_dayone" in playerArcade else 0},
                    {'name': 'Headshots Blocking Dead', 'value': playerArcade["headshots_dayone"] if "headshots_dayone" in playerArcade else 0, 'inline': False},
                    {'name': 'Wins Dragonwars', 'value': playerArcade["wins_dragonwars2"] if "wins_dragonwars2" in playerArcade else 0},
                    {'name': 'Kills Dragonwars', 'value': playerArcade["kills_dragonwars2"] if "kills_dragonwars2" in playerArcade else 0},
                    {'name': 'Wins Bounty Hunter', 'value': playerArcade["wins_oneinthequiver"] if "wins_oneinthequiver" in playerArcade else 0},
                    {'name': 'Kills Bounty Hunter', 'value': playerArcade["kills_oneinthequiver"] if "kills_oneinthequiver" in playerArcade else 0},
                    {'name': 'Wins Throw Out', 'value': playerArcade["wins_throw_out"] if "wins_throw_out" in playerArcade else 0},
                    {'name': 'Kills Throw Out', 'value': playerArcade["kills_throw_out"] if "kills_throw_out" in playerArcade else 0},
                    {'name': 'Poop Collected', 'value': playerArcade["poop_collected"] if "poop_collected" in playerArcade else 0},
                ],
                '1': [
                    {'description': 'Arcade'},
                    {'name': 'Wins Enderspleef', 'value': playerArcade["wins_enderspleef"] if "wins_enderspleef" in playerArcade else 0},
                    {'name': 'Wins Farm Hunt', 'value': playerArcade["wins_farm_hunt"] if "wins_farm_hunt" in playerArcade else 0},
                    # {'name': 'Wins Party Games', 'value': "party games 1/2/3"},
                    {'name': 'Wins Hole in the Wall', 'value': playerArcade["wins_hole_in_the_wall"] if "wins_hole_in_the_wall" in playerArcade else 0, 'inline': False},
                    {'name': 'HITW Highest Score Qualifications', 'value': playerArcade["hitw_record_q"] if "hitw_record_q" in playerArcade else 0},
                    {'name': 'HITW Highest Score Finals', 'value': playerArcade["hitw_record_f"] if "hitw_record_f" in playerArcade else 0},
                    {'name': 'Wins Hypixel Says', 'value': playerArcade["wins_simon_says"] if "wins_simon_says" in playerArcade else 0},
                    {'name': 'Wins Mini Walls', 'value': playerArcade["wins_mini_walls"] if "wins_mini_walls" in playerArcade else 0},
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
    h = Arcade(bot)
    bot.add_cog(h)
