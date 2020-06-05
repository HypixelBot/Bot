from discord import AsyncWebhookAdapter
from discord import Webhook as WebHook
from cogs.utils.webhooks import *
from cogs.utils.checks import *
import logging
import discord
import asyncio

log = logging.getLogger(__name__)

class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reaction_emojis = ["✅", "❎"]
        self.messages = []
        self.rankColors = {'vip': 0x00FF00,
                           'vip+': 0x00FF00,
                           'mvp': 0x00FFFF,
                           'mvp+': 0x00FFFF,
                           'mvp++': 0xFFAA00,
                           'hypixel helper': 0x0000ff,
                           'hypixel moderator': 0x008000,
                           'hypixel admin': 0xff0000,
                           'member': 0x607d8b}

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author): return True
        return ctx.guild and (ctx.author.guild_permissions.manage_guild or ctx.guild.owner == ctx.author)

    async def cog_before_invoke(self, ctx):
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages:
            return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')

    @commands.command(hidden=True)
    @commands.guild_only()
    async def move(self, ctx, channel: discord.VoiceChannel, *, user: str = None):
        """Moves users from channel to channel.
            - move [channel] [user]
            - move [channel] [channel with users]
            - move [channel] [user1] [user2] ...
            ** **
            **Notice**: Remember to use their id and not name."""
        guild = ctx.guild
        if True in [(role.permissions.move_members or role.permissions.administrator) for role in await guild.fetch_member(self.bot.user.id).roles]:

            if not channel: return
            if not user: return await ctx.author.move_to(channel)

            if len(user.split()) == 1:
                member = await guild.fetch_member(int(user))
                if not member:
                    channel2 = self.bot.get_channel(int(user))
                    if channel2 and type(channel2) == discord.channel.VoiceChannel:
                        members = channel2.members
                        for member in members:
                            await member.move_to(channel)
                        return
                elif channel and type(channel) == discord.channel.VoiceChannel and member:
                    return await member.move_to(channel)

            if len(user.split()) > 1:
                members = user.split()
                for member in members:
                    member = await guild.fetch_member(int(member))
                    if channel and type(channel) == discord.channel.VoiceChannel:
                        await member.move_to(channel)
                return
        else: await ctx.send('Missing permissions to move members.')

    @commands.group(invoke_without_command = True, case_insensitive=True)
    @commands.guild_only()
    async def setup(self, ctx):
        """Easy way to setup custom features!
        To setup anything you must have permissions to manage the server!"""
        if ctx.invoked_subcommand is None: return await ctx.send_help(ctx.command)

    @setup.command(name='roles')
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setupRoles(self, ctx):
        """Set's up hypixel rank's based roles.
        This custom roles will be given to members that join according to their Hypixel Rank
        **If it's not possible to verify their minecraft username the role wont be given**"""
        cancel = None
        mrPerm = ctx.channel.permissions_for(ctx.me).manage_roles
        mmPerm = ctx.channel.permissions_for(ctx.me).manage_messages
        def check(m): return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        ranksdb = await self.bot.pool.fetchrow('select * from settings.hypixelroles where guildid=$1', ctx.guild.id)
        roles = {'member': None, 'vip': None, 'vip+': None, 'mvp': None, 'mvp+': None, 'mvp++': None, 'hypixel helper': None, 'hypixel moderator': None, 'hypixel admin': None}
        rolestr = ', '.join([k.upper() if len(k)<=5 else k.title() for k in roles])
        if ranksdb:
            start = await ctx.send('This server already has Hypixel rank\'s based roles.\nDo you want to delete them? [Y/N]')
            while True:
                try: response = await self.bot.wait_for('message', check=check, timeout=120)
                except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                if mmPerm: await response.delete()
                if 'y' in response.content.lower():
                    if cancel: await cancel.delete(); cancel = None
                    await self.bot.pool.execute('delete from settings.hypixelroles where guildid=$1', ctx.guild.id)
                    await start.edit(content='The custom roles have been deleted!\nDo you want to run the setup again? [Y/N]')
                    while True:
                        try: response = await self.bot.wait_for('message', check=check, timeout=120)
                        except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                        if mmPerm: await response.delete()
                        if 'y' in response.content.lower():
                            if cancel: await cancel.delete()
                            await start.delete(); return await ctx.reinvoke()
                        elif 'n' in response.content.lower():
                            if cancel: await cancel.delete()
                            return await start.delete()
                        else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')
                elif 'n' in response.content.lower():
                    if cancel: await cancel.delete();
                    ranksFound = {
                    }
                    for k, v in roles.items():
                        ranksFound[k] = discord.utils.find(lambda r: r.id == ranksdb[k], ctx.guild.roles)
                    text = '\n'.join([f"**{k.upper() if len(k)<=5 else k.title()}**: "+(f"<@&{v.id}>" if v else 'Empty') for k, v in ranksFound.items()])
                    return await start.edit(content=None, embed=discord.Embed(description=f'**The following ranks are being used**:\n\n{text}', color=discord.Color.orange()))
                else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')
        em = discord.Embed(title='Welcome to the Hypixel rank setup!',
                           description=f'**1**. Search already made roles.\n'
                                       f'**2**. Create new roles. ({rolestr}){" [**No Perms**]" if not mrPerm else ""}',
                           color=discord.Color.orange()).set_footer(text='Select the option you want.')
        start = await ctx.send(embed=em)
        while True:
            try: response = await self.bot.wait_for('message', check=check, timeout=120)
            except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
            if mmPerm: await response.delete()
            if response.content == '1':
                em = discord.Embed(description='<a:loading:393852367751086090> **Searching for roles!**', color=discord.Color.orange())
                await start.edit(content=None, embed=em)
                rolesFound = roles
                higher = 0
                for role in roles:
                    rolesFound[role] = discord.utils.find(lambda r: role in r.name.lower(), ctx.guild.roles)
                    if rolesFound[role] and rolesFound[role].position > ctx.me.top_role.position:
                        higher += 1
                em.description=f'**Found the following roles**:\n\n' + '\n'.join(f"**{k.title()}**: {rolesFound[k]}" for k in roles)
                em.set_footer(text='Do you want the roles to be this ones? [Y/N]')
                await start.edit(content=None, embed=em)
                while True:
                    try: response = await self.bot.wait_for('message', check=check, timeout=120)
                    except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                    if mmPerm: await response.delete()
                    if 'y' in response.content.lower():
                        if cancel: await cancel.delete()
                        for name, role in rolesFound.items():
                            if role: rolesFound[name] = role.id
                        await self.bot.pool.execute("insert into settings.hypixelroles values($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
                                                    ctx.guild.id, rolesFound['vip'], rolesFound['vip+'], rolesFound['mvp'], rolesFound['mvp+'], rolesFound['mvp++'], rolesFound['hypixel helper'], rolesFound['hypixel moderator'], rolesFound['hypixel admin'], rolesFound['member'])
                        await start.edit(content=None, embed=discord.Embed(description='Hypixel rank\'s based roles successfully set up!', color=discord.Color.orange()))
                        if higher: await ctx.send(f'{higher}/8 of those roles is higher than my top role, therefore I won\'t be able to give it to someone.\n'
                                                  f'In order to be able to give the role I must have a higher role than those.')
                        return
                    elif 'n' in response.content.lower():
                        if cancel: await cancel.delete()
                        em.description = f'**Which role do you want to update?**\n\n' + '\n'.join(f"{i+1}. **{k.title()}**: {rolesFound[k]}" for i, k in enumerate(roles))
                        em.set_footer(text='Choose one at a time.')
                        await start.edit(content=None, embed=em)
                        done = None
                        while True:
                            try: response = await self.bot.wait_for('message', check=check, timeout=120)
                            except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                            if mmPerm: await response.delete()
                            if cancel: await cancel.delete()
                            if any(n in response.content for n in [str(x) for x in range(1,6)]) or any(r == response.content.lower() for r in [str(x) for x in roles]):
                                if response.content.isdigit(): r = list(roles.keys())[int(response.content)-1].title()
                                else: r = response.content.title()
                                msg = await ctx.send(f'Which role do you want to use as {r}')
                                while True:
                                    try: response = await self.bot.wait_for('message', check=check, timeout=120)
                                    except asyncio.TimeoutError: await msg.delete(); await start.delete(); return await ctx.send('You took too long to reply!')
                                    if mmPerm: await response.delete()
                                    if done: await done.delete()
                                    if cancel: await cancel.delete(); cancel=None
                                    if response.content.lower() == 'cancel': return await start.delete()
                                    role = None
                                    if response.role_mentions: role = response.role_mentions[0]
                                    if response.content.isdigit() and not role: role = discord.utils.get(ctx.guild.roles, id=int(response.content))
                                    if not role: role = discord.utils.find(lambda x: x.name.lower() == response.content.lower(), ctx.guild.roles)
                                    if role:
                                        await ctx.send(f'Using {role} as {r} role!', delete_after=10)
                                        roles[r.lower()] = role
                                        try: await msg.delete()
                                        except: pass
                                        em.description = f'**Which role do you want to update?**\n\n' + '\n'.join(f"{i+1}. **{k.title()}**: {rolesFound[k] if not roles[k] else roles[k]}" for i, k in enumerate(roles))
                                        await start.edit(content=None, embed=em)
                                        done = await ctx.send('You can change another role. If you\'re done say `done`.')
                                        break
                                    if not role: cancel = await ctx.send('Couldn\'t find any role. Try again!\nUse `cancel` to exit.', delete_after=10)
                            elif response.content.lower() == 'done':
                                if done: await done.delete()
                                await self.bot.pool.execute("insert into settings.hypixelroles values($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
                                                            ctx.guild.id, roles['vip'].id, roles['vip+'].id, roles['mvp'].id, roles['mvp+'].id, roles['mvp++'].id, roles['hypixel helper'].id, roles['hypixel moderator'].id, roles['hypixel admin'].id, roles['member'].id)
                                return await start.edit(content=None, embed=discord.Embed(color=discord.Color.orange(), description = f"Hypixel rank's based roles successfully set up!"))
                            elif response.content.lower() == 'cancel': return await start.delete()
                            else: cancel = await ctx.send('That\'s not a valid entry. Try again!\nUse `cancel` to exit.')
                    elif response.content.lower() == 'cancel': return await start.delete()
                    else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')
            elif response.content == '2':
                if cancel: await cancel.delete(); cancel=None
                if not ctx.me.guild_permissions.manage_roles:
                    return await ctx.send('Oops, I do not enough permissions for this one.\n'
                                          'You can either create the roles manually and run the setup again or give me the "Manage Roles" permission.')
                em = discord.Embed(description=f'The following roles will be created:\n\n{rolestr}', color=discord.Color.orange()).set_footer(text='Can I proceed with this action? [Y/N]')
                await start.edit(content=None, embed=em)
                while True:
                    try: response = await self.bot.wait_for('message', check=check, timeout=120)
                    except TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                    if mmPerm: await response.delete()
                    if 'y' in response.content.lower():
                        if cancel: await cancel.delete()
                        for role in list(reversed([x for x in roles])):
                            roles[role] = await ctx.guild.create_role(name=role.upper() if len(role)<=5 else role.title(), color=discord.Colour(self.rankColors[role.lower()]))
                        em = discord.Embed(color=discord.Color.orange(), description='The following roles have been created:\n\n'+"\n".join([f"**{x.name}**" for x in roles.values()])).set_footer(text='Hypixel rank\'s based roles successfully set up!')
                        await start.edit(content=None, embed=em)
                        return await self.bot.pool.execute("insert into settings.hypixelroles values($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
                                                           ctx.guild.id, roles['vip'].id, roles['vip+'].id, roles['mvp'].id, roles['mvp+'].id, roles['mvp++'].id, roles['hypixel helper'].id, roles['hypixel moderator'].id, roles['hypixel admin'].id, roles['member'].id)
                    elif 'n' in response.content.lower():
                        if cancel: await cancel.delete()
                        await ctx.send('Setup canceled!')
                        return await start.delete()
                    else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')
            elif response.content.lower() == 'cancel': return await start.delete()
            else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')

    @setup.command(name='rss')
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    async def setupRSS(self, ctx):
        """This will enable a direct feed source in your server from the Hypixel Forums
        Due to this demanding a lot of resources, the feature will be paid."""
        elPerm = ctx.channel.permissions_for(ctx.me).embed_links
        if not (await self.bot.is_owner(ctx.author)):
            isPatron = await self.bot.pool.fetchrow('select * from donators where userid=$1 and active is TRUE', ctx.author.id)
            if isPatron:
                if elPerm: return await ctx.send(embed=discord.Embed(title='Welcome to the Hypixel RSS feed setup!',
                                                                     description='You don\'t seem to qualify to use this command.\nDue to this feature being resource intensive, its limited to [donors](https://www.patreon.com/join/Wonderpants?) only.',
                                                                     color=discord.Color.orange()))
                else: return await ctx.send("You don\'t seem to qualify to use this command.\nDue to this feature being resource intensive, its limited to donors only.")
        cancel = None
        mwPerm = ctx.channel.permissions_for(ctx.me).manage_webhooks
        mmPerm = ctx.channel.permissions_for(ctx.me).manage_messages
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        rssdb = await self.bot.pool.fetchrow('select * from settings.rss where guildid=$1', ctx.guild.id)
        if rssdb:
            wh = WebHook.from_url(rssdb['webhook'], adapter=AsyncWebhookAdapter(self.bot.session))
            wh = discord.utils.find(lambda x: x.id == wh.id, await ctx.guild.webhooks())
            if not wh:
                start = await ctx.send(embed=discord.Embed(title='Welcome to the Hypixel RSS feed setup!', description='Oops, looks like the Hypixel RSS feed has been set up before however someone manually removed it.\nDo you want to set it up again? [Y/N]', color=discord.Color.orange()))
                while True:
                    try: response = await self.bot.wait_for('message', check=check, timeout=120)
                    except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                    if mmPerm: await response.delete()
                    if cancel: await cancel.delete()
                    if response.content.lower() == 'cancel': return await start.delete()
                    if 'y' in response.content.lower():
                        await start.delete()
                        await self.bot.pool.execute('delete from settings.rss where guildid=$1', ctx.guild.id)
                        return await ctx.reinvoke()
                    elif 'n' in response.content.lower():
                        await start.delete()
                        return await self.bot.pool.execute('delete from settings.rss where guildid=$1', ctx.guild.id)
                    else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')
            start = await ctx.send(embed=discord.Embed(title='Welcome to the Hypixel RSS feed setup!', description=f'This server has the RSS feed set up to the channel <#{wh.channel_id}>.\nDo you want to delete it? [Y/N]', color=discord.Color.orange()))
            while True:
                try: response = await self.bot.wait_for('message', check=check, timeout=120)
                except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                if mmPerm: await response.delete()
                if cancel: await cancel.delete()
                if response.content.lower() == 'cancel': return await start.delete()
                if 'y' in response.content.lower(): await start.delete(); return await self.bot.pool.execute('delete from settings.rss where guildid=$1', ctx.guild.id)
                elif 'n' in response.content.lower(): return await start.delete()
                else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')
        em = discord.Embed(title='Welcome to the Hypixel RSS feed setup!',
                           description=f'**1**. Search for webhooks in this channel.{" [**No Perms**]" if not mwPerm else ""}\n'
                                       f'**2**. Create a weebhook here.{" [**No Perms**]" if not mwPerm else ""}\n'
                                       f'**3**. Manually insert the webhook.', color=discord.Color.orange()).set_footer(text='Select the option you want.')
        start = await ctx.send(embed=em)
        while True:
            try: response = await self.bot.wait_for('message', check=check, timeout=120)
            except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
            if mmPerm: await response.delete()
            if cancel: await cancel.delete()
            if response.content.lower() == 'cancel':
                return await start.delete()
            elif response.content == '1':
                if not mwPerm: return await ctx.send('I do not have permissions to search for webhooks in this channel.')
                wbFound = [wh for wh in (await ctx.channel.webhooks())]
                if not wbFound:
                    await start.edit(embed=discord.Embed(title='Hypixel RSS feed setup!', description = 'No webhook was found!\n*Restarting webhook setup!*', color=discord.Color.orange()))
                    await asyncio.sleep(5); return await ctx.reinvoke()
                em.description = f"**Found the following webhooks**:\n\n" + '\n'.join([f"{i+1}. {x.name}" for i, x in enumerate(wbFound)])+'\n\u200b'
                em.set_footer(text='Select the option you want')
                await start.edit(content=None, embed=em)
                while True:
                    try: response = await self.bot.wait_for('message', check=check, timeout=120)
                    except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                    if mmPerm: await response.delete()
                    if cancel: await cancel.delete()
                    if response.content.lower() == 'cancel': return await start.delete()
                    if response.content.isdigit() and 0 < int(response.content) <= len(wbFound): webHook = wbFound[int(response.content)-1]
                    else: webHook = discord.utils.find(lambda wh: wh.name.lower() == response.content)
                    if not webHook: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')
                    else:
                        webHook = webHook.url
                        wh = Webhook(url=webHook, username="Hypixel RSS", avatar_url=self.bot.user.avatar_url, color=discord.Color.orange().value, title="Hypixel RSS feed setup!")
                        wh.description = 'Hypixel RSS feed set up successfully!'
                        await self.bot.pool.execute('insert into settings.rss values($1, $2, $3)', ctx.guild.id, ctx.author.id, webHook)
                        await start.delete()
                        return wh.post()
            elif response.content == '2':
                if not mwPerm: return await ctx.send('I do not have permissions to create webhooks in this channel.')
                wbHook = await ctx.channel.create_webhook(name='Hypixel RSS')
                wh = Webhook(url=wbHook.url, username="Hypixel RSS", avatar_url=self.bot.user.avatar_url, session=self.bot.session)
                wh.description = 'Hypixel RSS feed set up successfully!'
                await self.bot.pool.execute('insert into settings.rss values($1, $2, $3)', ctx.guild.id, ctx.author.id, wbHook.url)
                return wh.post()
            elif response.content == '3':
                await start.edit(content=None, embed=discord.Embed(title='Hypixel RSS feed setup!', color=discord.Color.orange(), description='Insert the webhook url.'))
                while True:
                    try: response = await self.bot.wait_for('message', check=check, timeout=120)
                    except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                    if mmPerm: await response.delete()
                    if response.content.lower() == 'cancel': return await start.delete()
                    wh = WebHook.from_url(response.content, adapter=AsyncWebhookAdapter(self.bot.session))
                    wh = discord.utils.find(lambda x: x.id == wh.id, await ctx.guild.webhooks())
                    if wh.channel_id == ctx.channel.id: await self.bot.pool.execute('insert into settings.rss values($1, $2, $3)', ctx.guild.id, ctx.author.id, wh.url)
                    elif wh.guild_id != ctx.guild.id: return await start.edit(content=None, embed=discord.Embed(title='Hypixel RSS feed setup!', color=discord.Color.orange(), description='That webhook doesn\'t belong to this server!'))
                    elif wh.channel_id != ctx.channel.id:
                        await start.edit(content=None, embed=discord.Embed(title='Hypixel RSS feed setup!', color=discord.Color.orange(), description=f'That webhook belongs to <#{wh.channel_id}>\nDo you want to continue? [Y/N]'))
                        while True:
                            try: response = await self.bot.wait_for('message', check=check, timeout=120)
                            except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
                            if mmPerm: await response.delete()
                            if cancel: await cancel.delete()
                            if 'y' in response.content.lower():
                                await self.bot.pool.execute('insert into settings.rss values($1, $2, $3)', ctx.guild.id, ctx.author.id, wh.url)
                                await start.edit(content=None, embed=discord.Embed(title='Hypixel RSS feed setup!', color=discord.Color.orange(), description=f'Hypixel RSS feed set up successfully!'))
                            elif 'n' in response.content.lower():
                                return await start.delete()
                            else: cancel = await ctx.send('That option doesn\t seem to be valid. Try again!\nUse `cancel` to exit.')
                    elif not wh:
                        await start.edit(content=None, embed=discord.Embed(title='Hypixel RSS feed setup!', color=discord.Color.orange(), description=f'That webhook isn\'t valid. Try again!\nUse `cancel` to exit.'))
            else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')

    @commands.group(name='ignore', invoke_without_command=True, case_insensitive=True)
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @is_mod()
    async def ignore(self, ctx):
        """Enable or Disable the use of commands in channels.
        Usage:
            [p]ignore - Opens the current channel's ignore menu.
            [p]ignore list - Shows currently ignored channels in the server.
            [p]ignore add <channel> - Disables usage of commands in that channel.
            [p]ignore remove <channel> - Allows the usage of commands in that channel."""
        cancel = None
        def check(m): return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        mmPerm = ctx.channel.permissions_for(ctx.me).manage_messages
        channels = await self.bot.pool.fetch('select * from settings.ignore where guildid=$1', ctx.guild.id)
        channelsID = [x["channelid"] for x in channels]
        em = discord.Embed(color=discord.Color.orange())
        em.description = f"**Channel Ignore Menu - <#{ctx.channel.id}>**\n\n" \
                         f"Ignore every command besides this one in this channel.\n\n" \
                         f"**1**. {'Uni' if ctx.channel.id in channelsID else 'I'}gnore channel: {ctx.channel.name}." + (
            "\n**2**. Show ignored channels." if channelsID else ""
        ) + '\n\nType the appropriate number to access the menu.\n' \
            'type \'cancel\' to leave the menu.'
        start = await ctx.send(embed=em)
        while True:
            try: response = await self.bot.wait_for('message', check=check, timeout=120)
            except asyncio.TimeoutError: await start.delete(); return await ctx.send('You took too long to reply!')
            if mmPerm: await response.delete()
            if cancel: await cancel.delete(); cancel=None
            if response.content == '1':
                ignored = ctx.channel.id in channelsID
                if ignored:
                    await ctx.pool.execute('delete from settings.ignore where channelid=$1', ctx.channel.id)
                    await start.delete()
                    await self.bot.ignored.load()
                    return await ctx.send(f'\🔇 | un-Ignoring all commands from the channel <#{ctx.channel.id}>')
                else:
                    await ctx.pool.execute('insert into settings.ignore(guildid, channelid) values($1, $2)', ctx.guild.id, ctx.channel.id)
                    await start.delete()
                    await self.bot.ignored.load()
                    return await ctx.send(f'\🔇 | Ignoring all commands from the channel <#{ctx.channel.id}>')
            elif response.content == '2' and channelsID:
                known = []
                unknown = []
                for id in channelsID:
                    channel = ctx.guild.get_channel(id)
                    if channel: known.append(f"<#{channel.id}>")
                    else: unknown.append(id)
                await start.delete()
                return await ctx.send(f"\🔇 Ignored channels in **{ctx.guild.name}**:\n\n{', '.join(known)}")
            elif response.content.lower() == 'cancel': return await start.delete()
            else: cancel = await ctx.send('That option doesn\'t seem to be valid. Try again!\nUse `cancel` to exit.')

    @ignore.command(name='list', case_insensitive=True)
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @is_mod()
    async def ignore_list(self, ctx):
        """Shows currently ignored channels"""
        ignored = await self.bot.pool.fetch('select * from settings.ignore where guildid=$1', ctx.guild.id)
        if not ignored: return await ctx.send('There are no ignored channels in this server.')
        channels = [x['channelid'] for x in ignored]
        known = []
        unknown = []
        for id in channels:
            channel = ctx.guild.get_channel(id)
            if channel: known.append(f"<#{channel.id}>")
            else: unknown.append(id)
        if not known: return await ctx.send('There were ignored channels but they were manually removed!')
        message = f"\🔇 Ignored channels in {ctx.guild.name}:\n\n"
        await ctx.send(message+', '.join(known))

    @ignore.command(name='add', case_insensitive=True)
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @is_mod()
    async def ignore_add(self, ctx, *, channel: discord.TextChannel):
        """Makes the bot ignore a certain channel."""
        ignored = await self.bot.pool.fetch('select * from settings.ignore where guildid=$1', ctx.guild.id)
        channels = [x['channelid'] for x in ignored]
        if channel.id in channels: return await ctx.send('That channel was already ignored!')
        await self.bot.pool.execute('insert into settings.ignore(guildid, channelid) values($1, $2)', ctx.guild.id, channel.id)
        await ctx.send(f'\🔇 | Ignoring all commands from the channel <#{channel.id}>')
        await self.bot.ignored.load()

    @ignore.command(name='remove', case_insensitive=True)
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @is_mod()
    async def ignore_remove(self, ctx, *, channel: discord.TextChannel):
        """Makes the bot un-ignore a certain channel."""
        ignored = await self.bot.pool.fetch('select * from settings.ignore where guildid=$1', ctx.guild.id)
        channels = [x['channelid'] for x in ignored]
        if channel.id not in channels: return await ctx.send('That channel is not ignored!')
        await self.bot.pool.execute('delete from settings.ignore where channelid=$1', channel.id)
        await ctx.send(f'\🔇 | un-Ignoring all commands from the channel <#{channel.id}>')
        self.bot.ignored.list[ctx.guild.id].remove(channel.id)
        if not self.bot.ignored.list[ctx.guild.id]:
            self.bot.ignored.list.pop(ctx.guild.id)

def setup(bot):
    bot.add_cog(Config(bot))
