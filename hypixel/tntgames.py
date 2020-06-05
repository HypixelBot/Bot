import datetime

from hypixel.utils.functions import *


class TnTGames(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenTnTGames(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "TNTGames" not in playerJSON["stats"] or len(playerJSON['stats']['TNTGames']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played TNT Games before.")
        embeds = self.TnTGames(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def TnTGames(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        TnTGames = playerJSON['stats']['TNTGames']
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
            'thumbnail': 'https://i.ibb.co/2hvh1x1/TNT-64.png',
            'pages': {
                '0': [
                    {'description': 'TnT Games - **Overall**'},
                    {'name': 'Coins', 'value': f"{TnTGames['coins']:,}" if 'coins' in TnTGames else '0', 'inline': False},
                    {'name': 'TNT Run Wins', 'value': f"{TnTGames['wins_tntrun']:,}" if 'wins_tntrun' in TnTGames else '0'},
                    {'name': 'TNT Run Record', 'value': f"{str(round(TnTGames['record_tntrun']/60, 2)).replace('.', ':')}" if 'record_tntrun' in TnTGames else '0'},
                    {'name': 'TNTag Wins', 'value': f"{TnTGames['wins_tntag']:,}" if 'wins_tntag' in TnTGames else '0'},
                    {'name': 'Bowspleef Wins', 'value': f"{TnTGames['wins_bowspleef']:,}" if 'wins_bowspleef' in TnTGames else '0'},
                    {'name': 'Bowspleef Losses', 'value': f"{TnTGames['deaths_bowspleef']:,}" if 'deaths_bowspleef' in TnTGames else '0'},
                    {'name': 'Wizards Kills', 'value': f"{TnTGames['tntgames_tnt_wizards_kills']:,}" if 'tntgames_tnt_wizards_kills' in TnTGames else '0'},
                    {'name': 'Wizards Deaths', 'value': f"{TnTGames['deaths_capture']:,}" if 'deaths_capture' in TnTGames else '0'},
                    {'name': 'Wizards Wins', 'value': f"{TnTGames['tntgames_wizards_wins']:,}" if 'tntgames_wizards_wins' in TnTGames else '0'},
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
    h = TnTGames(bot)
    bot.add_cog(h)
