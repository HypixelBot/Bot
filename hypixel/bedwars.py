import datetime

from hypixel.utils.functions import *


class Bedwars(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.group(hidden=True, enabled=False)
    async def HiddenBedwars(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "Bedwars" not in playerJSON["stats"] or len(playerJSON['stats']['Bedwars']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Bedwars before.")
        embeds = self.bedwars(player = player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    @commands.command(hidden=True, enabled=False)
    async def HiddenBedwarsCompare(self, ctx, user1=None, user2=None):
        start = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        if not user1: return
        user1, user2 = await self.utils._get_users(ctx, user1, user2)
        player1 = await self.utils._get_players(user1, ctx)
        if type(player1) is not self.bot.hypixel.Player: return
        player2 = await self.utils._get_players(user2, ctx)
        if type(player2) is not self.bot.hypixel.Player: return
        player1JSON, player2JSON = player1.JSON, player2.JSON
        if "stats" not in player1JSON or "Bedwars" not in player1JSON["stats"] or len(player1JSON['stats']['Bedwars']) < 5: return await ctx.send(f"Doesn't look like {player1.getName()} has played Bedwars before.")
        if "stats" not in player2JSON or "Bedwars" not in player2JSON["stats"] or len(player2JSON['stats']['Bedwars']) < 5: return await ctx.send(f"Doesn't look like {player2.getName()} has played Bedwars before.")
        if player1JSON["uuid"] == player2JSON["uuid"]: return await ctx.send("Can't compare someone with themself.")
        embeds = self.bedwars_compare(player1, player2, self.bot)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)

    def bedwars(self, player):
        playerJSON = player.JSON
        playerRank = player.getRank()
        playerName = player.getName()
        playerSession = player.getSession()
        playerBedwars = playerJSON["stats"]["Bedwars"]
        playerAchievements = playerJSON['achievements']
        onlineStatus = player.getOnlineStatus()
        if 'playerJSON' not in playerJSON:
            playerJSON["achievements"] = {}
            if 'bedwars_wins' not in playerJSON["achievements"]:
                playerJSON["achievements"]["bedwars_wins"] = 0
        if playerRank["rank"] == 'Youtuber': colour = self.utils.rank["RED"][0]
        elif playerRank['rank'].title() in ['Helper', 'Moderator', 'Admin']: colour = self.utils.rank[playerRank['rank'].upper()][0]
        elif "rankPlusColor" in playerJSON: colour = self.utils.rank[playerJSON["rankPlusColor"]][0]
        else: colour = 0x55FFFF
        if playerSession and 'gameType' in playerSession: footer = f'Currently in a {playerSession["gameType"].title()} game'; onlineStatus = True
        else: footer = self.bot.footer
        if onlineStatus:footer_url = 'https://image.ibb.co/h9VNfq/image.png'
        else: footer_url = 'https://image.ibb.co/hwheRV/image.png'
        embeds = {}
        emb = {
            'embed': {
                'title': f'{"["+playerRank["prefix"]+"]" if playerRank["prefix"] else "["+playerRank["rank"]+"]"} {playerName}' if
                playerRank["rank"] != 'Non' else playerName,
                'url': f"https://hypixel.net/player/{playerName}",
                'description': '',
                'color': colour
            },
            'footer': {
                'text': footer,
                'icon_url': footer_url
            },
            'thumbnail': 'https://image.ibb.co/eHggQq/image.png',
            'pages': {
                '0': [
                    {'description': 'Bed Wars - **Overall**'},
                    {'name': 'Level', 'value': playerAchievements['bedwars_level'] if 'bedwars_level' in playerAchievements else 0},
                    {'name': 'Win Streak', 'value': playerBedwars["winstreak"] if 'winstreak' in playerBedwars else 0},
                    {'name': 'Coins', 'value': f'{playerBedwars["coins"] if "coins" in playerBedwars else 0:,}'},
                    {'name': 'Games Played', 'value': f'{playerBedwars["games_played_bedwars"] if "games_played_bedwars" in playerBedwars else 0:,}'},
                    {'name': 'Kills', 'value': f'{playerBedwars["kills_bedwars"] if "kills_bedwars" in playerBedwars else 0:,}'},
                    {'name': 'Wins', 'value': f'{playerBedwars["wins_bedwars"] if "wins_bedwars" in playerBedwars else 0:,}'},
                    {'name': 'Deaths', 'value': f'{playerBedwars["deaths_bedwars"] if "deaths_bedwars" in playerBedwars else 0:,}'},
                    {'name': 'Losses', 'value': f'{playerBedwars["losses_bedwars"] if "losses_bedwars" in playerBedwars else 0:,}'},
                    {'name': 'KDR', 'value': f'{int(playerBedwars["kills_bedwars"] if "kills_bedwars" in playerBedwars else 0) / int(playerBedwars["deaths_bedwars"] if "deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerBedwars["wins_bedwars"] if "wins_bedwars" in playerBedwars else 0) / int(playerBedwars["losses_bedwars"] if "losses_bedwars" in playerBedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{playerBedwars["final_kills_bedwars"] if "final_kills_bedwars" in playerBedwars else 0:,}'},
                    {'name': 'Beds Broken', 'value': f'{playerBedwars["beds_broken_bedwars"] if "beds_broken_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{playerBedwars["final_deaths_bedwars"] if "final_deaths_bedwars" in playerBedwars else 0:,}'},
                    {'name': 'Beds Lost', 'value': f'{playerBedwars["beds_lost_bedwars"] if "beds_lost_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final KDR', 'value': f'{int(playerBedwars["final_kills_bedwars"] if "final_kills_bedwars" in playerBedwars else 0) / int(playerBedwars["final_deaths_bedwars"] if "final_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio', 'value': f'{int(playerBedwars["beds_broken_bedwars"] if "beds_broken_bedwars" in playerBedwars else 0) / int(playerBedwars["beds_lost_bedwars"] if "beds_lost_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Final Kills per game', 'value': f'{(playerBedwars["final_kills_bedwars"] if "final_kills_bedwars" in playerBedwars else 0) / (playerBedwars["games_played_bedwars"] if "games_played_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Beds Broken per game', 'value': f'{(playerBedwars["beds_broken_bedwars"] if "beds_broken_bedwars" in playerBedwars else 0) / (playerBedwars["games_played_bedwars"] if "games_played_bedwars" in playerBedwars else 1):.2f}'},
                ],
                '1': [
                    {'description': 'Bed Wars - **Solo**'},
                    {'name': 'Kills', 'value': f'{playerBedwars["eight_one_kills_bedwars"] if "eight_one_kills_bedwars" in playerBedwars else 0}'},
                    {'name': 'Wins', 'value': f'{playerBedwars["eight_one_wins_bedwars"] if "eight_one_wins_bedwars" in playerBedwars else 0}'},
                    {'name': 'Deaths', 'value': f'{playerBedwars["eight_one_deaths_bedwars"] if "eight_one_deaths_bedwars" in playerBedwars else 0}'},
                    {'name': 'Losses', 'value': f'{playerBedwars["eight_one_losses_bedwars"] if "eight_one_losses_bedwars" in playerBedwars else 0}'},
                    {'name': 'KDR', 'value': f'{int(playerBedwars["eight_one_kills_bedwars"] if "eight_one_kills_bedwars" in playerBedwars else 0) / int(playerBedwars["eight_one_deaths_bedwars"] if "eight_one_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerBedwars["eight_one_wins_bedwars"] if "eight_one_wins_bedwars" in playerBedwars else 0) / int(playerBedwars["eight_one_losses_bedwars"] if "eight_one_losses_bedwars" in playerBedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{playerBedwars["eight_one_final_kills_bedwars"] if "eight_one_final_kills_bedwars" in playerBedwars else 0}'},
                    {'name': 'Beds Broken', 'value': f'{playerBedwars["eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{playerBedwars["eight_one_final_deaths_bedwars"] if "eight_one_final_deaths_bedwars" in playerBedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{playerBedwars["eight_one_beds_lost_bedwars"] if "eight_one_beds_lost_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final KDR', 'value': f'{int(playerBedwars["eight_one_final_kills_bedwars"] if "eight_one_final_kills_bedwars" in playerBedwars else 0) / int(playerBedwars["eight_one_final_deaths_bedwars"] if "eight_one_final_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio', 'value': f'{int(playerBedwars["eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in playerBedwars else 0) / int(playerBedwars["eight_one_beds_lost_bedwars"] if "eight_one_beds_lost_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Final Kills per game', 'value': f'{(playerBedwars["eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in playerBedwars else 0) / (playerBedwars["eight_one_games_played_bedwars"] if "eight_one_games_played_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Beds Broken per game', 'value': f'{(playerBedwars["eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in playerBedwars else 0) / (playerBedwars["eight_one_games_played_bedwars"] if "eight_one_games_played_bedwars" in playerBedwars else 1):.2f}'},
                ],
                '2': [
                    {'description': 'Bed Wars - **Doubles**'},
                    {'name': 'Kills', 'value': f'{playerBedwars["eight_two_kills_bedwars"] if "eight_two_kills_bedwars" in playerBedwars else 0}'},
                    {'name': 'Wins', 'value': f'{playerBedwars["eight_two_wins_bedwars"] if "eight_two_wins_bedwars" in playerBedwars else 0}'},
                    {'name': 'Deaths', 'value': f'{playerBedwars["eight_two_deaths_bedwars"] if "eight_two_deaths_bedwars" in playerBedwars else 0}'},
                    {'name': 'Losses', 'value': f'{playerBedwars["eight_two_losses_bedwars"] if "eight_two_losses_bedwars" in playerBedwars else 0}'},
                    {'name': 'KDR', 'value': f'{int(playerBedwars["eight_two_kills_bedwars"] if "eight_two_kills_bedwars" in playerBedwars else 0) / int(playerBedwars["eight_two_deaths_bedwars"] if "eight_two_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerBedwars["eight_two_wins_bedwars"] if "eight_two_wins_bedwars" in playerBedwars else 0) / int(playerBedwars["eight_two_losses_bedwars"] if "eight_two_losses_bedwars" in playerBedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{playerBedwars["eight_two_final_kills_bedwars"] if "eight_two_final_kills_bedwars" in playerBedwars else 0}'},
                    {'name': 'Beds Broken', 'value': f'{playerBedwars["eight_two_beds_broken_bedwars"] if "eight_two_beds_broken_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{playerBedwars["eight_two_final_deaths_bedwars"] if "eight_two_final_deaths_bedwars" in playerBedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{playerBedwars["eight_two_beds_lost_bedwars"] if "eight_two_beds_lost_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final KDR', 'value': f'{int(playerBedwars["eight_two_final_kills_bedwars"] if "eight_two_final_kills_bedwars" in playerBedwars else 0   ) / int(playerBedwars["eight_two_final_deaths_bedwars"] if "eight_two_final_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio', 'value': f'{int(playerBedwars["eight_two_beds_broken_bedwars"] if "eight_two_beds_broken_bedwars" in playerBedwars else 0) / int(playerBedwars["eight_two_beds_lost_bedwars"] if "eight_two_beds_lost_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Final Kills per game', 'value': f'{(playerBedwars["eight_two_final_kills_bedwars"] if "eight_two_final_kills_bedwars" in playerBedwars else 0) / (playerBedwars["eight_two_games_played_bedwars"] if "eight_two_games_played_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Beds Broken per game', 'value': f'{(playerBedwars["eight_two_beds_broken_bedwars"] if "eight_two_beds_broken_bedwars" in playerBedwars else 0) / (playerBedwars["eight_two_games_played_bedwars"] if "eight_two_games_played_bedwars" in playerBedwars else 1):.2f}'},
                ],
                '3': [
                    {'description': 'Bed Wars - **Teams of Three**'},
                    {'name': 'Kills', 'value': f'{playerBedwars["four_three_kills_bedwars"] if "four_three_kills_bedwars" in playerBedwars else 0}'},
                    {'name': 'Wins', 'value': f'{playerBedwars["four_three_wins_bedwars"] if "four_three_wins_bedwars" in playerBedwars else 0}'},
                    {'name': 'Deaths', 'value': f'{playerBedwars["four_three_deaths_bedwars"] if "four_three_deaths_bedwars" in playerBedwars else 0}'},
                    {'name': 'Losses', 'value': f'{playerBedwars["four_three_losses_bedwars"] if "four_three_losses_bedwars" in playerBedwars else 0}'},
                    {'name': 'KDR', 'value': f'{int(playerBedwars["four_three_kills_bedwars"] if "four_three_kills_bedwars" in playerBedwars else 0) / int(playerBedwars["four_three_deaths_bedwars"] if "four_three_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerBedwars["four_three_wins_bedwars"] if "four_three_wins_bedwars" in playerBedwars else 0) / int(playerBedwars["four_three_losses_bedwars"] if "four_three_losses_bedwars" in playerBedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{playerBedwars["four_three_final_kills_bedwars"] if "four_three_final_kills_bedwars" in playerBedwars else 0}'},
                    {'name': 'Beds Broken', 'value': f'{playerBedwars["four_three_beds_broken_bedwars"] if "four_three_beds_broken_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{playerBedwars["four_three_final_deaths_bedwars"] if "four_three_final_deaths_bedwars" in playerBedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{playerBedwars["four_three_beds_lost_bedwars"] if "four_three_beds_lost_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final KDR', 'value': f'{int(playerBedwars["four_three_final_kills_bedwars"] if "four_three_final_kills_bedwars" in playerBedwars else 0) / int(playerBedwars["four_three_final_deaths_bedwars"] if "four_three_final_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio', 'value': f'{int(playerBedwars["four_three_beds_broken_bedwars"] if "four_three_beds_broken_bedwars" in playerBedwars else 0) / int(playerBedwars["four_three_beds_lost_bedwars"] if "four_three_beds_lost_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Final Kills per game', 'value': f'{(playerBedwars["four_three_final_kills_bedwars"] if "four_three_final_kills_bedwars" in playerBedwars else 0) / (playerBedwars["four_three_games_played_bedwars"] if "four_three_games_played_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Beds Broken per game', 'value': f'{(playerBedwars["four_three_beds_broken_bedwars"] if "four_three_beds_broken_bedwars" in playerBedwars else 0) / (playerBedwars["four_three_games_played_bedwars"] if "four_three_games_played_bedwars" in playerBedwars else 1):.2f}'},
                ],
                '4': [
                    {'description': 'Bed Wars - **Teams of Four**'},
                    {'name': 'Kills', 'value': f'{playerBedwars["four_four_kills_bedwars"] if "four_four_kills_bedwars" in playerBedwars else 0}'},
                    {'name': 'Wins', 'value': f'{playerBedwars["four_four_wins_bedwars"] if "four_four_wins_bedwars" in playerBedwars else 0}'},
                    {'name': 'Deaths', 'value': f'{playerBedwars["four_four_deaths_bedwars"] if "four_four_deaths_bedwars" in playerBedwars else 0}'},
                    {'name': 'Losses', 'value': f'{playerBedwars["four_four_losses_bedwars"] if "four_four_losses_bedwars" in playerBedwars else 0}'},
                    {'name': 'KDR', 'value': f'{int(playerBedwars["four_four_kills_bedwars"] if "four_four_kills_bedwars" in playerBedwars else 0) / int(playerBedwars["four_four_deaths_bedwars"] if "four_four_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(playerBedwars["four_four_wins_bedwars"] if "four_four_wins_bedwars" in playerBedwars else 0) / int(playerBedwars["four_four_losses_bedwars"] if "four_four_losses_bedwars" in playerBedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{playerBedwars["four_four_final_kills_bedwars"] if "four_four_final_kills_bedwars" in playerBedwars else 0}'},
                    {'name': 'Beds Broken', 'value': f'{playerBedwars["four_four_beds_broken_bedwars"] if "four_four_beds_broken_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{playerBedwars["four_four_final_deaths_bedwars"] if "four_four_final_deaths_bedwars" in playerBedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{playerBedwars["four_four_beds_lost_bedwars"] if "four_four_beds_lost_bedwars" in playerBedwars else 0}'},
                    {'name': 'Final KDR', 'value': f'{int(playerBedwars["four_four_final_kills_bedwars"] if "four_four_final_kills_bedwars" in playerBedwars else 0) / int(playerBedwars["four_four_final_deaths_bedwars"] if "four_four_final_deaths_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio', 'value': f'{int(playerBedwars["four_four_beds_broken_bedwars"] if "four_four_beds_broken_bedwars" in playerBedwars else 0) / int(playerBedwars["four_four_beds_lost_bedwars"] if "four_four_beds_lost_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Final Kills per game', 'value': f'{(playerBedwars["four_four_final_kills_bedwars"] if "four_four_final_kills_bedwars" in playerBedwars else 0) / (playerBedwars["four_four_games_played_bedwars"] if "four_four_games_played_bedwars" in playerBedwars else 1):.2f}'},
                    {'name': 'Avg. Beds Broken per game', 'value': f'{(playerBedwars["four_four_beds_broken_bedwars"] if "four_four_beds_broken_bedwars" in playerBedwars else 0) / (playerBedwars["four_four_games_played_bedwars"] if "four_four_games_played_bedwars" in playerBedwars else 1):.2f}'},
                ]
            },
            # 'image': f'https://visage.surgeplay.com/full/256/{playerName}'
        }
        embed = discord.Embed(**emb["embed"])
        embed.set_thumbnail(url = emb["thumbnail"])
        for page in range(len(emb["pages"])):
            for field in emb["pages"][str(page)]:
                if 'description' in field:
                    embed.description = field["description"]
                else:
                    embed.add_field(**field)
            if 'image' in emb:
                embed.set_image(url = emb["image"])
            embed.set_footer(text = emb["footer"]["text"], icon_url = emb["footer"]["icon_url"])
            embeds[page] = embed
            del embed
            embed = discord.Embed(**emb["embed"])
            embed.set_thumbnail(url = emb["thumbnail"])
        return embeds

    def bedwars_compare(self, player1, player2, bot):
        player1JSON, player2JSON = player1.JSON, player2.JSON
        player1Rank, player2Rank = player1.getRank(), player2.getRank()
        player1Name, player2Name = player1.getName(), player2.getName()
        player1Level, player2Level = player1JSON['achievements']['bedwars_level'] if 'bedwars_level' in player1JSON['achievements'] else 0 \
            , player2JSON['achievements']['bedwars_level'] if 'bedwars_level' in player2JSON['achievements'] else 0
        player1Bedwars, player2Bedwars = player1JSON["stats"]["Bedwars"], player2JSON["stats"]["Bedwars"]
        if 'bedwars_wins' not in player1JSON["achievements"]: player1JSON["achievements"]["bedwars_wins"] = 0
        if 'bedwars_wins' not in player2JSON["achievements"]: player2JSON["achievements"]["bedwars_wins"] = 0
        embeds = {}
        if player1Rank["rank"] != 'Non': player1Title = f'{"["+player1Rank["prefix"]+"]" if player1Rank["prefix"] else "["+player1Rank["rank"]+"]"} {player1Name}'
        else: player1Title = player1Name
        if player2Rank["rank"] != 'Non': player2Title = f'{"["+player2Rank["prefix"]+"]" if player2Rank["prefix"] else "["+player2Rank["rank"]+"]"} {player2Name}'
        else: player2Title = player2Name
        emb = {
            'embed': {
                'title': f'{player1Title} | {player2Title}',

                'description': '',
            },
            'footer': {
                'text': self.bot.footer,
                'icon_url': bot.user.avatar_url
            },
            'thumbnail': 'https://image.ibb.co/eHggQq/image.png',
            'pages': {
                '0': [
                    {'description': 'Bed Wars - **Overall**'},
                    {'name': 'Level', 'value': f'{player1Level} | {player2Level}'},
                    {'name': 'Coins', 'value': f'{player1Bedwars["coins"] if "coins" in player1Bedwars else 0:,} | {player2Bedwars["coins"] if "coins" in player2Bedwars else 0:,}'},
                    {'name': 'Kills', 'value': f'{player1Bedwars["kills_bedwars"] if "kills_bedwars" in player1Bedwars else 0:,} | {player2Bedwars["kills_bedwars"] if "kills_bedwars" in player2Bedwars else 0:,}'},
                    {'name': 'Deaths', 'value': f'{player1Bedwars["deaths_bedwars"] if "deaths_bedwars" in player1Bedwars else 0:,} | {player2Bedwars["deaths_bedwars"] if "deaths_bedwars" in player2Bedwars else 0:,}'},
                    {'name': 'Wins', 'value': f'{player1JSON["achievements"]["bedwars_wins"] if "bedwars_wins" in player1JSON["achievements"] else 0:,} | {player2JSON["achievements"]["bedwars_wins"] if "bedwars_wins" in player2JSON["achievements"] else 0:,}'},
                    {'name': 'Losses', 'value': f'{player1Bedwars["losses_bedwars"] if "losses_bedwars" in player1Bedwars else 0:,} | {player2Bedwars["losses_bedwars"] if "losses_bedwars" in player2Bedwars else 0:,}'},
                    {'name': 'KDR', 'value': f'{int(player1Bedwars["kills_bedwars"] if "kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["deaths_bedwars"] if "deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["kills_bedwars"] if "kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["deaths_bedwars"] if "deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(player1JSON["achievements"]["bedwars_wins"] if "bedwars_wins" in player1JSON["achievements"] else 0) / int(player1Bedwars["losses_bedwars"] if "losses_bedwars" in player1Bedwars else 1):.2f} | {int(player2JSON["achievements"]["bedwars_wins"] if "bedwars_wins" in player2JSON["achievements"] else 0) / int(player2Bedwars["losses_bedwars"] if "losses_bedwars" in player2Bedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{player1Bedwars["final_kills_bedwars"] if "final_kills_bedwars" in player1Bedwars else 0:,} | {player2Bedwars["final_kills_bedwars"] if "final_kills_bedwars" in player2Bedwars else 0:,}'},
                    {'name': 'Final Deaths', 'value': f'{player1Bedwars["final_deaths_bedwars"] if "final_deaths_bedwars" in player1Bedwars else 0:,} | {player2Bedwars["final_deaths_bedwars"] if "final_deaths_bedwars" in player2Bedwars else 0:,}'},
                    {'name': 'Beds Broken', 'value': f'{player1Bedwars["beds_broken_bedwars"] if "beds_broken_bedwars" in player1Bedwars else 0} | {player2Bedwars["beds_broken_bedwars"] if "beds_broken_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{player1Bedwars["beds_lost_bedwars"] if "beds_lost_bedwars" in player1Bedwars else 0} | {player2Bedwars["beds_lost_bedwars"] if "beds_lost_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final KDR', 'value': f'{int(player1Bedwars["final_kills_bedwars"] if "final_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["final_deaths_bedwars"] if "final_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["final_kills_bedwars"] if "final_kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["final_deaths_bedwars"] if "final_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio', 'value': f'{int(player1Bedwars["beds_broken_bedwars"] if "beds_broken_bedwars" in player1Bedwars else 0) / int(player1Bedwars["beds_lost_bedwars"] if "beds_lost_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["beds_broken_bedwars"] if "beds_broken_bedwars" in player2Bedwars else 0) / int(player2Bedwars["beds_lost_bedwars"] if "beds_lost_bedwars" in player2Bedwars else 1):.2f}'},
                ],
                '1': [
                    {'description': 'Bed Wars - **Solo**'},
                    {'name': 'Kills', 'value': f'{player1Bedwars["eight_one_kills_bedwars"] if "eight_one_kills_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_one_kills_bedwars"] if "eight_one_kills_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Deaths', 'value': f'{player1Bedwars["eight_one_deaths_bedwars"] if "eight_one_deaths_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_one_deaths_bedwars"] if "eight_one_deaths_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Wins', 'value': f'{player1Bedwars["eight_one_wins_bedwars"] if "eight_one_wins_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_one_wins_bedwars"] if "eight_one_wins_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Losses', 'value': f'{player1Bedwars["eight_one_losses_bedwars"] if "eight_one_losses_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_one_losses_bedwars"] if "eight_one_losses_bedwars" in player2Bedwars else 0}'},
                    {'name': 'KDR', 'value': f'{int(player1Bedwars["eight_one_kills_bedwars"] if "eight_one_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["eight_one_deaths_bedwars"] if "eight_one_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["eight_one_kills_bedwars"] if "eight_one_kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["eight_one_deaths_bedwars"] if "eight_one_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(player1Bedwars["eight_one_wins_bedwars"] if "eight_one_wins_bedwars" in player1Bedwars else 0) / int(player1Bedwars["eight_one_losses_bedwars"] if "eight_one_losses_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["eight_one_wins_bedwars"] if "eight_one_wins_bedwars" in player2Bedwars else 0) / int(player2Bedwars["eight_one_losses_bedwars"] if "eight_one_losses_bedwars" in player2Bedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{player1Bedwars["eight_one_final_kills_bedwars"] if "eight_one_final_kills_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_one_final_kills_bedwars"] if "eight_one_final_kills_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{player1Bedwars["eight_one_final_deaths_bedwars"] if "eight_one_final_deaths_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_one_final_deaths_bedwars"] if "eight_one_final_deaths_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Broken', 'value': f'{player1Bedwars["eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{player1Bedwars["eight_one_beds_lost_bedwars"] if "eight_one_beds_lost_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_one_beds_lost_bedwars"] if "eight_one_beds_lost_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final KDR',
                     f'value': f'{int(player1Bedwars["eight_one_final_kills_bedwars"] if "eight_one_final_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["eight_one_final_deaths_bedwars"] if "eight_one_final_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["eight_one_final_kills_bedwars"] if "eight_one_final_kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["eight_one_final_deaths_bedwars"] if "eight_one_final_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio',
                     f'value': f'{int(player1Bedwars["eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in player1Bedwars else 0) / int(player1Bedwars["eight_one_beds_lost_bedwars"] if "eight_one_beds_lost_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in player2Bedwars else 0) / int(player2Bedwars["eight_one_beds_lost_bedwars"] if "eight_one_beds_lost_bedwars" in player2Bedwars else 1):.2f}'},
                ],
                '2': [
                    {'description': 'Bed Wars - **Doubles**'},
                    {'name': 'Kills', 'value': f'{player1Bedwars["eight_two_kills_bedwars"] if "eight_two_kills_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_two_kills_bedwars"] if "eight_two_kills_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Deaths', 'value': f'{player1Bedwars["eight_two_deaths_bedwars"] if "eight_two_deaths_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_two_deaths_bedwars"] if "eight_two_deaths_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Wins', 'value': f'{player1Bedwars["eight_two_wins_bedwars"] if "eight_two_wins_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_two_wins_bedwars"] if "eight_two_wins_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Losses', 'value': f'{player1Bedwars["eight_two_losses_bedwars"] if "eight_two_losses_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_two_losses_bedwars"] if "eight_two_losses_bedwars" in player2Bedwars else 0}'},
                    {'name': 'KDR', 'value': f'{int(player1Bedwars["eight_two_kills_bedwars"] if "eight_two_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["eight_two_deaths_bedwars"] if "eight_two_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["eight_two_kills_bedwars"] if "eight_two_kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["eight_two_deaths_bedwars"] if "eight_two_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(player1Bedwars["eight_two_wins_bedwars"] if "eight_two_wins_bedwars" in player1Bedwars else 0) / int(player1Bedwars["eight_two_losses_bedwars"] if "eight_two_losses_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["eight_two_wins_bedwars"] if "eight_two_wins_bedwars" in player2Bedwars else 0) / int(player2Bedwars["eight_two_losses_bedwars"] if "eight_two_losses_bedwars" in player2Bedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{player1Bedwars["eight_two_final_kills_bedwars"] if "eight_two_final_kills_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_two_final_kills_bedwars"] if "eight_two_final_kills_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{player1Bedwars["eight_two_final_deaths_bedwars"] if "eight_two_final_deaths_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_two_final_deaths_bedwars"] if "eight_two_final_deaths_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Broken', 'value': f'{player1Bedwars["eight_two_beds_broken_bedwars"] if "eight_two_beds_broken_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_two_beds_broken_bedwars"] if "eight_two_beds_broken_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{player1Bedwars["eight_two_beds_lost_bedwars"] if "eight_two_beds_lost_bedwars" in player1Bedwars else 0} | {player2Bedwars["eight_two_beds_lost_bedwars"] if "eight_two_beds_lost_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final KDR',
                     'value': f'{int(player1Bedwars["eight_two_final_kills_bedwars"] if "eight_two_final_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["eight_two_final_deaths_bedwars"] if "eight_two_final_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["eight_two_final_kills_bedwars"] if "eight_two_final_kills_bedwars" in player2Bedwars else 0   ) / int(player2Bedwars["eight_two_final_deaths_bedwars"] if "eight_two_final_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio',
                     'value': f'{int(player1Bedwars["eight_two_beds_broken_bedwars"] if "eight_two_beds_broken_bedwars" in player1Bedwars else 0) / int(player1Bedwars["eight_two_beds_lost_bedwars"] if "eight_two_beds_lost_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["eight_two_beds_broken_bedwars"] if "eight_two_beds_broken_bedwars" in player2Bedwars else 0) / int(player2Bedwars["eight_two_beds_lost_bedwars"] if "eight_two_beds_lost_bedwars" in player2Bedwars else 1):.2f}'},
                ],
                '3': [
                    {'description': 'Bed Wars - **Teams of Three**'},
                    {'name': 'Kills', 'value': f'{player1Bedwars["four_three_kills_bedwars"] if "four_three_kills_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_three_kills_bedwars"] if "four_three_kills_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Deaths', 'value': f'{player1Bedwars["four_three_deaths_bedwars"] if "four_three_deaths_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_three_deaths_bedwars"] if "four_three_deaths_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Wins', 'value': f'{player1Bedwars["four_three_wins_bedwars"] if "four_three_wins_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_three_wins_bedwars"] if "four_three_wins_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Losses', 'value': f'{player1Bedwars["four_three_losses_bedwars"] if "four_three_losses_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_three_losses_bedwars"] if "four_three_losses_bedwars" in player2Bedwars else 0}'},
                    {'name': 'KDR', 'value': f'{int(player1Bedwars["four_three_kills_bedwars"] if "four_three_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["four_three_deaths_bedwars"] if "four_three_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["four_three_kills_bedwars"] if "four_three_kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["four_three_deaths_bedwars"] if "four_three_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(player1Bedwars["four_three_wins_bedwars"] if "four_three_wins_bedwars" in player1Bedwars else 0) / int(player1Bedwars["four_three_losses_bedwars"] if "four_three_losses_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["four_three_wins_bedwars"] if "four_three_wins_bedwars" in player2Bedwars else 0) / int(player2Bedwars["four_three_losses_bedwars"] if "four_three_losses_bedwars" in player2Bedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{player1Bedwars["four_three_final_kills_bedwars"] if "four_three_final_kills_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_three_final_kills_bedwars"] if "four_three_final_kills_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{player1Bedwars["four_three_final_deaths_bedwars"] if "four_three_final_deaths_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_three_final_deaths_bedwars"] if "four_three_final_deaths_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Broken', 'value': f'{player1Bedwars["four_three_beds_broken_bedwars"] if "four_three_beds_broken_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_three_beds_broken_bedwars"] if "four_three_beds_broken_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{player1Bedwars["four_three_beds_lost_bedwars"] if "four_three_beds_lost_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_three_beds_lost_bedwars"] if "four_three_beds_lost_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final KDR',
                     'value': f'{int(player1Bedwars["four_three_final_kills_bedwars"] if "four_three_final_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["four_three_final_deaths_bedwars"] if "four_three_final_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["four_three_final_kills_bedwars"] if "four_three_final_kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["four_three_final_deaths_bedwars"] if "four_three_final_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio',
                     'value': f'{int(player1Bedwars["four_three_beds_broken_bedwars"] if "four_three_beds_broken_bedwars" in player1Bedwars else 0) / int(player1Bedwars["four_three_beds_lost_bedwars"] if "four_three_beds_lost_bedwars" in player1Bedwars else 1):.2f} | f{int(player2Bedwars["four_three_beds_broken_bedwars"] if "four_three_beds_broken_bedwars" in player2Bedwars else 0) / int(player2Bedwars["four_three_beds_lost_bedwars"] if "four_three_beds_lost_bedwars" in player2Bedwars else 1):.2f}'},
                ],
                '4': [
                    {'description': 'Bed Wars - **Teams of Four**'},
                    {'name': 'Kills', 'value': f'{player1Bedwars["four_four_kills_bedwars"] if "four_four_kills_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_four_kills_bedwars"] if "four_four_kills_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Deaths', 'value': f'{player1Bedwars["four_four_deaths_bedwars"] if "four_four_deaths_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_four_deaths_bedwars"] if "four_four_deaths_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Wins', 'value': f'{player1Bedwars["four_four_wins_bedwars"] if "four_four_wins_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_four_wins_bedwars"] if "four_four_wins_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Losses', 'value': f'{player1Bedwars["four_four_losses_bedwars"] if "four_four_losses_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_four_losses_bedwars"] if "four_four_losses_bedwars" in player2Bedwars else 0}'},
                    {'name': 'KDR', 'value': f'{int(player1Bedwars["four_four_kills_bedwars"] if "four_four_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["four_four_deaths_bedwars"] if "four_four_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["four_four_kills_bedwars"] if "four_four_kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["four_four_deaths_bedwars"] if "four_four_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'WLR', 'value': f'{int(player1Bedwars["four_four_wins_bedwars"] if "four_four_wins_bedwars" in player1Bedwars else 0) / int(player1Bedwars["four_four_losses_bedwars"] if "four_four_losses_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["four_four_wins_bedwars"] if "four_four_wins_bedwars" in player2Bedwars else 0) / int(player2Bedwars["four_four_losses_bedwars"] if "four_four_losses_bedwars" in player2Bedwars else 1):.2f}'},

                    {'name': 'Final Kills', 'value': f'{player1Bedwars["four_four_final_kills_bedwars"] if "four_four_final_kills_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_four_final_kills_bedwars"] if "four_four_final_kills_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final Deaths', 'value': f'{player1Bedwars["four_four_final_deaths_bedwars"] if "four_four_final_deaths_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_four_final_deaths_bedwars"] if "four_four_final_deaths_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Broken', 'value': f'{player1Bedwars["four_four_beds_broken_bedwars"] if "four_four_beds_broken_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_four_beds_broken_bedwars"] if "four_four_beds_broken_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Beds Lost', 'value': f'{player1Bedwars["four_four_beds_lost_bedwars"] if "four_four_beds_lost_bedwars" in player1Bedwars else 0} | {player2Bedwars["four_four_beds_lost_bedwars"] if "four_four_beds_lost_bedwars" in player2Bedwars else 0}'},
                    {'name': 'Final KDR',
                     'value': f'{int(player1Bedwars["four_four_final_kills_bedwars"] if "four_four_final_kills_bedwars" in player1Bedwars else 0) / int(player1Bedwars["four_four_final_deaths_bedwars"] if "four_four_final_deaths_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["four_four_final_kills_bedwars"] if "four_four_final_kills_bedwars" in player2Bedwars else 0) / int(player2Bedwars["four_four_final_deaths_bedwars"] if "four_four_final_deaths_bedwars" in player2Bedwars else 1):.2f}'},
                    {'name': 'Beds Broken/Lost Ratio',
                     'value': f'{int(player1Bedwars["four_four_beds_broken_bedwars"] if "four_four_beds_broken_bedwars" in player1Bedwars else 0) / int(player1Bedwars["four_four_beds_lost_bedwars"] if "four_four_beds_lost_bedwars" in player1Bedwars else 1):.2f} | {int(player2Bedwars["four_four_beds_broken_bedwars"] if "four_four_beds_broken_bedwars" in player2Bedwars else 0) / int(player2Bedwars["four_four_beds_lost_bedwars"] if "four_four_beds_lost_bedwars" in player2Bedwars else 1):.2f}'},
                ]
            }
        }
        embed = discord.Embed(**emb["embed"])
        embed.set_thumbnail(url=emb["thumbnail"])
        for page in range(len(emb["pages"])):
            for field in emb["pages"][str(page)]:
                if 'description' in field:
                    embed.description = field["description"]
                else:
                    embed.add_field(**field)
            embed.set_footer(text=emb["footer"]["text"], icon_url=emb["footer"]["icon_url"])
            embeds[page] = embed
            del embed
            embed = discord.Embed(**emb["embed"])
            embed.set_thumbnail(url=emb["thumbnail"])
        return embeds

def setup(bot):
    h = Bedwars(bot)
    bot.add_cog(h)
