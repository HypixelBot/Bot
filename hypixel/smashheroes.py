import datetime

from hypixel.utils.functions import *


class MurderMystery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenSmashHeroes(self, ctx, user):
        start = datetime.datetime.now()
        player = await self.utils.findUser(ctx, user)
        if type(player) != Player: return
        playerJSON = player.JSON
        if "stats" not in playerJSON or "SuperSmash" not in playerJSON["stats"] or len(playerJSON['stats']['SuperSmash']) < 5: return await ctx.send(f"Doesn't look like `{player.getName()}` has played Smash Heroes before.")
        embeds = self.SmashHeroes(player)
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        await self.utils.send(ctx, embeds = embeds)
        await self.utils._discord_account(ctx, playerJSON, player.getRank()["rank"])

    def SmashHeroes(self, player):
        pass

def setup(bot):
    h = MurderMystery(bot)
    bot.add_cog(h)
