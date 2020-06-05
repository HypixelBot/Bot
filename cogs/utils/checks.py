from discord.ext import commands
import discord
import json

# The permission system of the bot is based on a "just works" basis
# You have permissions and the bot has permissions. If you meet the permissions
# required to execute the command (and the bot does as well) then it goes through
# and you can execute the command.
# Certain permissions signify if the person is a moderator (Manage Server) or an
# admin (Administrator). Having these signify certain bypasses.
# Of course, the owner will always be able to execute commands.

def load_config():
    with open('settings/config.json') as f:
        return json.load(f)

async def check_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)

async def check_guild_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_guild_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_guild_permissions(ctx, perms, check=check)
    return commands.check(pred)

def is_mod():
    async def pred(ctx):
        if not ctx.guild: return True
        if ctx.guild.owner and ctx.guild.owner.id == ctx.author.id: return True
        return await check_guild_permissions(ctx, {'manage_guild': True})
    return commands.check(pred)

def is_admin():
    async def pred(ctx):
        if not ctx.guild: return True
        if ctx.guild.owner and ctx.guild.owner.id == ctx.author.id: return True
        return await check_guild_permissions(ctx, {'administrator': True})
    return commands.check(pred)

def mod_or_permissions(**perms):
    perms['manage_guild'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)

def admin_or_permissions(**perms):
    perms['administrator'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)

def is_in_guilds(guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        if type(guild_ids) is int:
            return guild.id == guild_ids
        return guild.id in guild_ids
    return commands.check(predicate)

def is_in_channels(*channel_ids):
    def predicate(ctx):
        channel = ctx.channel
        if channel is None:
            return False
        return channel.id in channel_ids
    return commands.check(predicate)

def embed_perms(ctx):
    return ctx.channel.permissions_for(ctx.me).embed_links

def is_guild_owner():
    async def predicate(ctx):
        is_owner = await ctx.bot.is_owner(ctx.author)
        if is_owner: return True
        return ctx.guild.owner and ctx.guild.owner.id == ctx.author.id
    return commands.check(predicate)

def has_voted():
    async def predicate(ctx):
        # is_owner = await ctx.bot.is_owner(ctx.author)
        # if is_owner: return True
        return await ctx.bot.pool.fetch(f'select * from votes where userID={ctx.author.id} and active is TRUE')
    return commands.check(predicate)

def find_all(predicate, seq):
    elements = []
    for element in seq:
        if predicate(element):
            elements.append(element)
    if elements: return elements
    return None

def staff(guild):
    roles = find_all(lambda r: not r.managed and (r.permissions.administrator or r.permissions.manage_guild or r.permissions.kick_members or r.permissions.ban_members or r.permissions.manage_nicknames or r.permissions.manage_channels or r.permissions.manage_messages or r.permissions.manage_roles or r.permissions.manage_webhooks or r.permissions.manage_emojis), guild.roles)
    for r in roles:
        if all(m.bot for m in r.members):
            roles.pop(roles.index(r))
    return roles

def is_staff():
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author): return True
        if type(ctx.channel) == discord.channel.DMChannel: return False
        try: return any(r in staff(ctx.guild) for r in ctx.author.roles)
        except: return False
    return commands.check(predicate)
