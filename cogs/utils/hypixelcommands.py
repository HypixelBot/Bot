import gzip
# import jnbt
import zlib
from ast import literal_eval
from collections import Counter

import datetime
import discord
import math
import re
from io import BytesIO

from cogs.utils import jnbt
from cogs.utils.dataIO import dataIO

class Commands:

    def __init__(self, bot):
        self.bot = bot
        self.rank = {
            'RED': 0xFF5555,
            'GOLD': 0xFFAA00,
            'GREEN': 0x55FF55,
            'YELLOW': 0xFFFF55,
            'LIGHT_PURPLE': 0xFF55FF,
            'WHITE': 0xFFFFFF,
            'BLUE': 0x5555FF,
            'DARK_BLUE': 0x0000AA,
            'DARK_GREEN': 0x00AA00,
            'DARK_RED': 0xAA0000,
            'DARK_AQUA': 0x00AAAA,
            'DARK_PURPLE': 0xAA00AA,
            'DARK_GRAY': 0xAAAAAA,
            'BLACK': 0x000000,
            'HELPER': 0x5555FF,
            'MODERATOR': 0x00AA00,
            'ADMIN': 0xFF5555
        }

    def tournaments(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        tourney = playerJSON["tourney"]
        bedwars = playerJSON["stats"]["Bedwars"]
        if playerRank["rank"] == 'Youtuber': colour = self.rank["RED"]
        elif "rankPlusColor" in playerJSON: colour = self.rank[playerJSON["rankPlusColor"]]
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
            'thumbnail': f'https://visage.surgeplay.com/head/256/{playerJSON["uuid"]}.png',
            'pages': {
                '0': [
                    {'description': 'Hypixel Tournaments'},
                    {'name': 'Total Tributes', 'value': f'{tourney["total_tributes"] if "total_tributes" in tourney else 0:,}'},
                    {'name': 'Total Playtime', 'value': f'{sum([x[1]["playtime"] for x in tourney.items() if type(x[1]) is dict and "playtime" in x[1]])/60} hours'},
                ],
            },
            # 'image': f'https://visage.surgeplay.com/full/256/{playerName}'
        }
        if "bedwars4s_0" in tourney: emb["pages"]["0"].append({'name': 'Bedwars `Nov 23` to `Nov 25`', 'value': f'Playtime: `{tourney["bedwars4s_0"]["playtime"]/60} hours`\n'
                                                                                                                f'Tributes Earned: `{tourney["bedwars4s_0"]["tributes_earned"]}`\n'
                                                                                                                f'Games Played: `{bedwars["tourney_bedwars4s_0_games_played_bedwars"] if "tourney_bedwars4s_0_games_played_bedwars" in bedwars else 0:,}`\n'
                                                                                                                f'Games Won: `{bedwars["tourney_bedwars4s_0_wins_bedwars"] if "tourney_bedwars4s_0_wins_bedwars" in bedwars else 0:,}`\n'
                                                                                                                f'Games Lost: `{bedwars["tourney_bedwars4s_0_losses_bedwars"] if "tourney_bedwars4s_0_losses_bedwars" in bedwars else 0:,}`\n'
                                                                                                                f'Final Kills: `{bedwars["tourney_bedwars4s_0_final_kills_bedwars"] if "tourney_bedwars4s_0_final_kills_bedwars" in bedwars else 0}`\n', 'inline':False})
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
