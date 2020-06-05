from cogs.utils.dbl.client import DBLClient
import discord
from discord.ext import commands, tasks

import asyncio
import logging

log = logging.getLogger(__name__)

class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjMzMzQyMjg3MTU2NzQwMDk2MSIsImJvdCI6dHJ1ZSwiaWF0IjoxNTE1MjU1NDA5fQ.GgX0N7VBKvOeyztnAIbhvXA29p5akVpzYLrx1yDmq_g' # set this to your DBL token
        self.dblpy = DBLClient(self.bot, self.token, webhook_path='/dblwebhook',
                                   webhook_auth='#ziySC35V1fU!##85F&HcFhbz!KVBpjZ2I!OGngCSSSr7rrFr2%eg2',
                                   webhook_port=8080)

    # The decorator below will work only on discord.py 1.1.0+
    # In case your discord.py version is below that, you can use self.bot.loop.create_task(self.update_stats())

    @tasks.loop(minutes=5.0)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""
        logging.info('Attempting to post server count')
        try:
            await self.dblpy.post_guild_count()
            logging.info('Posted server count ({})'.format(self.dblpy.guild_count()))
        except Exception as e:
            logging.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

        # if you are not using the tasks extension, put the line below

        await asyncio.sleep(1800)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        fetched = await self.bot.pool.fetchrow('select * from votes where userid=$1', int(data['user']))
        if fetched: await self.bot.pool.execute('update votes set count=$1, active=True, timestamp=current_timestamp where userid=$2', fetched['count']+1, int(data['user']))
        else: await self.bot.pool.execute('insert into votes(userid, count, active, timestamp) values($1, 0, True, current_timestamp)', int(data['user']))
        user: discord.User = await self.bot.fetch_user(int(data['user']))
        await user.send('Your vote from top.gg has been successfully delivered. <3')
        logging.info('Received an upvote')
        logging.info(data)

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        logging.info('Received a test')
        logging.info(data)

def setup(bot):
    bot.add_cog(TopGG(bot))