import re

from cogs.utils import context, time
import asyncio
import copy
import logging
import traceback
from cogs.utils.hypixel import Player

import asyncpg
from PIL import Image
from io import BytesIO
from uuid import uuid4
import time as t

import discord
from discord.ext import commands

class utils:
    def __init__(self, bot):
        self.bot = bot
        self.reaction_emojis = ['⏮', '◀', '▶', '⏭', '⏹']
        self.Mojang_username = 'https://api.mojang.com/users/profiles/minecraft/{username}'
        self.rank = {'RED': [0xFF5555, "https://preview.ibb.co/mUVKtA/mvp-red.png", "https://preview.ibb.co/gDJYLq/mvp-red.png"],
                     'GOLD': [0xFFAA00, "https://preview.ibb.co/dhQKtA/mvp-gold.png","https://preview.ibb.co/imW9tA/mvp-gold.png"],
                     'GREEN': [0x55FF55, "https://preview.ibb.co/m5VV0q/mvp-green.png", "https://preview.ibb.co/mGTNDA/mvp-green.png"],
                     'YELLOW': [0xFFFF55, "https://preview.ibb.co/iv4ZRV/mvp-yellow.png", "https://preview.ibb.co/cks4RV/mvp-yellow.png"],
                     'LIGHT_PURPLE': [0xFF55FF, "https://preview.ibb.co/g4tHfq/mvp-lightpurple.png", "https://preview.ibb.co/nwu7fq/mvp-lightpurple.png"],
                     'WHITE': [0xFFFFFF, "https://preview.ibb.co/kUcXDA/mvp-white.png", "https://preview.ibb.co/n4T00q/mvp-white.png"],
                     'BLUE': [0x5555FF, "https://preview.ibb.co/hevf0q/mvp-blue.png", "https://preview.ibb.co/ih7omV/mvp-blue.png"],
                     'DARK_BLUE': [0x0000AA, "https://preview.ibb.co/hevf0q/mvp-blue.png", "https://preview.ibb.co/ih7omV/mvp-blue.png"],
                     'DARK_GREEN': [0x00AA00, "https://preview.ibb.co/btPetA/mvp-darkgreen.png", "https://preview.ibb.co/kWZvYA/mvp-darkgreen.png"],
                     'DARK_RED': [0xAA0000, "https://preview.ibb.co/ivm3Lq/mvp-darkred.png", "https://preview.ibb.co/dsXFYA/mvp-darkred.png"],
                     'DARK_AQUA': [0x00AAAA, "https://preview.ibb.co/hJMsDA/mvp-darkaqua.png", "https://preview.ibb.co/f3P7fq/mvp-darkaqua.png"],
                     'DARK_PURPLE': [0xAA00AA, "https://preview.ibb.co/iRKZRV/mvp-darkpurple.png", "https://preview.ibb.co/e7JNDA/mvp-darkpurple.png"],
                     'DARK_GRAY': [0xAAAAAA, "https://preview.ibb.co/hPkxfq/mvp-darkgray.png", "https://preview.ibb.co/hBodmV/mvp-darkgray.png"],
                     'BLACK': [0x000000, "https://preview.ibb.co/i4YYLq/mvp-black.png", "https://preview.ibb.co/cM3uRV/mvp-black.png"],
                     'HELPER': [0x5555FF, "https://preview.ibb.co/eAqDLq/helper.png"],
                     "MODERATOR": [0x00AA00, "https://preview.ibb.co/c802DA/mod.png"],
                     "ADMIN": [0xFF5555, "https://preview.ibb.co/d9tptA/admin.png"]}
        self.uuid_library = {}

    async def _discord_account(self, ctx, playerJSON, rank):
        if "socialMedia" in playerJSON and "links" in playerJSON["socialMedia"] and "DISCORD" in playerJSON["socialMedia"]["links"]:
            discordAccount = playerJSON["socialMedia"]["links"]["DISCORD"]
            if f'{ctx.author.name}#{ctx.author.discriminator}' == discordAccount:
                data = await self.bot.pool.fetchrow("select * from hypixel where userid=$1", ctx.author.id)
                if not data:
                    await self.bot.pool.execute("""with upsert as (update hypixel set userid=$1, useruuid=$2  where useruuid=$2 returning *)
                                                            insert into hypixel(userid, useruuid) select $1, $2 where not exists (select * from upsert)""", ctx.author.id, playerJSON['uuid'])
        if ctx.guild: await self.updateRole(ctx, rank, playerJSON)

    async def cog_before_invoke(self, ctx):
        try:
            await ctx.trigger_typing()
        except:
            pass

    async def _get_user_by_uuid(self, uuid, ctx):
        data = await self.bot.pool.fetchrow("select * from hypixel where useruuid=$1", uuid)
        if data:
            user_id = int(data[0])
            if type(ctx.channel) != discord.channel.DMChannel and discord.utils.get(ctx.guild.members, id=user_id):
                return f'<@{user_id}>'
            else:
                return await self.bot.fetch_user(user_id)
        else:
            return None

    async def _get_user(self, ctx, index=0, author=False):
        mention = True
        if ctx.message.mentions and not author:
            author = ctx.message.mentions[index]
            if author.bot:
                await ctx.send('Invalid user type.')
                return None
            author = str(author.id)
        else:
            author = ctx.message.author.id
            mention = False
        data = await self.bot.pool.fetchrow(f"select * from hypixel where userID={author}")
        if data: return data
        if mention:
            await ctx.send(f'`{ctx.message.mentions[index].name}#{ctx.message.mentions[index].discriminator}` doesn\'t seem to have their minecraft account associated')
            return None
        else:
            await ctx.send_help(ctx.command)
            return None

    async def _get_users(self, ctx, user1, user2):
        if not user1 and not user2:
            return await ctx.send_help(ctx.command)
        if user1.startswith('<'):
            user1 = await self._get_user(ctx)
            if user2 and user2.startswith('<'):
                user2 = await self._get_user(ctx, 1)
        elif user2 and user2.startswith('<'):
            user2 = await self._get_user(ctx)
        if not user2:
            user2 = user1
            user1 = await self._get_user(ctx, author=True)
        if not user1 or not user2:
            return await ctx.send('Failed to get both players.')
        if type(user1) == asyncpg.Record: user1 = user1['useruuid']
        if type(user2) == asyncpg.Record: user2 = user2['useruuid']
        return user1, user2

    async def _get_players(self, player, ctx):
        try:
            player = self.bot.hypixel.Player(player)
        except self.bot.hypixel.PlayerNotFoundException as e:
            return await ctx.send(f"Couldn't find the user `{player}`")
        except self.bot.hypixel.HypixelAPIError:
            return await ctx.send('There seems to be an error with the API. Try again later.')
        except self.bot.hypixel.HypixelAPIThrottle:
            return await ctx.send('There\'s a global throttle. Try again later.')
        return player

    async def getSkin(self, uuid):
        file = BytesIO()
        response = await self.bot.session.get(f'https://visage.surgeplay.com/full/256/{uuid}')
        if response.status != 200:
            return await self.getSkin('X-Steve')
        img = Image.open(BytesIO(await response.read()))
        img.save(file, 'PNG')
        # file.seek(0)

        return discord.File(file, f"{str(uuid4()).replace('-', '')}.png")

    async def send(self, ctx, embeds=None, message=None, destroy=False, file=None):
        guild = False
        if ctx.command.name == 'guild': guild = True

        reaction_emojis = copy.copy(self.reaction_emojis)
        if guild: reaction_emojis.append('ℹ')

        def check(reaction, user):
            if reaction.message.id == message.id:
                if str(reaction.emoji) in reaction_emojis:
                    if user.id in [ctx.message.author.id, 98141664303927296]: return True

        try:
            page = 0
            channel = ctx.channel
            permissions = ctx.channel.permissions_for(ctx.me)
            if len(embeds) == 1 or (len(embeds) == 2 and guild):
                embed = embeds[list(embeds)[0]]
                if message:
                    if guild:
                        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
                        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
                        for reaction in list(reversed(reaction_emojis[-2:])): await message.add_reaction(reaction)
                    await message.edit(content=None, embed=embed)
                    if not guild: return
                elif not message:
                    message = await channel.send(embed=embed, file=file)
                    if guild:
                        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
                        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
                        for reaction in list(reversed(reaction_emojis[-2:])): await message.add_reaction(reaction)
                    if not guild: return

            main = True
            while guild and len(embeds) == 2:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=120)
                except asyncio.TimeoutError:
                    if not permissions.manage_messages:
                        message = await channel.fetch_message(message.id)
                        if message:
                            for reaction in message.reactions:
                                if reaction.me: await message.remove_reaction(reaction, ctx.me)
                    else:
                        await message.clear_reactions()
                    del reaction_emojis
                    return
                await asyncio.sleep(0.1)
                try:
                    await message.remove_reaction(reaction, user)
                except:
                    pass

                if str(reaction) == reaction_emojis[-1]:
                    if main:
                        await message.edit(content=None, embed=embeds['info'])
                        main = False
                    else:
                        await message.edit(content=None, embed=embeds['0'])
                        main = True

                elif str(reaction) == reaction_emojis[4]:
                    if destroy: await message.delete()
                    if not ctx.channel.permissions_for(ctx.me).manage_messages:
                        message = await channel.fetch_message(message.id)
                        if message:
                            for reaction in message.reactions:
                                if reaction.me:
                                    await message.remove_reaction(reaction, ctx.me)
                    else:
                        await message.clear_reactions()
                    del reaction_emojis
                    return

            if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
            if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
            if message:
                await message.edit(content=None, embed=embeds[list(embeds)[page]])
            elif not message:
                message = await channel.send(embed=embeds[list(embeds)[page]], file=file)

            interval = t.monotonic()
            for reaction in reaction_emojis: await message.add_reaction(reaction); await asyncio.sleep(0.2)

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=120)
                except asyncio.TimeoutError:
                    if not permissions.manage_messages:
                        message = await channel.fetch_message(message.id)
                        if message:
                            for reaction in message.reactions:
                                if reaction.me: await message.remove_reaction(reaction, ctx.me)
                    else:
                        await message.clear_reactions()
                    return
                if (t.monotonic() - interval) < 1: continue
                interval = t.monotonic()
                try:
                    await asyncio.sleep(0.1)
                    await message.remove_reaction(reaction, user)
                except:
                    pass

                if str(reaction) == reaction_emojis[0] and main:
                    if page != 0:
                        page = 0
                        await message.edit(content=None, embed=embeds[list(embeds)[page]])

                elif str(reaction) == reaction_emojis[1] and main:
                    if page == 0:
                        pass
                    else:
                        page -= 1
                        await message.edit(content=None, embed=embeds[list(embeds)[page]])

                elif str(reaction) == reaction_emojis[2] and main:
                    if page == len(embeds) - (1 if not guild else 2):
                        pass
                    else:
                        page += 1
                        await message.edit(content=None, embed=embeds[list(embeds)[page]])

                elif str(reaction) == reaction_emojis[3] and main:
                    if page != len(embeds) - (1 if not guild else 2):
                        page = len(embeds) - (1 if not guild else 2)
                        await message.edit(content=None, embed=embeds[list(embeds)[page]])

                elif str(reaction) == reaction_emojis[4]:
                    if destroy: await message.delete()
                    if ctx.channel.permissions_for(ctx.me).manage_messages: await message.clear_reactions()
                    return

                elif str(reaction) == reaction_emojis[-1]:
                    if main:
                        await message.edit(content=None, embed=embeds['info'])
                        main = False
                    else:
                        await message.edit(content=None, embed=embeds[list(embeds)[page]])
                        main = True

        except discord.errors.NotFound:
            return

    async def updateRole(self, ctx, rank, playerJSON):
        if ctx.guild and ctx.guild.id in await self.bot.settings().hypixelRoles():
            guild = ctx.guild
            ranksdb = await self.bot.pool.fetchrow('select * from settings.hypixelroles where guildid=$1', guild.id)
            rank = rank.lower()
            if rank in ['helper', 'moderator', 'admin']: rank = 'hypixel ' + rank
            # User is in cache
            if str(ctx.author.id) in self.bot.rankCache:
                rank = self.bot.rankCache[str(ctx.author.id)].lower()
                if rank == 'non': rank = 'member'
                role = discord.utils.get(guild.roles, id=ranksdb[rank.lower()])
                logging.warning(str(role))
                extraRoles = list(filter(lambda x: x is not None, [discord.utils.get(guild.roles, id=r) for r in ranksdb if role and r != role.id]))
                try:
                    await ctx.author.add_roles(role, reason='Rank Update')
                    await ctx.author.remove_roles(*extraRoles, reason='Rank Update')
                except Exception as error:
                    trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
                    logging.error(f'Channel: {ctx.channel} | User: {ctx.author} | {ctx.author.id}\nCommand: {ctx.message.content}\n```{"".join(trace)}```')
            else:
                # is user verified?
                user = await self.bot.pool.fetchrow('select * from public.hypixel where userid=$1 and useruuid=$2', ctx.author.id, playerJSON['uuid'])
                if not user: return logging.info('DEBUG: user not verified')
                if rank == 'non': rank = 'member'
                self.bot.rankCache[str(ctx.author.id)] = rank  # cache their rank
                await self.updateRole(ctx, rank, playerJSON)
                # role = discord.utils.get(guild.roles, id=ranksdb[rank.lower()])
                # logging.warning(str(role))
                # extraRoles = list(filter(lambda x: x is not None, [discord.utils.get(guild.roles, id=r) for r in ranksdb if role and r != role.id]))
                # try:
                #     await ctx.author.add_roles(role, reason='Rank Update')
                #     await ctx.author.remove_roles(*extraRoles, reason='Rank Update')
                # except Exception as error:
                #     trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
                #     logging.error(f'Channel: {ctx.channel} | User: {ctx.author} | {ctx.author.id}\nCommand: {ctx.message.content}\n```{"".join(trace)}```')

    async def findUser(self, ctx, user):
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        if user == '' or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
            data = await self._get_user(ctx)
            if not data: return
            user = data['useruuid']
        elif not re.fullmatch("([A-Za-z0-9_]+){1,16}", user):
            return await ctx.send("That username doesn't seem to be valid.")
        try: player = self.bot.hypixel.Player(user)
        except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
        except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
        except self.bot.hypixel.HypixelAPIThrottle: return await ctx.send('There\'s a global throttle. Try again later.')
        return player
