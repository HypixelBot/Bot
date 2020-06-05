from cogs.utils import hypixel # Do Not Remove
from cogs.utils.dataIO import dataIO
from cogs.utils.db import Table
from cogs.utils.checks import *
from cogs.utils import context
import contextlib
import traceback
import datetime
import asyncio
import aiohttp
import logging
import discord
import sys, os
import click

try:
    from cogs.utils import hypixel
    hypixel.setKeys(load_config()["hypixel"])
    hypixel_status = True
except hypixel.HypixelAPIError as error:
    logging.error('\n'.join(traceback.format_exception(type(error), error, error.__traceback__)))
    hypixel_status = False

@contextlib.contextmanager
def setup_logging():
    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = logging.FileHandler(filename=f'Log{str(datetime.datetime.now().date())}.txt', encoding='utf-8', mode='w')
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(fmt)
        log.addHandler(consoleHandler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)

try: import uvloop
except ImportError: pass
else: asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class HypixelBot(commands.AutoShardedBot):

    def __init__(self):
        # super().__init__(command_prefix=self._prefix, help_attrs=dict(hidden=True), fetch_offline_members=False, case_insensitive=True, shard_ids=[i for i in range(sys.argv[-2], sys.argv[-1])], shard_count=20)
        super().__init__(command_prefix='-', help_attrs=dict(hidden=True), fetch_offline_members=False, case_insensitive=True)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.platform = __import__('platform').system()
        if not hasattr(self, 'uptime'): self.uptime = datetime.datetime.now()
        self.patron = None
        self.hypixel = hypixel
        self.hypixel_status = hypixel_status
        self.ready = False

        self.headers = {}
        self.command_count = {}
        self.blacklisted = []
        self.ignored = self.Ignored()
        self.rankCache = {}
        self.ignore = {}
        self.footer = f'Hypixel Bot | Made with ❤ by Ice#5555 '
        self.owner_id = 98141664303927296
        self.default_prefix = 'h!'# if self.platform != 'Windows' else '!!'
        self.webhooks = {
            'direct-messages': 'https://discordapp.com/api/webhooks/497511134681890818/exje5nggrG1mt25U34KmsmgxyupviqeU4kUDP8GID5Y0EjE352LoOPD-D3sPYdXkvzPS',
            'guilds-joined2': 'https://discordapp.com/api/webhooks/511198557261398017/Bgc6_owKoCapDZ-4cYVczQQJ-kaw-34bLIfyuxE7l_0iIGtUDhpS6mZgA3izbfoy70BF',
            'hypixelbot': 'https://discordapp.com/api/webhooks/393047983803072513/R9AoHL567m5vJLiDDgY91SFewU1_qBLhXhTMnnON4q3C7Aqw1a4RBNtO3NBdFszx1fpO',
            'suggestions': 'https://discordapp.com/api/webhooks/497510690987180072/6KauPwfJwi1SHkohN6tjjof-VooqFKAENYISARwDOIWbzPLsrhUt98T3nSSrWl4UNSyH',
            'welcome-goodbye': 'https://discordapp.com/api/webhooks/497511249215750154/si6iaPXI1Me1fDTi-t0ilDzrqKDjPEzs7fRj84_3xIiQP-P1OgNzPkqHVN2par94YPh8'
        }

        for extension in os.listdir("cogs"):
            if extension.endswith('.py'):
                if int(sys.argv[-2]) > 0 and extension[:-3] == "discordbots": continue
                try: self.load_extension("cogs." + extension[:-3])
                except Exception as e:
                    logging.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
                    logging.error(f'Failed to load extension {extension}\n{type(e).__name__}: {e}')
        for extension in os.listdir("hypixel"):
            if extension.endswith('.py'):
                try: self.load_extension("hypixel." + extension[:-3])
                except Exception as e:
                    logging.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
                    logging.error(f'Failed to load extension {extension}\n{type(e).__name__}: {e}')

    async def hastebin(self, content):
        async with self.session.post("https://hastebin.com/documents", data=content.encode('utf-8')) as resp:
            if resp.status == 200:
                result = await resp.json()
                return "https://hastebin.com/" + result["key"]
            else:
                return "Error with creating Hastebin. Status: %s" % resp.status

    class settings:
        @staticmethod
        async def hypixelRoles():
            guilds = await pool.fetch("select guildid from settings.hypixelroles;")
            return [x['guildid'] for x in guilds]

    class Ignored:
        def __init__(self):
            self.list = {}
        async def load(self):
            data = await pool.fetch("select * from settings.ignore;")
            for k, v in data:
                if k not in self.list:
                    self.list[k] = [v[1] for v in data if v[0] == k]

    async def _prefix(self, bot, ctx):
        await self.wait_until_ready()
        user_id = bot.user.id
        base = [f'<@!{user_id}> ', f'<@{user_id}> ', self.default_prefix]
        # if self.platform == 'Windows': return base
        if ctx.guild:
            prefix = await pool.fetchrow("select prefix from prefixes where guildid=$1;", ctx.guild.id)
            if prefix: base.extend(prefix)
        return base

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name="h!help | @hypixel", type=discord.ActivityType.watching))
        self.ready = True
        logging.info(f'Ready: {self.user} (ID: {self.user.id})')
        self.blacklisted = [row['userid'] for row in await pool.fetch("select * from blacklist;")]
        await self.ignored.load()
        try:
            data = dataIO.load_json('settings/restart.json')
            os.remove('settings/restart.json')
            channel = self.get_channel(data.channel)
            msg = await channel.fetch_message(data.message)
            for r in msg.reactions:
                if r.me: await msg.remove_reaction(r.emoji, channel.guild.me)
        except Exception: pass

    async def on_resumed(self):
        print('resumed...')

    async def on_command_error(self, ctx, error):
        trace = traceback.format_exception(type(error), error, error.__traceback__)
        if type(ctx.channel) is discord.channel.TextChannel: message = f'Guild: {ctx.guild.name} | {ctx.guild.id}\nChannel: {ctx.channel.name} | {ctx.channel.id}\nUsers: {ctx.author} | {ctx.author.id}\nCommand: {ctx.message.content}\n```{"".join(trace)}```'
        else: message = f'Users: {ctx.author} | {ctx.author.id}\nCommand: {ctx.message.content}\n```{"".join(trace)}```'

        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, discord.Forbidden): return await ctx.send('I do not have permission to execute this action.')
            elif isinstance(original, discord.NotFound): return await ctx.send(f'This entity does not exist: {original.text}')
            elif isinstance(original, discord.HTTPException):
                print(message)
                return await ctx.send('Somehow, an unexpected error occurred. Try again later?')
        elif isinstance(error, commands.errors.NoPrivateMessage): return await ctx.send('This command cannot be used in private messages.')
        if isinstance(error, commands.errors.MissingRequiredArgument): return await ctx.send_help(ctx.command)
        elif isinstance(error, commands.errors.BadArgument):
            if ctx.command.name == 'shared': return await ctx.send(f"\🔍 | **{ctx.author}**, the user could not be found.")
            return await ctx.send(error)
        elif isinstance(error, commands.errors.CheckFailure):
            if any(word in error.args[0] for word in ['session', 'guild', 'leaderboard']): return await ctx.send(f'In order to use `{ctx.command}` command you must upvote.\n<https://discordbots.org/bot/hypixel/vote>')
            return
        elif isinstance(error, commands.errors.CommandOnCooldown):
            if await self.is_owner(ctx.author): return await ctx.reinvoke()
            else: return await ctx.send(f'You can use this command again in {int(error.retry_after):.1f} seconds.')
        elif isinstance(error, discord.errors.NotFound): return
        elif isinstance(error, commands.errors.DisabledCommand): return
        elif isinstance(error, discord.errors.Forbidden): await ctx.send('I do not have permission to execute this action.')
        await ctx.send('Oops, something went wrong.')
        logging.error(message)
        # await self.get_user(self.owner_id).send(embed=discord.Embed(color=discord.Color.orange(), description=message if len(message)<1800 else await self.hastebin(message)))

    async def on_command_completion(self, ctx):
        if not ctx.command_failed:
            if str(ctx.command) not in self.command_count: self.command_count[str(ctx.command)] = 1
            else: self.command_count[str(ctx.command)] += 1
            await pool.execute(f"""do $$
                                begin insert into usage values('{ctx.command}',1);
                                exception when unique_violation then update usage set count = count+1 where cmd = '{ctx.command}';
                                end $$;""")

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls = context.Context)

        if ctx.command is None: return

        # Ignore
        if type(message.channel) != discord.DMChannel and message.guild.id in self.ignored.list and message.channel.id in self.ignored.list[message.guild.id]:
            if 'ignore' in message.content.lower() and message.author.guild_permissions.manage_guild: pass
            else: return print(f'Message ignored in {message.guild} - #{message.channel}')

        await self.invoke(ctx)

    async def on_message(self, message):
        await self.wait_until_ready()

        if message.author.bot: return # or type(message.channel) == discord.DMChannel: return
        if not self.ready: return

        # Prevent blacklisted users from using the bot.
        if message.author.id in self.blacklisted: return

        await self.process_commands(message)

    async def on_message_edit(self, before, after):
        await self.wait_until_ready()

        if type(after.channel) == discord.channel.DMChannel: return

        if after.author.bot: return # or type(message.channel) == discord.DMChannel: return
        if after.author.id not in [self.owner_id]: return

        await self.process_commands(after)

    async def close(self):
        with contextlib.redirect_stdout(None):
            await super().close()
            await self.session.close()
        print('Bot session closed!')

    def run(self):
        super().run(load_config()['token'], reconnect=True)

if __name__ == '__main__':
    with setup_logging():
        try:
            loop = asyncio.get_event_loop()
            try:
                pool = loop.run_until_complete(Table.create_pool(load_config()['database'], command_timeout=60))
                print('Database connected!')
            except Exception as error:
                logging.error(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
                click.echo('Could not set up PostgreSQL. Exiting.', file=sys.stderr); sys.exit(0)
            bot = HypixelBot()
            bot.pool = pool
            bot.run()
        except KeyboardInterrupt: sys.exit(0)
        except Exception as error: logging.error(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
