from cogs.utils.chat_formatting import *
from hypixel.utils.functions import *


class Verfiy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenVerify(self, ctx, InGameName):
        user = InGameName
        userCode = f"{str(ctx.author.id)[-6:]}#{ctx.author.discriminator}"
        if not user: return await ctx.send_help(ctx.command)
        try: player = self.bot.hypixel.Player(user, cache=False)
        except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
        except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
        except self.bot.hypixel.HypixelAPIThrottle: return await ctx.send('There\'s a global throttle. Try again later.')
        playerName = player.getName()
        playerUUID = player.UUID
        playerJSON = player.JSON
        playerDiscord = playerJSON["socialMedia"]["links"]["DISCORD"] if 'socialMedia' in playerJSON and 'links' in playerJSON["socialMedia"] and 'DISCORD' in playerJSON["socialMedia"]["links"] else None
        isVerified = await self.bot.pool.fetchrow("select * from hypixel where userid=$1", ctx.author.id)
        if isVerified and isVerified['useruuid'] == playerUUID:
            await ctx.send(f'You\'re already verified as {playerName}.')
        else:
            if playerDiscord != userCode:
                return await ctx.send(f'{ctx.author.mention} your Hypixel social settings don\'t seem to match the ones expected! Make sure you\'ve set your discord on hypixel to `{str(ctx.author.id)[-6:]}#{ctx.author.discriminator}`\n'
                               f'Verification Tutorial: <https://youtu.be/LiUcDhLjLDc>')

            data = await self.bot.pool.fetchrow("select userid from hypixel where useruuid=$1", playerUUID)
            if data: await self.bot.pool.execute('update hypixel set userid=$1 where useruuid=$2', ctx.author.id, playerUUID)
            else: await self.bot.pool.execute('insert into hypixel(userid, useruuid) values($1, $2)', ctx.author.id, playerUUID)
            await ctx.send(f'You have been successfully verified as {playerName}')
        return await self.utils.updateRole(ctx, player.getRank()['rank'], playerJSON)
        # @todo continue
        # if playerDiscord == userCode: match = True
        # data = await self.bot.pool.fetchrow("select userid from hypixel where useruuid=$1", playerUUID)
        # if data and not match:
        #     if self.bot.get_user(data['userid']) == ctx.author: return await ctx.send(f'You\'ve already verified yourself as `{playerName}`')
        #     return await ctx.send(f'That player is already assigned to someone else')
        # elif data: uuidExists = True
        # data = await self.bot.pool.fetchrow("select useruuid from hypixel where userid=$1", ctx.author.id)
        # if data: verified = True
        # if match:
        #     if verified: await self.bot.pool.execute("update hypixel set useruuid=$1 where userID=$2", playerUUID, ctx.author.id)
        #     elif uuidExists: await self.bot.pool.execute("update hypixel set userid=$1 where useruuid=$2", ctx.author.id, playerUUID)
        #     else: await self.bot.pool.execute("insert into hypixel values ($1, $2)", ctx.author.id, playerUUID)
        #     await ctx.send(f'You have been verified `{playerName}`')
        #     return await self.utils.updateRole(ctx, player.getRank()['rank'], playerJSON)
        # else:
        #     await ctx.send(f'{ctx.author.mention} your Discord account is not linked! Make sure you\'ve set your discord on hypixel to `{str(ctx.author.id)[-6:]}#{ctx.author.discriminator}`\n'
        #                    f'Verification Tutorial: <https://youtu.be/LiUcDhLjLDc>')
        #     # or <https://m.wikihow.com/Link-a-Discord-Account-with-a-Hypixel-Profile>

    @commands.command(hidden=True, enabled=False)
    async def HiddenUnerify(self, ctx):
        data = await self.bot.pool.fetchrow("select * from hypixel where userid=$1", ctx.author.id)
        if data:
            await self.bot.pool.execute('delete from hypixel where userid=$1', ctx.author.id)
            return await ctx.send('You have successfully been unverified from the bot.')
        else:
            return await ctx.send(f'You aren\'t verified yet.\nTo get information about verifying yourself, run `{escape(ctx.prefix)}help verify`')


def setup(bot):
    h = Verfiy(bot)
    bot.add_cog(h)
