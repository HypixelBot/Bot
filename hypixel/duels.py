import datetime

from hypixel.utils.functions import *


def duelsCalc(playerDuels):
    playerDuels['uhc_rounds_played'] = (playerDuels['uhc_duel_rounds_played'] if "uhc_duel_rounds_played" in playerDuels else 0) + (playerDuels['uhc_four_rounds_played'] if "uhc_four_rounds_played" in playerDuels else 0) + (playerDuels['uhc_doubles_rounds_played'] if "uhc_doubles_rounds_played" in playerDuels else 0)
    playerDuels['uhc_wins'] = (playerDuels['uhc_duel_wins'] if "uhc_duel_wins" in playerDuels else 0) + (playerDuels['uhc_four_wins'] if "uhc_four_wins" in playerDuels else 0) + (playerDuels['uhc_doubles_wins'] if "uhc_doubles_wins" in playerDuels else 0)
    playerDuels['uhc_kills'] = (playerDuels['uhc_duel_kills'] if "uhc_duel_kills" in playerDuels else 0) + (playerDuels['uhc_four_kills'] if "uhc_four_kills" in playerDuels else 0) + (playerDuels['uhc_doubles_kills'] if "uhc_doubles_kills" in playerDuels else 0)
    playerDuels['uhc_losses'] = (playerDuels['uhc_duel_losses'] if "uhc_duel_losses" in playerDuels else 0) + (playerDuels['uhc_four_losses'] if "uhc_four_losses" in playerDuels else 0) + (playerDuels['uhc_doubles_losses'] if "uhc_doubles_losses" in playerDuels else 0)
    playerDuels['uhc_deaths'] = (playerDuels['uhc_duel_deaths'] if "uhc_duel_deaths" in playerDuels else 0) + (playerDuels['uhc_four_deaths'] if "uhc_four_deaths" in playerDuels else 0) + (playerDuels['uhc_doubles_deaths'] if "uhc_doubles_deaths" in playerDuels else 0)
    playerDuels['uhc_damage_dealt'] = (playerDuels['uhc_duel_damage_dealt'] if "uhc_duel_damage_dealt" in playerDuels else 0) + (playerDuels['uhc_four_damage_dealt'] if "uhc_four_damage_dealt" in playerDuels else 0) + (playerDuels['uhc_doubles_damage_dealt'] if "uhc_doubles_damage_dealt" in playerDuels else 0)
    playerDuels['uhc_health_regenerated'] = (playerDuels['uhc_duel_health_regenerated'] if "uhc_duel_health_regenerated" in playerDuels else 0) + (playerDuels['uhc_four_health_regenerated'] if "uhc_four_health_regenerated" in playerDuels else 0) + (playerDuels['uhc_doubles_health_regenerated'] if "uhc_doubles_health_regenerated" in playerDuels else 0)
    playerDuels['uhc_melee_swings'] = (playerDuels['uhc_duel_melee_swings'] if "uhc_duel_melee_swings" in playerDuels else 0) + (playerDuels['uhc_four_melee_swings'] if "uhc_four_melee_swings" in playerDuels else 0) + (playerDuels['uhc_doubles_melee_swings'] if "uhc_doubles_melee_swings" in playerDuels else 0)
    playerDuels['uhc_melee_hits'] = (playerDuels['uhc_duel_melee_hits'] if "uhc_duel_melee_hits" in playerDuels else 0) + (playerDuels['uhc_four_melee_hits'] if "uhc_four_melee_hits" in playerDuels else 0) + (playerDuels['uhc_doubles_melee_hits'] if "uhc_doubles_melee_hits" in playerDuels else 0)
    playerDuels['uhc_bow_shots'] = (playerDuels['uhc_duel_bow_shots'] if "uhc_duel_bow_shots" in playerDuels else 0) + (playerDuels['uhc_four_bow_shots'] if "uhc_four_bow_shots" in playerDuels else 0) + (playerDuels['uhc_doubles_bow_shots'] if "uhc_doubles_bow_shots" in playerDuels else 0)
    playerDuels['uhc_bow_hits'] = (playerDuels['uhc_duel_bow_hits'] if "uhc_duel_bow_hits" in playerDuels else 0) + (playerDuels['uhc_four_bow_hits'] if "uhc_four_bow_hits" in playerDuels else 0) + (playerDuels['uhc_doubles_bow_hits'] if "uhc_doubles_bow_hits" in playerDuels else 0)

    playerDuels['sw_rounds_played'] = (playerDuels['sw_duel_rounds_played'] if "sw_duel_rounds_played" in playerDuels else 0) + (playerDuels['sw_doubles_rounds_played'] if "sw_doubles_rounds_played" in playerDuels else 0)
    playerDuels['sw_wins'] = (playerDuels['sw_duel_wins'] if "sw_duel_wins" in playerDuels else 0) + (playerDuels['sw_doubles_wins'] if "sw_doubles_wins" in playerDuels else 0)
    playerDuels['sw_kills'] = (playerDuels['sw_duel_kills'] if "sw_duel_kills" in playerDuels else 0) + (playerDuels['sw_doubles_kills'] if "sw_doubles_kills" in playerDuels else 0)
    playerDuels['sw_losses'] = (playerDuels['sw_duel_losses'] if "sw_duel_losses" in playerDuels else 0) + (playerDuels['sw_doubles_losses'] if "sw_doubles_losses" in playerDuels else 0)
    playerDuels['sw_deaths'] = (playerDuels['sw_duel_deaths'] if "sw_duel_deaths" in playerDuels else 0) + (playerDuels['sw_doubles_deaths'] if "sw_doubles_deaths" in playerDuels else 0)
    playerDuels['sw_damage_dealt'] = (playerDuels['sw_duel_damage_dealt'] if "sw_duel_damage_dealt" in playerDuels else 0) + (playerDuels['sw_doubles_damage_dealt'] if "sw_doubles_damage_dealt" in playerDuels else 0)
    playerDuels['sw_health_regenerated'] = (playerDuels['sw_duel_health_regenerated'] if "sw_duel_health_regenerated" in playerDuels else 0) + (playerDuels['sw_doubles_health_regenerated'] if "sw_doubles_health_regenerated" in playerDuels else 0)
    playerDuels['sw_melee_swings'] = (playerDuels['sw_duel_melee_swings'] if "sw_duel_melee_swings" in playerDuels else 0) + (playerDuels['sw_doubles_melee_swings'] if "sw_doubles_melee_swings" in playerDuels else 0)
    playerDuels['sw_melee_hits'] = (playerDuels['sw_duel_melee_hits'] if "sw_duel_melee_hits" in playerDuels else 0) + (playerDuels['sw_doubles_melee_hits'] if "sw_doubles_melee_hits" in playerDuels else 0)
    playerDuels['sw_bow_shots'] = (playerDuels['sw_duel_bow_shots'] if "sw_duel_bow_shots" in playerDuels else 0) + (playerDuels['sw_doubles_bow_shots'] if "sw_doubles_bow_shots" in playerDuels else 0)
    playerDuels['sw_bow_hits'] = (playerDuels['sw_duel_bow_hits'] if "sw_duel_bow_hits" in playerDuels else 0) + (playerDuels['sw_doubles_bow_hits'] if "sw_doubles_bow_hits" in playerDuels else 0)

    playerDuels['mw_rounds_played'] = (playerDuels['mw_duel_rounds_played'] if "mw_duel_rounds_played" in playerDuels else 0) + (playerDuels['mw_four_rounds_played'] if "mw_four_rounds_played" in playerDuels else 0) + (playerDuels['mw_doubles_rounds_played'] if "mw_doubles_rounds_played" in playerDuels else 0)
    playerDuels['mw_wins'] = (playerDuels['mw_duel_wins'] if "mw_duel_wins" in playerDuels else 0) + (playerDuels['mw_four_wins'] if "mw_four_wins" in playerDuels else 0) + (playerDuels['mw_doubles_wins'] if "mw_doubles_wins" in playerDuels else 0)
    playerDuels['mw_kills'] = (playerDuels['mw_duel_kills'] if "mw_duel_kills" in playerDuels else 0) + (playerDuels['mw_four_kills'] if "mw_four_kills" in playerDuels else 0) + (playerDuels['mw_doubles_kills'] if "mw_doubles_kills" in playerDuels else 0)
    playerDuels['mw_losses'] = (playerDuels['mw_duel_losses'] if "mw_duel_losses" in playerDuels else 0) + (playerDuels['mw_four_losses'] if "mw_four_losses" in playerDuels else 0) + (playerDuels['mw_doubles_losses'] if "mw_doubles_losses" in playerDuels else 0)
    playerDuels['mw_deaths'] = (playerDuels['mw_duel_deaths'] if "mw_duel_deaths" in playerDuels else 0) + (playerDuels['mw_four_deaths'] if "mw_four_deaths" in playerDuels else 0) + (playerDuels['mw_doubles_deaths'] if "mw_doubles_deaths" in playerDuels else 0)
    playerDuels['mw_damage_dealt'] = (playerDuels['mw_duel_damage_dealt'] if "mw_duel_damage_dealt" in playerDuels else 0) + (playerDuels['mw_four_damage_dealt'] if "mw_four_damage_dealt" in playerDuels else 0) + (playerDuels['mw_doubles_damage_dealt'] if "mw_doubles_damage_dealt" in playerDuels else 0)
    playerDuels['mw_health_regenerated'] = (playerDuels['mw_duel_health_regenerated'] if "mw_duel_health_regenerated" in playerDuels else 0) + (playerDuels['mw_four_health_regenerated'] if "mw_four_health_regenerated" in playerDuels else 0) + (playerDuels['mw_doubles_health_regenerated'] if "mw_doubles_health_regenerated" in playerDuels else 0)
    playerDuels['mw_melee_swings'] = (playerDuels['mw_duel_melee_swings'] if "mw_duel_melee_swings" in playerDuels else 0) + (playerDuels['mw_four_melee_swings'] if "mw_four_melee_swings" in playerDuels else 0) + (playerDuels['mw_doubles_melee_swings'] if "mw_doubles_melee_swings" in playerDuels else 0)
    playerDuels['mw_melee_hits'] = (playerDuels['mw_duel_melee_hits'] if "mw_duel_melee_hits" in playerDuels else 0) + (playerDuels['mw_four_melee_hits'] if "mw_four_melee_hits" in playerDuels else 0) + (playerDuels['mw_doubles_melee_hits'] if "mw_doubles_melee_hits" in playerDuels else 0)
    playerDuels['mw_bow_shots'] = (playerDuels['mw_duel_bow_shots'] if "mw_duel_bow_shots" in playerDuels else 0) + (playerDuels['mw_four_bow_shots'] if "mw_four_bow_shots" in playerDuels else 0) + (playerDuels['mw_doubles_bow_shots'] if "mw_doubles_bow_shots" in playerDuels else 0)
    playerDuels['mw_bow_hits'] = (playerDuels['mw_duel_bow_hits'] if "mw_duel_bow_hits" in playerDuels else 0) + (playerDuels['mw_four_bow_hits'] if "mw_four_bow_hits" in playerDuels else 0) + (playerDuels['mw_doubles_bow_hits'] if "mw_doubles_bow_hits" in playerDuels else 0)

    playerDuels['op_rounds_played'] = (playerDuels['op_duel_rounds_played'] if "op_duel_rounds_played" in playerDuels else 0) + (playerDuels['op_doubles_rounds_played'] if "op_doubles_rounds_played" in playerDuels else 0)
    playerDuels['op_wins'] = (playerDuels['op_duel_wins'] if "op_duel_wins" in playerDuels else 0) + (playerDuels['op_doubles_wins'] if "op_doubles_wins" in playerDuels else 0)
    playerDuels['op_kills'] = (playerDuels['op_duel_kills'] if "op_duel_kills" in playerDuels else 0) + (playerDuels['op_doubles_kills'] if "op_doubles_kills" in playerDuels else 0)
    playerDuels['op_losses'] = (playerDuels['op_duel_losses'] if "op_duel_losses" in playerDuels else 0) + (playerDuels['op_doubles_losses'] if "op_doubles_losses" in playerDuels else 0)
    playerDuels['op_deaths'] = (playerDuels['op_duel_deaths'] if "op_duel_deaths" in playerDuels else 0) + (playerDuels['op_doubles_deaths'] if "op_doubles_deaths" in playerDuels else 0)
    playerDuels['op_damage_dealt'] = (playerDuels['op_duel_damage_dealt'] if "op_duel_damage_dealt" in playerDuels else 0) + (playerDuels['op_doubles_damage_dealt'] if "op_doubles_damage_dealt" in playerDuels else 0)
    playerDuels['op_health_regenerated'] = (playerDuels['op_duel_health_regenerated'] if "op_duel_health_regenerated" in playerDuels else 0) + (playerDuels['op_doubles_health_regenerated'] if "op_doubles_health_regenerated" in playerDuels else 0)
    playerDuels['op_melee_swings'] = (playerDuels['op_duel_melee_swings'] if "op_duel_melee_swings" in playerDuels else 0) + (playerDuels['op_doubles_melee_swings'] if "op_doubles_melee_swings" in playerDuels else 0)
    playerDuels['op_melee_hits'] = (playerDuels['op_duel_melee_hits'] if "op_duel_melee_hits" in playerDuels else 0) + (playerDuels['op_doubles_melee_hits'] if "op_doubles_melee_hits" in playerDuels else 0)
    playerDuels['op_bow_shots'] = (playerDuels['op_duel_bow_shots'] if "op_duel_bow_shots" in playerDuels else 0) + (playerDuels['op_doubles_bow_shots'] if "op_doubles_bow_shots" in playerDuels else 0)
    playerDuels['op_bow_hits'] = (playerDuels['op_duel_bow_hits'] if "op_duel_bow_hits" in playerDuels else 0) + (playerDuels['op_doubles_bow_hits'] if "op_doubles_bow_hits" in playerDuels else 0)

    return playerDuels


