import itertools

import discord
from discord.ext import commands


class Paginator:

    def __init__(self, max_size=2000):
        self.max_size = max_size
        self.clear()

    def new_embed(self):
        embed: discord.Embed = discord.Embed(description='', color=discord.Color.orange())
        embed.set_author(name="Hypixel Bot Help Manual",
                                   icon_url="https://cdn.discordapp.com/avatars/333422871567400961/afd25e730e0ac183091d14086fb9a130.png?size=4096")
        embed.set_footer(text=f"Type help <command> for more info on a command.")
        return embed

    def clear(self):
        self._current_page = self.new_embed()
        self._count = 0
        self.fields = 0
        self._pages = []

    def add_line(self, line='', *, empty=False):
        max_page_size = self.max_size - 2
        line += '\n'
        if len(line) > max_page_size:
            raise RuntimeError('Line exceeds maximum page size %s' % (max_page_size))

        if self._count + len(line) + 1 > self.max_size:
            self.close_page()

        self._count += len(line) + 1
        self._current_page.description += line

        if empty:
            self._current_page.description += ''
            self._count += 1

    def add_field(self, name, value):
        if self.fields >= 25:
            raise RuntimeError('Field count exceeds limit 25')
        self._current_page.add_field(name=name, value=value, inline=False)

    def close_page(self):
        self._pages.append(self._current_page)
        self._count = 0

    def __len__(self):
        total = sum(len(p) for p in self._pages)
        return total + self._count

    @property
    def pages(self):
        if self._current_page and self._pages.__len__() < 1:
            self.close_page()
        return self._pages

    def __repr__(self):
        fmt = '<Paginator prefix: {0.prefix} suffix: {0.suffix} max_size: {0.max_size} count: {0._count}>'
        return fmt.format(self)


class HelpCommand(commands.HelpCommand):

    def __init__(self, **options):
        self.width = options.pop('width', 80)
        self.indent = options.pop('indent', 2)
        self.sort_commands = options.pop('sort_commands', True)
        self.dm_help = options.pop('dm_help', False)
        self.dm_help_threshold = options.pop('dm_help_threshold', 1000)
        self.commands_heading = options.pop('commands_heading', "Commands:")
        self.no_category = options.pop('no_category', 'No Category')
        self.paginator = options.pop('paginator', None)

        if self.paginator is None:
            self.paginator = Paginator()

        super().__init__(**options)

    def shorten_text(self, text):
        if len(text) > self.width:
            return text[:self.width - 3] + '...'
        return text

    def get_ending_note(self):
        return

    def add_indented_commands(self, commands, *, heading, max_size=None):

        if not commands:
            return

        max_size = max_size or self.get_max_size(commands)

        get_width = discord.utils._string_width
        cmds = []
        for command in commands:
            name = command.name
            width = max_size - (get_width(name) - len(name))

            desc = f"- {command.short_doc}" if command.short_doc else ''
            entry = f'​{self.indent * " "}**{name:<{width}}** {desc}'
            cmds.append(self.shorten_text(entry))
        self.paginator.add_field(f"**__{heading}__**", '\n'.join(cmds))

    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            await destination.send(embed=page)

    def add_command_formatting(self, command):

        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        self.paginator.add_line(f"`Syntax: {signature}`", empty=True)


        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    def get_destination(self):
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        elif self.dm_help is None and len(self.paginator) > self.dm_help_threshold:
            return ctx.author
        else:
            return ctx.channel

    async def prepare_help_command(self, ctx, command):
        self.paginator.clear()
        await super().prepare_help_command(ctx, command)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        no_category = '\u200b{0.no_category}:'.format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name + ':' if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        max_size = self.get_max_size(filtered)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, commands in to_iterate:
            commands = sorted(commands, key=lambda c: c.name) if self.sort_commands else list(commands)
            self.add_indented_commands(commands, heading=category, max_size=max_size)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages()

    async def send_group_help(self, group):
        self.add_command_formatting(group)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=self.commands_heading)

        if filtered:
            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

        await self.send_pages()

    async def send_cog_help(self, cog):
        if cog.description:
            self.paginator.add_line(cog.description, empty=True)

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=self.commands_heading)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()

    async def command_callback(self, ctx, *, command=None):
        await self.prepare_help_command(ctx, command)
        bot = ctx.bot

        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        # Check if it's a cog
        cog = bot.get_cog(command)
        if cog is not None:
            return await self.send_cog_help(cog)

        maybe_coro = discord.utils.maybe_coroutine

        keys = command.split(' ')
        cmd = bot.all_commands.get(keys[0])
        if cmd is None:
            return

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                print(string)
                return await self.send_error_message(string)
            else:
                if found is None:
                    string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))
                    return await self.send_error_message(string)
                cmd = found

        if isinstance(cmd, commands.Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand(indent=5)
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(CustomHelp(bot))
