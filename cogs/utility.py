from collections import Counter
from cogs.utils.paginator import Pages
from cogs.utils.checks import *
from datetime import datetime
import logging
import discord
import time

log = logging.getLogger(__name__)

class Utility(commands.Cog):
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        await ctx.trigger_typing()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages:
            return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')

    @staticmethod
    def format_delta(delta):
        return round(delta * 1000)

    @staticmethod
    async def timeit(coro):
        """Times a coroutine."""
        before = time.monotonic()
        coro_result = await coro
        after = time.monotonic()
        return after - before, coro_result

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.guild_only()
    async def info(self, ctx, user:discord.User = None):
        """Shows info about a discord member."""
        if not user: user = ctx.author
        if user in ctx.guild.members:
            guild_shared = True
            user = ctx.guild.get_member(user.id)
        else: guild_shared = False

        e = discord.Embed()
        #e.colour = 0xea7938
        e.set_author(name=str(user))
        roles = [role.name.replace('@', '@\u200b') for role in user.roles] if guild_shared else None
        # shared = sum(1 for m in self.bot.get_all_members() if m.id == user.id)
        if str(user.avatar_url)[54:].startswith('a_'): avi=f'https://images.discordapp.net/avatars/{str(user.avatar_url)[35:-10]}'
        else: avi = user.avatar_url
        voice = user.voice if guild_shared else None
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
        else: voice = 'Not connected.'

        guild = ctx.guild
        game = [None if 'activity' not in dir(user) else user.activity, 'Game']
        if not game[0]: game[0] = 'None'
        elif game[0].type is discord.ActivityType.playing:
            game[1] = 'Streaming'
            game[0] = f'[{game[0].name}]({game[0].url})'
        elif game[0].type is discord.ActivityType.listening and "title" in dir(game[0]):
            game[1] = 'Listening to'
            game[0] = f'[{game[0].title}](https://open.spotify.com/track/{game[0].track_id}) from '+', '.join(game[0].artists)
        elif game[0].type is discord.ActivityType.watching:
            game[1] = 'Watching'
            game[0] = game[0].name
        elif game[0].type == 4:
            game[1] = "Custom Status"
            game[0] = game[0].state
        elif user.activity.type.value == 0: game[0] = user.activity.name

        e.add_field(name='ID', value=user.id)
        if guild_shared: e.add_field(name='Nick', value=user.nick)
        if guild_shared: e.add_field(name='Status', value=user.status)
        if guild_shared: e.add_field(name='Voice', value=voice)
        if guild_shared: e.add_field(name = game[1], value = game[0], inline = False)
        # e.add_field(name='Servers', value=f'{shared} shared')
        e.add_field(name = 'Account Created', value = f"{user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S')} [{(datetime.now() - datetime.fromtimestamp(user.created_at.timestamp())).days}]", inline=False)
        if guild_shared: e.add_field(name='Join Date', value= f"{user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S')} [{(datetime.now() - datetime.fromtimestamp(user.joined_at.timestamp())).days}]", inline=False)
        try:
            sorted_users = [m for m in sorted(guild.members, key=lambda m: m.joined_at.timestamp())]
            user_index = sorted_users.index(user)
            users_order = ''
            if user_index != 0:
                users_order += f'{sorted_users[user_index-1].name} > '
            users_order += f'**{sorted_users[user_index].name}**'
            if len(sorted_users) >= user_index + 1:
                users_order += f' > {sorted_users[user_index+1].name}'
            if len(sorted_users) >= user_index + 2:
                users_order += f' > {sorted_users[user_index+2].name}'
            if len(sorted_users) >= user_index + 3:
                users_order += f' > {sorted_users[user_index+3].name}'
            if guild_shared: e.add_field(name=f'Join Order [{user_index+1}]', value=users_order, inline=False)
        except: pass
        if guild_shared: e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
        e.set_thumbnail(url = avi)

        if user.avatar:
            e.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=e)

    @info.command()
    @commands.guild_only()
    async def avi(self, ctx, user:discord.Member = None):
        """Shows the pfp of a discord member."""
        if not user: user = ctx.author

        if user.avatar_url[54:].startswith('a_'): avi=f'https://images.discordapp.net/avatars/{user.avatar_url[35:-10]}'
        else: avi = user.avatar_url

        embed = discord.Embed()
        embed.set_image(url=avi)
        await ctx.send(embed=embed)

    @info.command(name='server', aliases=['guild'])
    @commands.guild_only()
    async def server_info(self, ctx):
        """Shows info about the current server."""
        guild = ctx.guild
        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        # we're going to duck type our way here
        class Secret:
            pass

        secret_member = Secret()
        secret_member.id = 0
        secret_member.roles = [guild.default_role]

        # figure out what channels are 'secret'
        secret_channels = 0
        secret_voice = 0
        text_channels = 0
        for channel in guild.channels:
            perms = channel.permissions_for(secret_member)
            is_text = isinstance(channel, discord.TextChannel)
            text_channels += is_text
            if is_text and not perms.read_messages:
                secret_channels += 1
            elif not is_text and (not perms.connect or not perms.speak):
                secret_voice += 1

        regular_channels = len(guild.channels) - secret_channels
        voice_channels = len(guild.channels) - text_channels
        member_by_status = Counter(str(m.status) for m in guild.members)

        e = discord.Embed()
        e.title = 'Info for ' + guild.name
        e.add_field(name='ID', value=guild.id)
        e.add_field(name='Owner', value=guild.owner)
        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        if guild.splash:
            e.set_image(url=guild.splash_url)

        info = [ctx.tick(len(guild.features) >= 3, 'Partnered')]

        sfw = guild.explicit_content_filter is not discord.ContentFilter.disabled
        info.append(ctx.tick(sfw, 'Scanning Images'))
        info.append(ctx.tick(guild.member_count > 100, 'Large'))
        e.add_field(name='Info', value='\n'.join(map(str, info)))

        fmt = f'Text {text_channels} ({secret_channels} secret)\nVoice {voice_channels} ({secret_voice} locked)'
        e.add_field(name='Channels', value=fmt)

        fmt = f'<:online:313956277808005120> {member_by_status["online"]}\n' \
              f'<:away:313956277220802560> {member_by_status["idle"]}\n' \
              f'<:dnd:313956276893646850> {member_by_status["dnd"]}\n' \
              f'<:offline:313956277237710868> {member_by_status["offline"]}\n' \
              f'Total: {guild.member_count}'

        e.add_field(name='Members', value=fmt)
        e.add_field(name='Created At', value="{} [{}]".format(guild.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), (datetime.now() - datetime.fromtimestamp(guild.created_at.timestamp())).days), inline=False)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
        await ctx.send(embed=e)

    @commands.command(name = 'ping', hidden=True)
    @commands.guild_only()
    async def _ping(self, ctx):
        """Get response time."""
        before = time.monotonic()
        typing_delay = self.format_delta((await self.timeit(ctx.trigger_typing()))[0])
        message_delay, message = await self.timeit(ctx.send('..'))
        message_delay = self.format_delta(message_delay)
        edit_delay = self.format_delta((await self.timeit(message.edit(content='...')))[0])
        gateway_delay = self.format_delta((datetime.utcnow() - ctx.message.created_at).total_seconds())
        after = time.monotonic()
        total_delay = self.format_delta(after - before)
        await message.edit(content='Pong.\n\n**Stats for nerds**:\nTyping delay: `{}ms`\nMessage send delay: `{}ms`\n'
                                   'Message edit delay: `{}ms`\nGateway delay: `{}ms`\nTotal: `{}ms`'
                           .format(typing_delay, message_delay, edit_delay, gateway_delay, total_delay))

    @commands.command('colors', aliases=['colours'])
    async def color(self, ctx):
        em = discord.Embed(title='Minecraft color codes', color=discord.Color.orange())
        em.add_field(name='Color Codes', value="<:darkred:513110394068271104> - Dark Red &4\n<:red:513110394072596491> - Red &c\n<:gold:513110394039173130> - Gold &6\n<:yellow:513110393774800909> - Yellow &e\n<:darkgreen:513110393611223042> - Dark Green &2\n<:green:513110394017939457> - Green &a\n<:aqua:513110393934053392> - Aqua &b\n<:darkaqua:513110393925664773> - Dark Aqua &3")
        em.add_field(name='​', value='<:darkblue:513110394026459146> - Dark Blue &1\n<:blue:513110393988710400> - Blue &9\n<:lightpurple:513110393653035009> - Light Purple &d\n<:purple:513110394047430666> - Dark Purple &5\n<:white:513110393670074369> - White &f\n<:gray:513110394240499722> - Grey &7\n<:darkgray:513110394794147858> - Dark Grey &8\n<:black:513110393653035040> - Black &0')
        em.add_field(name='​', value='<:strike:513118587011989516> - Strike Through &m\n'
                                     '<:underline:513118588555624449> - Underline &n\n'
                                     '<:bold:513118587074904064> - Bold &l\n'
                                     '<:italic:513118587268104211> - Italic &o\n'
                                     '<:magic:513118587133886491> - Obfuscated &k')
        await ctx.send(embed=em)

    # @commands.command()
    # async def charinfo(self, ctx, *, characters: str):
    #     """Shows you information about a number of characters.
    #    Only up to 25 characters at a time.
    #    """
    #
    #     if len(characters) > 25:
    #         return await ctx.send(f'Too many characters ({len(characters)}/25)')
    #
    #     def to_string(c):
    #         digit = f'{ord(c):x}'
    #         name = unicodedata.name(c, 'Name not found.')
    #         return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'
    #
    #     await ctx.send('\n'.join(map(to_string, characters)))
    #
    # @commands.command(name='ud')
    # async def urban(self, ctx, *, search_terms):
    #     """Urban Dictionary search
    #
    #     Definition number must be between 1 and 10"""
    #
    #     def encode(s):
    #         return quote_plus(s, encoding='utf-8', errors='replace')
    #
    #     search_terms = search_terms.split(" ")
    #     try:
    #         if len(search_terms) > 1:
    #             pos = int(search_terms[-1]) - 1
    #             search_terms = search_terms[:-1]
    #         else:
    #             pos = 0
    #         if pos not in range(0, 11):  # API only provides the
    #             pos = 0  # top 10 definitions
    #     except ValueError:
    #         pos = 0
    #
    #     search_terms = "+".join([encode(s) for s in search_terms])
    #     url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
    #     try:
    #         async with self.bot.session.get(url) as r:
    #             result = await r.json()
    #         if result["list"]:
    #             defs = len(result['list'])
    #             result = result['list'][pos]
    #             definition = result['definition'] if 'definition' in result else 'Non'
    #             example = result['example'] if "example" in result and len(result['example']) > 0 else "Non"
    #             em = discord.Embed(color = ctx.author.color if type(ctx.channel) is discord.channel.TextChannel else discord.Color.orange())
    #             em.set_thumbnail(url='https://i.imgur.com/DAFxw8a.png')
    #             em.add_field(name=f'Definition of {result["word"] if "word" in result else "Non"}', value=definition, inline=False)
    #             em.add_field(name='Example', value=example, inline=False)
    #             em.add_field(name='Author', value=result["author"] if "author" in result else "Non")
    #             em.add_field(name='Ratings', value=f'👍`{result["thumbs_up"] if "thumbs_up" in result else "0"}` 👎`{result["thumbs_down"] if "thumbs_down" in result else "0"}`')
    #             em.set_footer(text=f'Definition #{pos+1} out of #{defs}')
    #             await ctx.send(embed = em)
    #         else:
    #             pass
    #     except IndexError:
    #         await ctx.send("There is no definition #{}".format(pos + 1))
    #
    # @commands.command(name='weather', hidden=True)
    # @commands.is_owner()
    # async def _weather(self, ctx, *, location: str):
    #     _location = self.weather.lookup_by_location(location)
    #     condition = _location.condition()
    #     km = 0.621371192
    #     em = discord.Embed(title = _location.description().replace('Yahoo! ', ''), description = condition.text())
    #     em.set_thumbnail(url = f"http://l.yimg.com/a/i/us/we/52/{_location.condition().code()}.gif")
    #     em.add_field(name = 'Country', value = f':flag_{_location.title().split(",")[-1].replace(" ", "").lower()}:')
    #     em.add_field(name = 'Temperature', value = f'{float(_location.condition().temp()):1.1f}°C | {float(celsius_to_fahrenheit(int(_location.condition().temp()))):1.1f}°F')
    #     em.add_field(name = 'Latitude', value = _location.latitude())
    #     em.add_field(name = 'Longitude', value = _location.longitude())
    #     em.add_field(name = 'Wind Speed', value = f'{float(_location.wind()["speed"]):1.1f} Km/h | {float(_location.wind()["speed"])*km:1.1f} Mph')
    #     em.add_field(name = 'Humidity', value = f'{_location.atmosphere()["humidity"]}%')
    #     await ctx.send(embed = em)
    #
    # @commands.command()
    # async def staff(self, ctx):
    # 	"""Shows the all the staff members."""
    # 	owner = ctx.guild.owner
    # 	members = {'owner': f'{owner.nick if owner.nick else owner.name}#{owner.discriminator}'.replace('`', '\`'),
    # 			   'admin': [], 'staff': []}
    # 	for role in ctx.guild.roles:
    # 		if role.permissions.administrator:
    # 			for member in role.members:
    # 				user = f'{member.nick if member.nick else member.name}#{member.discriminator}'.replace('`', '\`')
    # 				if not(member.bot or user in members['admin'] or user in members['owner']): members['admin'].append(user)
    # 				if user in members['staff']: members['staff'].pop(members['staff'].index(user))
    #
    # 		if role.permissions.manage_guild or role.permissions.kick_members or role.permissions.ban_members or role.permissions.manage_nicknames or role.permissions.manage_channels or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.manage_emojis:
    # 			for member in role.members:
    # 				user = f'{member.nick if member.nick else member.name}#{member.discriminator}'.replace('`', '\`')
    # 				if not(member.bot or user in members['admin'] or user in members['staff'] or user in members['owner']): members['staff'].append(user)
    #
    # 	em = discord.Embed()
    # 	#if ctx.guild.icon: em.set_thumbnail(url=ctx.guild.icon_url)
    # 	em.add_field(name='Owner', value='`'+members['owner']+'`', inline=False)
    # 	if members['admin']: em.add_field(name='Admin' if len(members['admin']) == 1 else f'Admins [{len(members["admin"])}]', value='`'+', '.join(members['admin'])+'`', inline=False)
    # 	if members['staff']: em.add_field(name='Staff' if len(members['staff']) == 1 else f'Staff [{len(members["staff"])}]', value='`'+', '.join(members['staff'])+'`', inline=False)
    # 	await ctx.send(embed=em)
    #
    # @commands.command()
    # async def staff(self, ctx, guild=None):
    # 	"""Shows the all the staff members."""
    # 	if guild: guild = self.bot.get_guild(int(guild))
    # 	else: guild = ctx.guild
    # 	owner = guild.owner
    # 	roles = find_all(lambda r: not r.managed and (r.permissions.administrator or r.permissions.manage_guild or r.permissions.kick_members or r.permissions.ban_members or r.permissions.manage_nicknames or r.permissions.manage_channels or r.permissions.manage_messages or r.permissions.manage_roles or r.permissions.manage_webhooks or r.permissions.manage_emojis), guild.roles)
    # 	users = []
    # 	em = discord.Embed(title=f'Guild Owner: {owner}')
    # 	for r in sorted(roles, key=lambda r: r.position, reverse=True):
    # 		rusers = '`'+', '.join([f'{u.nick if u.nick else u.name}#{u.discriminator}'.replace('`', '\`') for u in r.members if not u.bot and u.id not in users])+'`'
    # 		for u in r.members: users.append(u.id)
    # 		if rusers != '``': em.add_field(name=r.name, value=rusers, inline=False)
    # 	await ctx.send(embed=em)
    #
    # @commands.command(name='role')
    # async def _role(self, ctx, *, role: str):
    # 	vmembers = False
    # 	if len(role.split()) > 1 and role.split()[-1] == 'members':
    # 		if not discord.utils.find(lambda r: r.name == role, ctx.guild.roles):
    # 			role = ' '.join(role.split()[:-1])
    # 			vmembers = True
    # 	r = discord.utils.find(lambda r: r.name == role, ctx.guild.roles)
    # 	if not r: return await ctx.send(f'Role "{role}" not found.')
    # 	em = discord.Embed(color=r.colour if r.colour else None)
    # 	em.set_thumbnail(url='https://i.imgur.com/BadXVNx.png')
    # 	if vmembers:
    # 		if len(r.members) > 50: return await ctx.send('There are too many members with that role.')
    # 		em.title = r.name
    # 		msg = ''
    # 		part = 0
    # 		for m in sorted(r.members, key=lambda m: m.joined_at):
    # 			user = '`'+f'{m.nick if m.nick else m.name}#{m.discriminator}'+'`'
    # 			if len(msg + f'{user}, ') >= 1024:
    # 				em.add_field(name='​', value=msg[:-3]+'`', inline=False)
    # 				msg = ''
    # 				part+=1
    # 			else:
    # 				msg+=f'`{user}`, '
    # 		em.add_field(name='​', value=msg[:-3]+'`' if len(r.members) > 1 else 'None', inline=False)
    # 	else:
    # 		member_by_status = Counter(str(m.status) for m in r.members)
    # 		em.title = 'Name'
    # 		em.description=f'{r.name}\n​'
    # 		em.add_field(name='Members', value=f'{len(r.members)} ({len(r.members)-member_by_status["offline"]} online)')
    # 		em.add_field(name='Position', value= f'{len(ctx.guild.roles) - r.position} (Out of {len(ctx.guild.roles)})')
    # 		em.add_field(name='Color', value=f'Hex: {r.color}\nRGB: {r.color.to_rgb()}')
    # 		em.add_field(name='Hoisted', value=str(r.hoist))
    # 		em.add_field(name='Managed', value=str(r.managed))
    # 		em.add_field(name='Mentionable', value=str(r.mentionable))
    # 		em.add_field(name='Created On', value=f"{r.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S')} [{(datetime.now() - datetime.fromtimestamp(r.created_at.timestamp())).days}]", inline=False)
    # 	await ctx.send(embed=em)
    #
    # @commands.command(name='announcement')
    # async def announce(self, ctx):
    #     """Important announcement"""
    #     channel = ctx.author.dm_channel
    #     if not channel:
    #         await ctx.author.create_dm()
    #         channel = ctx.author.dm_channel
    #     messages = [m.content for m in await channel.history(reverse=True, limit=5).flatten()]
    #     if any("Hello. This is an important message from the bot developer" in m for m in messages): return await ctx.send('You\'ve already received the announcement!')
    #     await ctx.author.send(f'Hello. This is an important message from the bot developer, Ice#5518, regarding the current state of the bot.\n'
    #                           f'A lot of people that uses this bot daily has probably noticed that from time to time the bot gets really slow, that\'s due to the fact that the bot is growing faster than expected. '
    #                           f'The bot is currently in {len(self.bot.guilds)} server and taking up to 500MB of ram and the host doesn\'t allow ram usage to be above 500.\n'
    #                           f'The bot is being ran in a host for free, that\'s why the ram usage is so limited, and I can\'t afford a paid/better host all by myself and this is where you come in. '
    #                           f'I\'ve set up a patreon where you can support me and hopefully get the bot a better host. <https://www.patreon.com/Wonderpants>\n'
    #                           f'If it isn\'t possible to give the bot a better hosting service it\'ll most likely either shut down or become private.\n'
    #                           f'Thank you for the support and using my bot. It means a lot to me.')
    #     await ctx.send(f'📫 | {ctx.author.mention}, a message has been sent to you.')
    #     logging.info(f'{ctx.author} user announcements command!')

    async def _complex_cleanup_strategy(self, ctx, search):
        prefixes = tuple(await self.bot._prefix(self.bot, ctx)) # thanks startswith

        def check(m):
            return m.author == ctx.me or m.content.startswith(prefixes)
        try:
            deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        except discord.Forbidden as e:
            return await ctx.send('I do not have permissions to delete messages.')
        return Counter(m.author.display_name for m in deleted)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel.

        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.

        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.

        You must have Manage Messages permission to use this.
        """
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.manage_messages: return await ctx.author.send(f'I don\'t have permissions to manage messages in this channel!')
        strategy = self._complex_cleanup_strategy

        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key = lambda t: t[1], reverse = True)
            messages.extend(f'- **{author}**: {count}' for author, count in spammers)

        await ctx.send('\n'.join(messages), delete_after = 10)

    @commands.command()
    @commands.guild_only()
    @is_staff()
    async def listroles(self, ctx):
        """Useful command to find every role and their ID's"""
        guild = ctx.guild
        roles = list(guild.roles)[:]
        roles.sort(key = lambda role: -role.position)

        p = Pages(ctx, entries=[f"{r.name}, {r.id}" for r in roles], per_page=25, show_index_count=False)
        await p.paginate()

    @commands.command()
    @commands.guild_only()
    async def role(self, ctx, *, role: discord.Role):
        """Shows info about a role. Can use name, id or mention"""
        users = Counter([str(u.status) for u in role.members])
        em = discord.Embed(color=role.color)
        em.set_author(name=role.name)
        em.add_field(name='Members', value=f"{len(role.members)}{'' if 'online' not in users else ' ('+str(users['online'])+' online)'}")
        em.add_field(name='Position', value=f"{len(ctx.guild.roles)-role.position}/{len(ctx.guild.roles)}")
        em.add_field(name='Color', value=f'Hex: #{int(round(role.color.r)):02x}{int(round(role.color.g)):02x}{int(round(role.color.b)):02x}\n'
                                         f'RGB: ({role.color.r}, {role.color.g}, {role.color.b})')
        em.add_field(name='Hoisted', value=role.hoist)
        em.add_field(name='Managed', value=role.managed)
        em.add_field(name='Mentionable', value=role.mentionable)
        em.add_field(name='Permissions', value=', '.join([x[0].replace('_', ' ').title() for x in role.permissions if x[1]]))
        em.set_footer(text=f"ID: {role.id}")
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Utility(bot))
