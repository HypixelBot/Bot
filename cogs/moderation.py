from collections import Counter, defaultdict
from discord.ext import commands
from .utils import checks, time
from cogs.utils.misc import *
import argparse, shlex
import traceback
import logging
import discord
import re

log = logging.getLogger(__name__)

class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)

class Prefix(commands.Converter):
    async def convert(self, ctx, argument):
        user_id = ctx.bot.user.id
        if argument.startswith((f'<@{user_id}>', f'<@!{user_id}>')):
            raise commands.BadArgument('That is a reserved prefix already in use.')
        return argument

## The actual cog

class Mod(commands.Cog):
    """Moderation related commands."""

    def __init__(self, bot):
        self.bot = bot

        # guild_id: set(user_id)
        self._recently_kicked = defaultdict(set)

    def __repr__(self):
        return '<cogs.Mod>'

    async def cog_before_invoke(self, ctx):
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages:
            return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')

    @commands.command(aliases=['newmembers'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def newusers(self, ctx, *, count=5):
        """Tells you the newest members of the server.

        This is useful to check if any suspicious members have
        joined.

        The count parameter can only be up to 25.
        """
        count = max(min(count, 25), 5)

        if not ctx.guild.chunked:
            await self.bot.request_offline_members(ctx.guild)

        members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[:count]

        e = discord.Embed(title='New Members', colour=discord.Colour.green())

        for member in members:
            body = f'joined {time.human_timedelta(member.joined_at)}\ncreated {time.human_timedelta(member.created_at)}'
            e.add_field(name=f'{member} (ID: {member.id})', value=body, inline=False)

        await ctx.send(embed=e)

    @commands.group(aliases=['purge'], case_insensitive=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def remove(self, ctx):
        """Removes messages that meet a criteria.

        In order to use this command, you must have Manage Messages permissions.
        Note that the bot needs Manage Messages as well. These commands cannot
        be used in a private message.

        When the command is done doing its work, you will get a message
        detailing which users got removed and how many messages got removed.
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            await ctx.send(f'Successfully removed {deleted} messages.')
        else:
            await ctx.send(to_send, delete_after=10)

    @remove.command()
    async def mentions(self, ctx, search=100):
        """Removes messages that only have mentions in them."""
        pattern = re.compile("<@([0-9]+)>")
        await self.do_removal(ctx, search, lambda e: e.mentions and pattern.match(e.content).group() == e.content)

    @remove.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @remove.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @remove.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @remove.command(name='all')
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @remove.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @remove.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.

        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @remove.command(name='bot')
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return m.author.bot or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @remove.command(name='emoji')
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<:(\w+):(\d+)>')
        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @remove.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f'Successfully removed {total_reactions} reactions.')

    @remove.command()
    async def custom(self, ctx, *, args: str):
        """A more advanced purge command.

        This command uses a powerful "command line" syntax.
        Most options support multiple values to indicate 'any' match.
        If the value has spaces it must be quoted.

        The messages are only deleted if all options are met unless
        the `--or` flag is passed, in which case only if any is met.

        The following options are valid.

        `--user`: A mention or name of the user to remove.
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.

        Flag options (no arguments):

        `--bot`: Check if it's a bot user.
        `--embeds`: Check if the message has embeds.
        `--files`: Check if the message has attachments.
        `--emoji`: Check if the message has custom emoji.
        `--reactions`: Check if the message has reactions
        `--or`: Use logical OR for all options.
        `--not`: Use logical NOT for all options.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--reactions', action='store_const', const=lambda m: len(m.reactions))
        parser.add_argument('--search', type=int, default=100)
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any
        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        args.search = max(0, min(2000, args.search)) # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)

    @commands.group(name = 'prefix', invoke_without_command = True, case_insensitive=True)
    @commands.guild_only()
    async def prefix(self, ctx):
        """Manages the server's custom prefixes.
		If called without a subcommand, this will list the currently set
		prefixes.
		"""

        data = await self.bot.pool.fetchrow("SELECT prefix FROM prefixes WHERE guildid=$1;", ctx.guild.id)
        if not data:
            data = {'prefix': self.bot.default_prefix}

        e = discord.Embed(color=discord.Colour.dark_blue())
        e.set_author(name=f"{ctx.guild.name}'s Prefixes")
        e.set_thumbnail(url=ctx.guild.icon_url)
        e.add_field(name="Default Prefix:", value=f"`{self.bot.default_prefix}`")
        e.add_field(name="Server Prefix:", value=f"`{data['prefix']}`")
        await ctx.send(embed=e)

    @prefix.command()
    @checks.is_mod()
    async def set(self, ctx, prefix: Prefix):
        """Sets custom prefix.
		Previously set prefixes are overridden.
		To have a word prefix, you should quote it and end it with
		a space, e.g. "hello " to set the prefix to "hello ". This
		is because Discord removes spaces when sending messages so
		the spaces are not preserved.
		Multi-word prefixes must be quoted also.
		You must have Manage Server permission to use this command.
		"""

        if len(prefix) > 5: return await ctx.send('The prefix lenght can\'t be higher than 5!')
        if prefix == ctx.prefix: return await ctx.send("The prefix you tried to set is already the current prefix!")

        await self.bot.pool.execute(f"""WITH upsert AS (UPDATE prefixes SET prefix=$1 WHERE guildid=$2 RETURNING *)
                                    INSERT INTO prefixes (prefix, guildid) SELECT $1, $2 WHERE NOT EXISTS (SELECT * FROM upsert)""", prefix, ctx.guild.id)
        await ctx.send(f"Prefix updated to **{prefix}**")

    @prefix.command()
    @checks.is_mod()
    async def reset(self, ctx):
        """Resets the custom prefix.
		This is the inverse of the 'prefix add' command. You can
		use this to remove prefixes from the default set as well.
		You must have Manage Server permission to use this command.
		"""

        await self.bot.pool.execute(f"delete from prefixes where guildid=$1", ctx.guild.id)

        await ctx.send(f"The prefix has been reset to **{self.bot.default_prefix}**")

def setup(bot):
    bot.add_cog(Mod(bot))
