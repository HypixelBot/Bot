import asyncio
import logging
import re

from cogs.utils.checks import *
from cogs.utils.mojang import *

log = logging.getLogger(__name__)

def list_factory(data):
    items = []
    for i in data:
        items.append(i[0])
    return items

class Hypixel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def description(self, ctx, *, text):
        """Sets up a description which is shown on the hypixel command."""
        if not (await self.bot.is_owner(ctx.author)):
            user = await self.bot.pool.fetchrow('select * from donators where userid=$1', ctx.author.id)
            if not user: return await ctx.send("You don\'t seem to qualify to use this command.\nThis feature is limited to donors only.")
        if len(text)>150: return await ctx.send('Oops, that description looks bigger than what I can handle. (Max. 150)')
        await self.bot.pool.execute("""with upsert as (update donators set phrase=$2 where userid=$1 returning *)
                                        insert into donators (userid, phrase) select $1, $2 where not exists (select * from upsert)""", ctx.author.id, text)
        await ctx.send(f'Your description has successfully been set to "{text}"')

    @commands.group(invoke_without_command = True, name = 'hypixel', aliases=['h'], case_insensitive=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cHypixel(self, ctx, *, user:str = ''):
        """Type `[p]help hypixel` for more information about the command.
            Use hypixel [gamemode] [user] to get game specific stats"""
        return await ctx.invoke(self.bot.get_command("HiddenHypixel"), user)

    ### Bedwars ###

    @cHypixel.group(name ='bedwars', aliases = ['bw', 'bedw', 'bwars'], invoke_without_command=True, case_insensitive=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cBedwars(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenBedwars"), user)

    @cBedwars.command(name='compare', aliases = ["c"])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cBedwarsCompare(self, ctx, user1=None, user2=None):
        return await ctx.invoke(self.bot.get_command("HiddenBedwarsCompare"), user1, user2)

    ### The Pit ###

    @cHypixel.group(name ='pit', invoke_without_command=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPit(self, ctx, user:str=''):
        return await ctx.invoke(self.bot.get_command("HiddenPit"), user)

    @cPit.command(name='contracts')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitContracts(self, ctx, user:str=''):
        return await ctx.invoke(self.bot.get_command("HiddenPitContract"), user)

    @cPit.command(name='lastkills')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitKills(self, ctx, user:str=''):
        return await ctx.invoke(self.bot.get_command("HiddenPitKills"), user)

    @cPit.command(name='position')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitPosition(self, ctx, user:str=''):
        return await ctx.invoke(self.bot.get_command("HiddenPitPosition"), user)

    @cPit.command(name='progress')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitProgress(self, ctx, user:str=''):
        return await ctx.invoke(self.bot.get_command("HiddenPitProgress"), user)

    @cPit.group(name='top')
    async def cPitTop(self, ctx):
        """Shows the leaderboard for the specified game"""
        if ctx.invoked_subcommand is None: return await ctx.send_help(ctx.command)

    @cPitTop.command(name='exp')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopExp(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopExp"))

    @cPitTop.command(name='gold')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopCash(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopCash"))

    @cPitTop.command(name='playtime')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopPlaytime(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopPlaytime"))

    @cPitTop.command(name='kills')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopKills(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopKills"))

    @cPitTop.command(name='renown')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopRenown(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopRenown"))

    @cPitTop.command(name='clicks')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopClicks(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopClicks"))

    @cPitTop.command(name='messages')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopMessages(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopMessages"))

    @cPitTop.command(name='contracts')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopContracts(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopContracts"))

    @cPitTop.command(name='bounty')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopBounty(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopBounty"))

    @cPitTop.command(name='deaths')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopDeaths(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopDeaths"))

    @cPitTop.command(name='streak')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def cPitTopStreak(self, ctx):
        return await ctx.invoke(self.bot.get_command("HiddenPitTopStreak"))

    ### Murder Mystery ###

    @cHypixel.command(name ='murdermystery', aliases = ['mm', 'murderm', 'mmystery'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_mmystery(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenMurderMystery"), user)

    ### Arcade ###

    @cHypixel.command(name ='arcade')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_arcade(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenArcade"), user)

    ### Blitz Survival Games ###

    @cHypixel.command(name ='blitz', aliases = ['survivalgames', 'hungergames', 'bsg'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_blitz(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenBlitz"), user)

    ### Cops And Crims ###

    @cHypixel.command(name ='copsandcrims', aliases = ['cc', 'copsncrims', 'cvc'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_copsncrims(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenCopsAndCrims"), user)

    ### Crazy Walls ###

    @cHypixel.command(name ='crazywalls', aliases = ['cw'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_crazywalls(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenCrazyWalls"), user)

    ### Mega Walls ###

    @cHypixel.command(name ='megawalls', aliases = ['mw'])
    async def _hypixel_megawalls(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenMegaWalls"), user)

    ### The Walls ###

    @cHypixel.command(name ='walls')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_walls(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenWalls"), user)

    ### SkyClash ###

    # @cHypixel.command(name ='skyclash', aliases=['sc'])
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # async def _hypixel_skyclash(self, ctx, user:str = ''):
    #     return await ctx.invoke(self.bot.get_command("HiddenSkyClash"), user)

    ### SkyWars ###

    @cHypixel.command(name ='skywars', aliases = ['sw', 'skyw', 'swars'], no_pm = True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_skywars(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenSkyWars"), user)

    ### Smash Heroes ###

    @cHypixel.command(name ='smashheroes', aliases=['sh'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.is_owner()
    async def _hypixel_smashheroes(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenSmashHeroes"), user)

    ### Speed UHC ###

    @cHypixel.command(name ='speeduhc', aliases=['suhc'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_speeduhc(self, ctx, user:str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenSpeedUHC"), user)

    ### UHC ###

    @cHypixel.command(name ='uhc')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_uhc(self, ctx, user:str=''):
        return await ctx.invoke(self.bot.get_command("HiddenUHC"), user)

    ### Duels ###

    @cHypixel.command(name ='duels')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_duels(self, ctx, user:str=''):
        return await ctx.invoke(self.bot.get_command("HiddenDuels"), user)

    ### Paintball ###

    @cHypixel.command(name='paintball')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_paintball(self, ctx, user: str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenPaintball"), user)

    ### Quake ###

    @cHypixel.command(name='quake')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_quake(self, ctx, user: str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenQuake"), user)

    ### VampireZ ###

    @cHypixel.command(name='vampirez')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_vampirez(self, ctx, user: str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenVampireZ"), user)

    ### BuildBattle ###

    @cHypixel.command(name='buildbattle')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_buildbattle(self, ctx, user: str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenBuildBattle"), user)

    ### TnT Games ###

    @cHypixel.command(name='tntgames')
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def _hypixel_tntgames(self, ctx, user: str = ''):
        return await ctx.invoke(self.bot.get_command("HiddenTnTGames"), user)

    ### Verify ###

    @commands.command(name='verify')
    @commands.cooldown(rate = 1, per = 10, type = commands.BucketType.user)
    async def _verify(self, ctx, *, InGameName:str=None):
        """Verifies your Minecraft account so you don't need to enter your username to check your stats"""
        return await ctx.invoke(self.bot.get_command("HiddenVerify"), InGameName)

    @commands.command(name='unverify')
    @commands.cooldown(rate = 1, per = 10, type = commands.BucketType.user)
    async def _unverify(self, ctx):
        """Unverifies your Minecraft account."""
        return await ctx.invoke(self.bot.get_command("HiddenUnerify"))

    # @commands.group('leaderboard', invoke_without_command = True, aliases=['lb'], case_insensitive=True)
    # @has_voted()
    # async def _leaderboard(self, ctx):
    #     """Shows the leaderboard for the specified game"""
    #     if ctx.invoked_subcommand is None: return await ctx.send_help(ctx.command)
    #
    # @_leaderboard.group('bedwars', invoke_without_command=True, aliases=['bw'], case_insensitive=True)
    # @has_voted()
    # async def bw_lb(self, ctx):
    #     if ctx.invoked_subcommand is None: return await ctx.send_help(ctx.command)
    #
    # @bw_lb.command('level', aliases=['lvl'])
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def bw_lb_level(self, ctx):
    #     """Returns Bedwars Level Leaderboard"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().Bedwars()
    #     leaders = hypixel.GetUsers(leaderboard.bedwars_level()['leaders'])
    #     top = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     em = discord.Embed(title='Bedwars Level Leaderboard')
    #     em.description = top
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = round(float(player.getBedwarsLevel()))
    #         except: stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @bw_lb.command('wins')
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def bw_lb_wins(self, ctx, default:str = 'overall'):
    #     """Returns Bedwars Wins Leaderboard. Modes: overall/weekly"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().Bedwars()
    #     if default == 'weekly':
    #         leaders = hypixel.GetUsers(leaderboard.wins_1()['leaders'])
    #         default = 'Weekly'
    #     else:
    #         leaders = hypixel.GetUsers(leaderboard.wins()['leaders'])
    #         default = 'Overall'
    #     top = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     em = discord.Embed(title=f'Bedwars {default} Wins Leaderboard')
    #     em.description = top
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = f"{player.JSON['stats']['Bedwars']['wins_bedwars']:,}"
    #         except: stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @bw_lb.command('kills')
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def bw_lb_kills(self, ctx, default:str = 'overall'):
    #     """Returns Bedwars Final Kills Leaderboard. Modes: overall/weekly"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().Bedwars()
    #     if default == 'weekly':
    #         leaders = hypixel.GetUsers(leaderboard.final_kills_1()['leaders'])
    #         default = 'Weekly'
    #     else:
    #         leaders = hypixel.GetUsers(leaderboard.final_kills()['leaders'])
    #         default = 'Overall'
    #     top = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     em = discord.Embed(title=f'Bedwars {default} Final Kills Leaderboard')
    #     em.description = top
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = f"{player.JSON['stats']['Bedwars']['final_kills_bedwars']:,}"
    #         except: stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @_leaderboard.group('skywars', invoke_without_command=True, aliases=['sw'], case_insensitive=True)
    # @has_voted()
    # async def sw_lb(self, ctx):
    #     if ctx.invoked_subcommand is None: return await self.bot.formatter.format_help_for(ctx, ctx.command)
    #
    # @sw_lb.command('ratings')
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def sw_lb_ratings(self, ctx):
    #     """Returns Skywars Ratings Leaderboard"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().Skywars()
    #     leaders = hypixel.GetUsers(leaderboard.skywars_rating_a()['leaders'])
    #     top = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     em = discord.Embed(title=f'Skywars Overall Ratings Leaderboard')
    #     em.description = top
    #     message = await ctx.send(embed = em)
    #     # for i, leader in enumerate(leaders):
    #     #     start = datetime.datetime.now()
    #     #     player = self.bot.hypixel.Player(leader)
    #     #     bwwins = player.JSON['stats']['SkyWars']['final_kills_bedwars'] # Ratings
    #     #     leaders[i] = f'{leader} - {bwwins:,}'
    #     #     em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     #     time_taken = (datetime.datetime.now() - start).total_seconds()
    #     #     if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     # await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @sw_lb.command('wins')
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def sw_lb_wins(self, ctx):
    #     """Returns Skywars Wins Leaderboard"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().Skywars()
    #     leaders = hypixel.GetUsers(leaderboard.wins()['leaders'])
    #     top = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     em = discord.Embed(title=f'Skywars Overall Wins Leaderboard')
    #     em.description = top
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = f"{player.JSON['stats']['SkyWars']['wins']:,}"
    #         except: stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @sw_lb.command('kills')
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def sw_lb_kills(self, ctx, default:str = 'overall'):
    #     """Returns Skywars Kills Leaderboard. Modes: overall/monthly/weekly"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().Skywars()
    #     if default == 'weekly':
    #         leaders = hypixel.GetUsers(leaderboard.kills_weekly_1()['leaders'])
    #         default = 'Weekly'
    #     elif default == 'monthly':
    #         leaders = hypixel.GetUsers(leaderboard.kills_monthly_2()['leaders'])
    #         default = 'Monthly'
    #     else:
    #         leaders = hypixel.GetUsers(leaderboard.kills()['leaders'])
    #         default = 'Overall'
    #     em = discord.Embed(title=f'Skywars {default} Wins Leaderboard')
    #     em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = f"{player.JSON['stats']['SkyWars']['kills']:,}"
    #         except: stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @_leaderboard.group('walls', invoke_without_command=True, case_insensitive=True)
    # @has_voted()
    # async def walls_lb(self, ctx):
    #     if ctx.invoked_subcommand is None: return await self.bot.formatter.format_help_for(ctx, ctx.command)
    #
    # @walls_lb.command('kills')
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def walls_lb_kills(self, ctx, default:str = 'overall'):
    #     """Returns Walls Kills Leaderboard. Modes: overall/monthly/weekly"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().Walls()
    #     if default.lower() == 'weekly':
    #         table = leaderboard.weekly_kills()
    #         leaders = hypixel.GetUsers(table['leaders'])
    #         default = 'Weekly'
    #     elif default.lower() == 'monthly':
    #         table = leaderboard.monthly_kills()
    #         leaders = hypixel.GetUsers(table['leaders'])
    #         default = 'Monthly'
    #     else:
    #         table = leaderboard.kills()
    #         leaders = hypixel.GetUsers(table['leaders'])
    #         default = 'Overall'
    #     em = discord.Embed(title=f'Walls {default} Kills Leaderboard')
    #     em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = f"{player.JSON['stats']['Walls'][table['path']]:,}"
    #         except:
    #             stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @_leaderboard.group('murdermystery', invoke_without_command=True, aliases=['mm'], case_insensitive=True)
    # @has_voted()
    # async def mm_lb(self, ctx):
    #     if ctx.invoked_subcommand is None: return await self.bot.formatter.format_help_for(ctx, ctx.command)
    #
    # @mm_lb.command('wins')
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def mm_lb_wins(self, ctx, default:str = 'overall'):
    #     """Returns Murder Mystery Kills Leaderboard. Modes: overall/weekly"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().MurderMystery()
    #     if default == 'weekly':
    #         leaders = hypixel.GetUsers(leaderboard.wins_1()['leaders'])
    #         default = 'Weekly'
    #     else:
    #         leaders = hypixel.GetUsers(leaderboard.wins()['leaders'])
    #         default = 'Overall'
    #     em = discord.Embed(title=f'MurderMystery {default} Wins Leaderboard')
    #     em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = f"{player.JSON['stats']['MurderMystery']['wins']:,}"
    #         except: stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @mm_lb.command('kills')
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def mm_lb_kills(self, ctx, default:str = 'overall'):
    #     """Returns Murder Mystery Kills Leaderboard. Modes: overall/weekly"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().MurderMystery()
    #     if default == 'weekly':
    #         leaders = hypixel.GetUsers(leaderboard.kills_1()['leaders'])
    #         default = 'Weekly'
    #     else:
    #         leaders = hypixel.GetUsers(leaderboard.kills()['leaders'])
    #         default = 'Overall'
    #     em = discord.Embed(title=f'MurderMystery {default} Kills Leaderboard')
    #     em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = f"{player.JSON['stats']['MurderMystery']['kills']:,}"
    #         except: stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
    #
    # @mm_lb.command('murderkills', aliases=['mkills'])
    # @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    # @has_voted()
    # async def mm_lb_mkills(self, ctx, default:str = 'overall'):
    #     """Returns Murder Mystery Kills Leaderboard. Modes: overall/weekly"""
    #     start = datetime.datetime.now()
    #     permissions = ctx.channel.permissions_for(ctx.me)
    #     if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
    #     if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
    #     if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
    #     if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
    #     leaderboard = hypixel.Leaderboards().MurderMystery()
    #     if default == 'weekly':
    #         leaders = hypixel.GetUsers(leaderboard.murderer_kills_1()['leaders'])
    #         default = 'Weekly'
    #     else:
    #         leaders = hypixel.GetUsers(leaderboard.murderer_kills()['leaders'])
    #         default = 'Overall'
    #     em = discord.Embed(title=f'MurderMystery {default} Murderer Kills Leaderboard')
    #     em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #     message = await ctx.send(embed = em)
    #     for i, leader in enumerate(leaders):
    #         start = datetime.datetime.now()
    #         try:
    #             player = self.bot.hypixel.Player(leader)
    #             stats = f"{player.JSON['stats']['MurderMystery']['kills_as_murderer']:,}"
    #         except: stats = 'Non'
    #         leaders[i] = f'{leader} - {stats}'
    #         em.description = '\n'.join([f'{i+1}. {escape(m)}' for i, m in enumerate(leaders)])
    #         time_taken = (datetime.datetime.now() - start).total_seconds()
    #         if time_taken > 0.5: await message.edit(content=None, embed = em)
    #     await message.edit(content=None, embed=em)
    #     time_taken = datetime.datetime.now() - start
    #     logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')

    ### Guild ###

    @commands.command()
    @has_voted()
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def guild(self, ctx, *, search: str=''):
        """Shows Members of a guild.
        You can get a guild from its name or player name
        Notice: Guild names are case sensitive!"""
        return await ctx.invoke(self.bot.get_command("HiddenGuild"), search)

    ### Session ###

    @commands.command('session')
    @has_voted()
    @commands.cooldown(rate = 1, per = 5, type = commands.BucketType.user)
    async def _session(self, ctx, user:str = ''):
        """Information about player's current session"""
        return await ctx.invoke(self.bot.get_command("HiddenSession"), user)

    @commands.command('user', hidden=True)
    @commands.is_owner()
    async def _user(self, ctx, *, member:discord.User = None):
        tickYes = "<:tickYes:315009125694177281>"
        tickNo = "<:tickNo:315009174163685377>"
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not member: member = ctx.author
        data = await ctx.bot.pool.fetch(f"select * from hypixel where userID={member.id}")
        voted = await ctx.bot.pool.fetch(f'select * from votes where userID={member.id} and active is TRUE')
        blacklist = await ctx.bot.pool.fetch(f"select * from blacklist where userID={member.id}")
        em = discord.Embed(color=discord.Color.blue(), title=f'{member} | {member.id}')
        logging.info(data)
        if data:
            ign = await Mojang(self.bot.session).getUser(uuid=data[0]['useruuid'])
        else: ign = "To set your Minecraft account use `verify`"
        info = {
            "owner": f"**Bot Owner**: {tickYes}\n" if member.id == self.bot.owner_id else '',
            "minecraft": f"**Minecraft**: {ign}",
            "voted": f"**Voted**: {tickYes if voted else tickNo}",
            "verified": f"**Verified**: {tickYes if data else tickNo}",
            "blacklisted": f"**Blacklisted**: {blacklist[0]['reason'] if blacklist else tickNo}"
        }
        em.description = f'​\n{info["minecraft"]}\n\n' \
            f'{info["owner"]}' \
            f'{info["voted"]}\n' \
            f'{info["verified"]}\n' \
            f'{info["blacklisted"]}'
        await ctx.send(embed=em)

    async def clear_cache(self):
        await self.bot.wait_until_ready()
        while True:
            await asyncio.sleep(3600)
            self.bot.hypixel.cleanCache()

def setup(bot):
    h = Hypixel(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(h.clear_cache())
    bot.add_cog(h)