class MurderMystery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenDuels(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "Walls" not in playerJSON["stats"] or len(playerJSON['stats']['Duels']) < 5: return await ctx.send(f"Doesn't look like `{user}` has played Duels before.")
        embeds = self.Duels(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def Duels(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        onlineStatus = player.getOnlineStatus()
        playerDuels = duelsCalc(playerJSON["stats"]["Duels"])
        if playerRank["rank"] == 'Youtuber': colour = self.utils.rank["RED"]
        elif "rankPlusColor" in playerJSON: colour = self.utils.rank[playerJSON["rankPlusColor"]][0]
        else: colour = 0x55FFFF
        if playerSession and 'gameType' in playerSession:
            footer = f'Currently in a {playerSession["gameType"].title()} game'
            onlineStatus = True
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
            'thumbnail': 'https://image.ibb.co/hwnzBV/3dPiMNj.png',
            'pages': {
                '0': [
                    {'description': 'Duels - **Overall**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["rounds_played"] if "rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["wins"] if "wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["kills"] if "kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["losses"] if "losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["deaths"] if "deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["wins"] if "wins" in playerDuels else 0) / int(playerDuels["losses"] if "losses" in playerDuels else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["kills"] if "kills" in playerDuels else 0) / int(playerDuels["deaths"] if "deaths" in playerDuels else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["damage_dealt"] if "damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["health_regenerated"] if "health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["melee_swings"] if "melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["melee_hits"] if "melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["bow_shots"] if "bow_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["bow_hits"] if "bow_hits" in playerDuels else 0}'},
                ],
                '1': [
                    {'description': 'Duels - **UHC**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["uhc_rounds_played"] if "uhc_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["uhc_wins"] if "uhc_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["uhc_kills"] if "uhc_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["uhc_losses"] if "uhc_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["uhc_deaths"] if "uhc_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["uhc_wins"] if "uhc_wins" in playerDuels else 0) / int(playerDuels["uhc_losses"] if "uhc_losses" in playerDuels and playerDuels["uhc_losses"] > 0 else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["uhc_kills"] if "uhc_kills" in playerDuels else 0) / int(playerDuels["uhc_deaths"] if "uhc_deaths" in playerDuels and playerDuels["uhc_deaths"] > 0 else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["uhc_damage_dealt"] if "uhc_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["uhc_health_regenerated"] if "uhc_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["uhc_melee_swings"] if "uhc_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["uhc_melee_hits"] if "uhc_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["uhc_bow_shots"] if "uhc_bow_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["uhc_bow_hits"] if "uhc_bow_hits" in playerDuels else 0}'},
                ],
                '2': [
                    {'description': 'Duels - **SkyWars**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["sw_rounds_played"] if "sw_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["sw_wins"] if "sw_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["sw_kills"] if "sw_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["sw_losses"] if "sw_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["sw_deaths"] if "sw_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["sw_wins"] if "sw_wins" in playerDuels else 0) / int(playerDuels["sw_losses"] if "sw_losses" in playerDuels and playerDuels["sw_losses"] > 0 else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["sw_kills"] if "sw_kills" in playerDuels else 0) / int(playerDuels["sw_deaths"] if "sw_deaths" in playerDuels and playerDuels["sw_deaths"] > 0 else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["sw_damage_dealt"] if "sw_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["sw_health_regenerated"] if "sw_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["sw_melee_swings"] if "sw_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["sw_melee_hits"] if "sw_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["sw_bow_shots"] if "sw_bow_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["sw_bow_hits"] if "sw_bow_hits" in playerDuels else 0}'},
                ],
                '3': [
                    {'description': 'Duels - **MegaWalls**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["mw_rounds_played"] if "mw_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["mw_wins"] if "mw_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["mw_kills"] if "mw_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["mw_losses"] if "mw_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["mw_deaths"] if "mw_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["mw_wins"] if "mw_wins" in playerDuels else 0) / int(playerDuels["mw_losses"] if "mw_losses" in playerDuels and playerDuels["mw_losses"] > 0 else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["mw_kills"] if "mw_kills" in playerDuels else 0) / int(playerDuels["mw_deaths"] if "mw_deaths" in playerDuels and playerDuels["mw_deaths"] > 0 else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["mw_damage_dealt"] if "mw_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["mw_health_regenerated"] if "mw_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["mw_melee_swings"] if "mw_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["mw_melee_hits"] if "mw_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["mw_bow_shots"] if "mw_bow_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["mw_bow_hits"] if "mw_bow_hits" in playerDuels else 0}'},
                ],
                '4': [
                    {'description': 'Duels - **Blitz**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["blitz_duel_rounds_played"] if "blitz_duel_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["blitz_duel_wins"] if "blitz_duel_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["blitz_duel_kills"] if "blitz_duel_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["blitz_duel_losses"] if "blitz_duel_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["blitz_duel_deaths"] if "blitz_duel_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["blitz_duel_wins"] if "blitz_duel_wins" in playerDuels else 0) / int(playerDuels["blitz_duel_losses"] if "blitz_duel_losses" in playerDuels else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["blitz_duel_kills"] if "blitz_duel_kills" in playerDuels else 0) / int(playerDuels["blitz_duel_deaths"] if "blitz_duel_deaths" in playerDuels else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["blitz_damage_dealt"] if "blitz_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["blitz_health_regenerated"] if "blitz_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["blitz_melee_swings"] if "blitz_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["blitz_melee_hits"] if "blitz_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["blitz_bow_shots"] if "blitz_bow_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["blitz_bow_hits"] if "blitz_bow_hits" in playerDuels else 0}'},
                ],
                '5': [
                    {'description': 'Duels - **OP**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["op_rounds_played"] if "op_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["op_wins"] if "op_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["op_kills"] if "op_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["op_losses"] if "op_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["op_deaths"] if "op_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["op_wins"] if "op_wins" in playerDuels else 0) / int(playerDuels["op_losses"] if "op_losses" in playerDuels and playerDuels["op_losses"] > 0 else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["op_kills"] if "op_kills" in playerDuels else 0) / int(playerDuels["op_deaths"] if "op_deaths" in playerDuels and playerDuels["op_deaths"] > 0 else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["op_damage_dealt"] if "op_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["op_health_regenerated"] if "op_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["op_melee_swings"] if "op_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["op_melee_hits"] if "op_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["op_bow_shots"] if "op_bow_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["op_bow_hits"] if "op_bow_hits" in playerDuels else 0}'},
                ],
                '6': [
                    {'description': 'Duels - **Classic**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["classic_duel_rounds_played"] if "classic_duel_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["classic_duel_wins"] if "classic_duel_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["classic_duel_kills"] if "classic_duel_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["classic_duel_losses"] if "classic_duel_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["classic_duel_deaths"] if "classic_duel_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["classic_duel_wins"] if "classic_duel_wins" in playerDuels else 0) / int(playerDuels["classic_duel_losses"] if "classic_duel_losses" in playerDuels else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["classic_duel_kills"] if "classic_duel_kills" in playerDuels else 0) / int(playerDuels["classic_duel_deaths"] if "classic_duel_deaths" in playerDuels else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["classic_duel_damage_dealt"] if "classic_duel_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["classic_duel_health_regenerated"] if "classic_duel_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["classic_duel_melee_swings"] if "classic_duel_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["classic_duel_melee_hits"] if "classic_duel_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["classic_duel_bow_shots"] if "classic_duel_bow_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["classic_duel_bow_hits"] if "classic_duel_bow_hits" in playerDuels else 0}'},
                ],
                '7': [
                    {'description': 'Duels - **Bow**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["bow_duel_rounds_played"] if "bow_duel_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["bow_duel_wins"] if "bow_duel_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["bow_duel_kills"] if "bow_duel_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["bow_duel_losses"] if "bow_duel_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["bow_duel_deaths"] if "bow_duel_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["bow_duel_wins"] if "bow_duel_wins" in playerDuels else 0) / int(playerDuels["bow_duel_losses"] if "bow_duel_losses" in playerDuels else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["bow_duel_kills"] if "bow_duel_kills" in playerDuels else 0) / int(playerDuels["bow_duel_deaths"] if "bow_duel_deaths" in playerDuels else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["bow_duel_damage_dealt"] if "bow_duel_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["bow_duel_health_regenerated"] if "bow_duel_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["bow_duel_melee_swings"] if "bow_duel_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["bow_duel_melee_hits"] if "bow_duel_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["bow_duel_bow_shots"] if "bow_duel_bow_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["bow_duel_bow_hits"] if "bow_duel_bow_hits" in playerDuels else 0}'},
                ],
                '8': [
                    {'description': 'Duels - **No Debuff**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["potion_duel_rounds_played"] if "potion_duel_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["potion_duel_wins"] if "potion_duel_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["potion_duel_kills"] if "potion_duel_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["potion_duel_losses"] if "potion_duel_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["potion_duel_deaths"] if "potion_duel_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["potion_duel_wins"] if "potion_duel_wins" in playerDuels else 0) / int(playerDuels["potion_duel_losses"] if "potion_duel_losses" in playerDuels else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["potion_duel_kills"] if "potion_duel_kills" in playerDuels else 0) / int(playerDuels["potion_duel_deaths"] if "potion_duel_deaths" in playerDuels else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["potion_duel_damage_dealt"] if "potion_duel_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["potion_duel_health_regenerated"] if "potion_duel_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["potion_duel_melee_swings"] if "potion_duel_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["potion_duel_melee_hits"] if "potion_duel_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["potion_duel_potion_shots"] if "potion_duel_potion_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["potion_duel_potion_hits"] if "potion_duel_potion_hits" in playerDuels else 0}'},
                ],
                '9': [
                    {'description': 'Duels - **Combo**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["combo_duel_rounds_played"] if "combo_duel_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["combo_duel_wins"] if "combo_duel_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["combo_duel_kills"] if "combo_duel_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["combo_duel_losses"] if "combo_duel_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["combo_duel_deaths"] if "combo_duel_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["combo_duel_wins"] if "combo_duel_wins" in playerDuels else 0) / int(playerDuels["combo_duel_losses"] if "combo_duel_losses" in playerDuels else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["combo_duel_kills"] if "combo_duel_kills" in playerDuels else 0) / int(playerDuels["combo_duel_deaths"] if "combo_duel_deaths" in playerDuels else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["combo_duel_damage_dealt"] if "combo_duel_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["combo_duel_health_regenerated"] if "combo_duel_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["combo_duel_melee_swings"] if "combo_duel_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["combo_duel_melee_hits"] if "combo_duel_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["combo_duel_combo_shots"] if "combo_duel_combo_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["combo_duel_combo_hits"] if "combo_duel_combo_hits" in playerDuels else 0}'},
                ],
                '10': [
                    {'description': 'Duels - **Bridge**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["bridge_duel_rounds_played"] if "bridge_duel_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["bridge_duel_wins"] if "bridge_duel_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["bridge_duel_kills"] if "bridge_duel_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["bridge_duel_losses"] if "bridge_duel_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["bridge_duel_deaths"] if "bridge_duel_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["bridge_duel_wins"] if "bridge_duel_wins" in playerDuels else 0) / int(playerDuels["bridge_duel_losses"] if "bridge_duel_losses" in playerDuels else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["bridge_duel_kills"] if "bridge_duel_kills" in playerDuels else 0) / int(playerDuels["bridge_duel_deaths"] if "bridge_duel_deaths" in playerDuels else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["bridge_duel_damage_dealt"] if "bridge_duel_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["bridge_duel_health_regenerated"] if "bridge_duel_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["bridge_duel_melee_swings"] if "bridge_duel_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["bridge_duel_melee_hits"] if "bridge_duel_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["bridge_duel_bridge_shots"] if "bridge_duel_bridge_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["bridge_duel_bridge_hits"] if "bridge_duel_bridge_hits" in playerDuels else 0}'},
                ],
                '11': [
                    {'description': 'Duels - **Sumo**'},
                    {'name': 'Rounds Played', 'value': f'{playerDuels["sumo_duel_rounds_played"] if "sumo_duel_rounds_played" in playerDuels else 0}', 'inline': False},
                    {'name': 'Wins', 'value': f'{playerDuels["sumo_duel_wins"] if "sumo_duel_wins" in playerDuels else 0}'},
                    {'name': 'Kills', 'value': f'{playerDuels["sumo_duel_kills"] if "sumo_duel_kills" in playerDuels else 0}'},
                    {'name': 'Losses', 'value': f'{playerDuels["sumo_duel_losses"] if "sumo_duel_losses" in playerDuels else 0}'},
                    {'name': 'Deaths', 'value': f'{playerDuels["sumo_duel_deaths"] if "sumo_duel_deaths" in playerDuels else 0}'},
                    {'name': 'WLR', 'value': f'{int(playerDuels["sumo_duel_wins"] if "sumo_duel_wins" in playerDuels else 0) / int(playerDuels["sumo_duel_losses"] if "sumo_duel_losses" in playerDuels else 1):.2f}'},
                    {'name': 'KDR', 'value': f'{int(playerDuels["sumo_duel_kills"] if "sumo_duel_kills" in playerDuels else 0) / int(playerDuels["sumo_duel_deaths"] if "sumo_duel_deaths" in playerDuels else 1):.2f}'},

                    {'name': 'Damage Dealt', 'value': f'{playerDuels["sumo_duel_damage_dealt"] if "sumo_duel_damage_dealt" in playerDuels else 0}'},
                    {'name': 'HP Renegerated', 'value': f'{playerDuels["sumo_duel_health_regenerated"] if "sumo_duel_health_regenerated" in playerDuels else 0}'},
                    {'name': 'Melee Swings', 'value': f'{playerDuels["sumo_duel_melee_swings"] if "sumo_duel_melee_swings" in playerDuels else 0}'},
                    {'name': 'Melee Hits', 'value': f'{playerDuels["sumo_duel_melee_hits"] if "sumo_duel_melee_hits" in playerDuels else 0}'},
                    {'name': 'Bow Shots', 'value': f'{playerDuels["sumo_duel_sumo_shots"] if "sumo_duel_sumo_shots" in playerDuels else 0}'},
                    {'name': 'Bow Hits', 'value': f'{playerDuels["sumo_duel_sumo_hits"] if "sumo_duel_sumo_hits" in playerDuels else 0}'},
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
    h = MurderMystery(bot)
    bot.add_cog(h)
