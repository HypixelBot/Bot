import datetime

from hypixel.utils.functions import *


class VampireZ(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenVampireZ(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "VampireZ" not in playerJSON["stats"] or len(playerJSON['stats']['VampireZ']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played VampireZ before.")
        embeds = self.VampireZ(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def VampireZ(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        VampireZ = playerJSON["stats"]["VampireZ"]
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
            'thumbnail': 'https://image.ibb.co/m40Q9q/Vampire-Z-64.png',
            'pages': {
                '0': [
                    {'description': 'VampireZ - **Overall**'},
                    {'name': 'Coins', 'value': f'{VampireZ["coins"] if "coins" in VampireZ else 0:,}', 'inline': False},
                    {'name': 'Human Kills', 'value': f"{VampireZ['human_kills'] if 'human_kills' in VampireZ else 0:,}"},
                    {'name': 'Human Deaths', 'value': f"{VampireZ['human_deaths'] if 'human_deaths' in VampireZ else 0:,}"},
                    {'name': 'Human Wins', 'value': f"{VampireZ['human_wins'] if 'human_wins' in VampireZ else 0:,}"},
                    {'name': 'Zombie Kills', 'value': f"{VampireZ['zombie_kills'] if 'zombie_kills' in VampireZ else 0:,}"},
                    {'name': 'Vampire Kills', 'value': f"{VampireZ['vampire_kills'] if 'vampire_kills' in VampireZ else 0:,}"},
                    {'name': 'Vampire Deaths', 'value': f"{VampireZ['vampire_deaths'] if 'vampire_deaths' in VampireZ else 0:,}"},
                    {'name': 'KDR Vampire', 'value': f"{int(VampireZ['human_kills'] if 'human_kills' in VampireZ else 0) / int(VampireZ['vampire_deaths'] if 'vampire_deaths' in VampireZ else 1):.2f}"},
                    {'name': 'KDR Human', 'value': f"{int(VampireZ['vampire_kills'] if 'vampire_kills' in VampireZ else 0) / int(VampireZ['human_deaths'] if 'human_deaths' in VampireZ else 1):.2f}"},
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
    h = VampireZ(bot)
    bot.add_cog(h)
