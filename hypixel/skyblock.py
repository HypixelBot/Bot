import asyncio
import base64
import copy
import logging
from collections import Counter

import io
import time as t
from argparse import Namespace

from cogs.utils.checks import *
from cogs.utils.time import *

log = logging.getLogger(__name__)

def list_factory(data):
    items = []
    for i in data:
        items.append(i[0])
    return items

def wrap_by_space(s, n):
    '''returns a string where \\n is inserted between every n words'''
    a = s.split()
    ret = ''
    for i in range(0, len(a), n):
        ret += ', '.join(a[i:i + n]) + '\n'

    return ret

def isAllowed(ctx):
    return ctx.message.author.id in [
        98141664303927296, 398500131747659778
    ]

def validate(x, y, **kwargs):
    try:
        if type(x) is dict: x = Namespace(**x)
        if y in x:
            value = eval(f"{x}.{y}")
            if kwargs.get('decimal'): return f"{value:,.2f}"
            if kwargs.get('comma'): return f"{(len(value) if (type(value) is list) else value):,}"
            return value
        else:
            return 0
    except SyntaxError:
        return vars(x)[y]
def bossKills(b):
    return sum([b[k] for k in b if k.startswith('boss_kills_tier')])

class Skyblock(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reaction_emojis = ['⬅', '➡']
        self.Mojang_username = 'https://api.mojang.com/users/profiles/minecraft/{username}'
        self.rank = {'RED': [0xFF5555, "https://preview.ibb.co/mUVKtA/mvp-red.png", "https://preview.ibb.co/gDJYLq/mvp-red.png"],
                     'GOLD': [0xFFAA00, "https://preview.ibb.co/dhQKtA/mvp-gold.png","https://preview.ibb.co/imW9tA/mvp-gold.png"],
                     'GREEN': [0x55FF55, "https://preview.ibb.co/m5VV0q/mvp-green.png", "https://preview.ibb.co/mGTNDA/mvp-green.png"],
                     'YELLOW': [0xFFFF55, "https://preview.ibb.co/iv4ZRV/mvp-yellow.png", "https://preview.ibb.co/cks4RV/mvp-yellow.png"],
                     'LIGHT_PURPLE': [0xFF55FF, "https://preview.ibb.co/g4tHfq/mvp-lightpurple.png", "https://preview.ibb.co/nwu7fq/mvp-lightpurple.png"],
                     'WHITE': [0xFFFFFF, "https://preview.ibb.co/kUcXDA/mvp-white.png", "https://preview.ibb.co/n4T00q/mvp-white.png"],
                     'BLUE': [0x5555FF, "https://preview.ibb.co/hevf0q/mvp-blue.png", "https://preview.ibb.co/ih7omV/mvp-blue.png"],
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
        if ctx.guild and ctx.guild.id in await self.bot.settings().hypixelRoles():
            guild = ctx.guild
            user = await self.bot.pool.fetchrow('select useruuid from public.hypixel where userid=$1', ctx.author.id)
            ranksdb = await self.bot.pool.fetchrow('select * from settings.hypixelroles where guildid=$1', guild.id)
            if str(ctx.author.id) in self.bot.rankCache:
                try: await ctx.author.add_roles(discord.utils.get(guild.roles, id=ranksdb[self.bot.rankCache[str(ctx.author.id)].lower()]))
                except: pass
            elif user:
                self.bot.rankCache[str(ctx.author.id)] = rank
                try: await ctx.author.add_roles(discord.utils.get(guild.roles, id=ranksdb[rank.lower()]))
                except: pass

    async def cog_before_invoke(self, ctx):
        try: await ctx.trigger_typing()
        except: pass

    async def UsernameFromUUUID(self, uuid):
        request = await self.bot.session.get(f'https://api.mojang.com/user/profiles/{uuid}/names')
        if request.reason != 'OK': return uuid
        username = (await request.json())[-1]['name']
        await self.bot.pool.execute(f"""INSERT INTO usernames 
                                        VALUES('{uuid}', '{username}') ON CONFLICT (uuid) DO UPDATE SET username = excluded.username""")
        return username

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

    async def send(self, ctx, embeds = None, message=None, destroy=False, file=None):
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
                    await message.edit(content=None, embed = embed)
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
                try: reaction, user = await self.bot.wait_for('reaction_add', check = check, timeout = 120)
                except asyncio.TimeoutError:
                    if not permissions.manage_messages:
                        message = await channel.fetch_message(message.id)
                        if message:
                            for reaction in message.reactions:
                                if reaction.me: await message.remove_reaction(reaction, ctx.me)
                    else: await message.clear_reactions()
                    del reaction_emojis
                    return
                await asyncio.sleep(0.1)
                try: await message.remove_reaction(reaction, user)
                except: pass

                if str(reaction) == reaction_emojis[-1]:
                    if main: await message.edit(content=None, embed = embeds['info']); main = False
                    else: await message.edit(content=None, embed = embeds['0']); main = True

                elif str(reaction) == reaction_emojis[4]:
                    if destroy: await message.delete()
                    if not ctx.channel.permissions_for(ctx.me).manage_messages:
                        message = await channel.fetch_message(message.id)
                        if message:
                            for reaction in message.reactions:
                                if reaction.me:
                                    await message.remove_reaction(reaction, ctx.me)
                    else: await message.clear_reactions()
                    del reaction_emojis
                    return

            if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
            if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
            if message: await message.edit(content=None, embed = embeds[list(embeds)[page]])
            elif not message: message = await channel.send(embed = embeds[list(embeds)[page]], file=file)

            interval = t.monotonic()
            for reaction in reaction_emojis: await message.add_reaction(reaction); await asyncio.sleep(0.2)

            while True:
                try: reaction, user = await self.bot.wait_for('reaction_add', check = check, timeout = 120)
                except asyncio.TimeoutError:
                    if not permissions.manage_messages:
                        message = await channel.fetch_message(message.id)
                        if message:
                            for reaction in message.reactions:
                                if reaction.me: await message.remove_reaction(reaction, ctx.me)
                    else: await message.clear_reactions()
                    return
                if (t.monotonic() - interval) < 1: continue
                interval = t.monotonic()
                try: await asyncio.sleep(0.1); await message.remove_reaction(reaction, user)
                except: pass

                if str(reaction) == reaction_emojis[0] and main:
                    if page == 0: pass
                    else:
                        page-=1
                        await message.edit(content=None, embed = embeds[list(embeds)[page]])

                elif str(reaction) == reaction_emojis[1] and main:
                    if page == len(embeds) - (1 if not guild else 2): pass
                    else:
                        page+=1
                        await message.edit(content=None, embed = embeds[list(embeds)[page]])


        except discord.errors.NotFound: return

    @commands.group(invoke_without_command = True, aliases=['sb'], case_insensitive=True)
    # @commands.check(isAllowed)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def skyblock(self, ctx, *, args: str = ''):
        """Type `[p]help skyblock` for more information about the command.

            [p]skyblock [user]

            **__Subcommands:__**
            **W**ork **I**n **P**rogress
            ~~[p]skyblock [__user__] [__profile__]~~
            ~~[p]skyblock [__profile__] *if you've verified yourself on the bot*~~

            [p]skyblock darkauction
            [p]skyblock magmaboss
            """
        split = args.split()
        user = split[0] if len(split) > 0 else None
        sbProfile = split[1] if len(split) > 1 else None
        if user in ['Grapes', 'Peach', 'Mango', 'Papaya', 'Watermelon',
                    'Lemon', 'Cucumber', 'Kiwi', 'Blueberry', 'Raspberry',
                    'Pomegranate', 'Orange', 'Pineapple', 'Zucchini', 'Pear',
                    'Apple', 'Lime', 'Banana', 'Tomato', 'Strawberry', 'Coconut']:
            sbProfile = user
            user = ''
        if ctx.invoked_subcommand is None:
            async with ctx.channel.typing():
                start = datetime.datetime.now()
                permissions = ctx.channel.permissions_for(ctx.me)
                if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
                if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
                if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
                if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
                    data = await self._get_user(ctx)
                    if not data: return
                    user = data['useruuid']
                try: SBuser = self.bot.hypixel.Skyblock(user)
                except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
                except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
                except self.bot.hypixel.SkyblockNotPlayed: return await ctx.send(f'Looks like {user} never played SkyBlock before.')
                profiles = SBuser.getProfiles()
                playerRank = SBuser.player.getRank()
                playerName = SBuser.player.getName()
                if sbProfile and sbProfile not in profiles: return await ctx.send(f"Looks like {playerName} doesn't have any profile by the name {sbProfile}")
                if not profiles: return await ctx.send(f"Looks like {playerName} doesn't have any SkyBlock profile.")
                onlineStatus = SBuser.player.getOnlineStatus()
                playerSession = SBuser.player.getSession()
                if playerRank["rank"] == 'Youtuber': colour = self.rank["RED"][0]
                elif playerRank['rank'].title() in ['Helper', 'Moderator', 'Admin']: colour = self.rank[playerRank['rank'].upper()][0]
                elif "rankPlusColor" in SBuser.player.JSON: colour = self.rank[SBuser.player.JSON["rankPlusColor"]][0]
                else: colour = 0x55FFFF
                if playerSession and 'gameType' in playerSession:
                    footer = f'Currently in a {playerSession["gameType"].title()} game'
                    onlineStatus = True
                else: footer = self.bot.footer
                if onlineStatus: footer_url = 'https://image.ibb.co/h9VNfq/image.png'
                else: footer_url = 'https://image.ibb.co/hwheRV/image.png'
                embeds = {}
                emb = {
                    'embed': {
                        'title': f'{"[" + playerRank["prefix"] + "]" if playerRank["prefix"] else "[" + playerRank["rank"] + "]"} {playerName}' if playerRank["rank"] != 'Non' else playerName,
                        'url': f'https://hypixel.net/player/{playerName}',
                        'color': colour,
                        # 'description': ''
                    },
                    'footer': {
                        'text': footer,
                        'icon_url': footer_url
                    },
                    'thumbnail': 'https://image.ibb.co/emhGrV/Hypixel-Thumbnail.png',
                    'pages': {
                    }
                }
                if sbProfile:
                    # if not isAllowed(ctx): return await ctx.send('Oops, this feature is still being worked on. Try again later')
                    profileID = SBuser.getProfileByName(sbProfile)
                    SBuser.setProfile(profileID=profileID)
                    members = SBuser.getProfileMembers()
                    myStats = members[SBuser.UUID]
                    rows = dict(await self.bot.pool.fetch('select uuid, username from usernames where uuid=' + ' or uuid='.join([f"'{x}'" for x in members.keys()])))
                    skills = True if "experience_skill_farming" in myStats else False
                    collections = True if "collection" in myStats else False
                    inventory = True if "inv_contents" in myStats else False
                    emb['pages'][str(len(emb['pages']))] = [
                        {'description': f'Skyblock - **{sbProfile}**'},
                        {'name': 'Members', 'value': wrap_by_space(' '.join([( f"**{rows[x]}**" if x == SBuser.UUID else rows[x]
                                                                               ) if x in rows else (await self.UsernameFromUUUID(x)) for x in members.keys() ]), 2)},
                        {'name': 'API Settings', 'value': f'{"**Skills**" if skills else "~~Skills~~"}, '
                                                          f'{"**Collections**" if collections else "~~Collections~~"},\n'
                                                          f'{"**Inventory**" if inventory else "~~Inventory~~"}'},
                        {'name': 'Purse', 'value': validate(myStats, 'coin_purse', decimal=True)},
                        {'name': 'Fairy Souls Collected', 'value': validate(myStats, 'fairy_souls_collected')},
                        # {'name': 'Highest Crit Damage', 'value': validate(myStats.stats, 'highest_crit_damage', decimal=True)},
                        {'name': 'Minions Crafted', 'value': validate(myStats, 'crafted_generators', comma=True)},
                        {'name': 'Objectives', 'value': f"{Counter([x['status'] for x in myStats.objectives.values()])['COMPLETE']}/{len(myStats.objectives)}"},
                        {'name': 'Bosses', 'value': f"Zombie {len(validate(myStats.slayer_bosses['zombie'], 'claimed_levels'))} - `{bossKills(validate(myStats.slayer_bosses, 'zombie'))} kills`\n"
                                                    f"Spider {len(validate(myStats.slayer_bosses['spider'], 'claimed_levels'))} - `{bossKills(validate(myStats.slayer_bosses, 'spider'))} kills`\n"
                                                    f"Wolf {len(validate(myStats.slayer_bosses['wolf'], 'claimed_levels'))} - `{bossKills(validate(myStats.slayer_bosses, 'wolf'))} kills`"
                         } if validate(myStats.slayer_bosses['zombie'], 'claimed_levels') else {},
                        {'name': 'Armor', 'value': ' '.join(SBuser.getArmor()), 'inline': False},
                    ]
                    if skills:
                        skills = await SBuser.getSkills()
                        page = str(len(emb['pages']))
                        emb['pages'][page] = [
                            {'description': f'Skyblock - **Skills**'},
                        ]
                        for skill, level in skills.items():
                            emb['pages'][page].append({
                                'name': f'{skill.title()} {level["level"]}', 'value': f"{level['NextLevel']:,.2f} xp -> lvl {level['level']+1}" if level['NextLevel'] != 0 else f"{level['totalExp']:,.2f}"
                            })
                    if collections:
                        emb['pages'][str(len(emb['pages']))] = [
                            {'description': f'Skyblock - **Collections**'},
                            {'name': 'Farming Collection', 'value': f"Wheat: `{validate(myStats.collection, 'WHEAT', comma=True)}`\n"
                                                                    f"Carrot: `{validate(myStats.collection, 'CARROT_ITEM', comma=True)}`\n"
                                                                    f"Potato: `{validate(myStats.collection, 'POTATO_ITEM', comma=True)}`\n"
                                                                    f"Pumpkin: `{validate(myStats.collection, 'PUMPKIN', comma=True)}`\n"
                                                                    f"Melon: `{validate(myStats.collection, 'MELON', comma=True)}`\n"
                                                                    f"Seeds: `{validate(myStats.collection, 'SEEDS', comma=True)}`\n"
                                                                    f"Mushroom: `{validate(myStats.collection, 'MUSHROOM_COLLECTION', comma=True)}`\n"
                                                                    f"Cocoa Bean: `{validate(myStats.collection, 'INK_SACK:3', comma=True)}`\n"
                                                                    f"Cactus: `{validate(myStats.collection, 'CACTUS', comma=True)}`\n"
                                                                    f"Sugar Cane: `{validate(myStats.collection, 'SUGAR_CANE', comma=True)}`\n"
                                                                    f"Feather: `{validate(myStats.collection, 'FEATHER', comma=True)}`\n"
                                                                    f"Leather: `{validate(myStats.collection, 'LEATHER', comma=True)}`\n"
                                                                    f"Raw Porkchop: `{validate(myStats.collection, 'PORK', comma=True)}`\n"
                                                                    f"Raw Chicken: `{validate(myStats.collection, 'RAW_CHICKEN', comma=True)}`\n"
                                                                    f"Mutton: `{validate(myStats.collection, 'MUTTON', comma=True)}`\n"
                                                                    f"Raw Rabbit: `{validate(myStats.collection, 'RABBIT', comma=True)}`\n"
                                                                    f"Nether Wart: `{validate(myStats.collection, 'NETHER_STALK', comma=True)}`\n"},
                            {'name': 'Mining Collection', 'value': f"Cobblestone: `{validate(myStats.collection, 'COBBLESTONE', comma=True)}`\n"
                                                                   f"Coal: `{validate(myStats.collection, 'COAL', comma=True)}`\n"
                                                                   f"Iron Ingot: `{validate(myStats.collection, 'IRON_INGOT', comma=True)}`\n"
                                                                   f"Gold Ingot: `{validate(myStats.collection, 'GOLD_INGOT', comma=True)}`\n"
                                                                   f"Diamond: `{validate(myStats.collection, 'DIAMOND', comma=True)}`\n"
                                                                   f"Lapis Lazuli: `{validate(myStats.collection, 'INK_SACK:4', comma=True)}`\n"
                                                                   f"Emerald: `{validate(myStats.collection, 'EMERALD', comma=True)}`\n"
                                                                   f"Redstone: `{validate(myStats.collection, 'REDSTONE', comma=True)}`\n"
                                                                   f"Nether Quartz: `{validate(myStats.collection, 'QUARTZ', comma=True)}`\n"
                                                                   f"Obsidian: `{validate(myStats.collection, 'OBSIDIAN', comma=True)}`\n"
                                                                   f"Glowstone Dust: `{validate(myStats.collection, 'GLOWSTONE_DUST', comma=True)}`\n"
                                                                   f"Gravel: `{validate(myStats.collection, 'GRAVEL', comma=True)}`\n"
                                                                   f"Ice: `{validate(myStats.collection, 'ICE', comma=True)}`\n"
                                                                   f"Netherrack: `{validate(myStats.collection, 'NETHERRACK', comma=True)}`\n"
                                                                   f"Sand: `{validate(myStats.collection, 'SAND', comma=True)}`\n"
                                                                   f"End Stone: `{validate(myStats.collection, 'ENDER_STONE', comma=True)}`\n"},
                        ]
                        emb['pages'][str(len(emb['pages']))] = [
                            {'description': f'Skyblock - **Collections**'},
                            {'name': 'Foraging Collection', 'value': f"Oak Wood: `{validate(myStats.collection, 'LOG', comma=True)}`\n"
                                                                     f"Spruce Wood: `{validate(myStats.collection, 'LOG:1', comma=True)}`\n"
                                                                     f"Birch Wood: `{validate(myStats.collection, 'LOG:2', comma=True)}`\n"
                                                                     f"Dark Oak Wood: `{validate(myStats.collection, 'LOG_2:2', comma=True)}`\n"
                                                                     f"Acacia Wood: `{validate(myStats.collection, 'LOG_2', comma=True)}`\n"
                                                                     f"Jungle Wood: `{validate(myStats.collection, 'LOG:3', comma=True)}`\n"},
                            {'name': 'Combat Collection', 'value': f"Rotten Flesh: `{validate(myStats.collection, 'ROTTEN_FLESH', comma=True)}`\n"
                                                                   f"Bone: `{validate(myStats.collection, 'BONE', comma=True)}`\n"
                                                                   f"String: `{validate(myStats.collection, 'STRING', comma=True)}`\n"
                                                                   f"Spider Eye: `{validate(myStats.collection, 'SPIDER_EYE', comma=True)}`\n"
                                                                   f"Gunpowder: `{validate(myStats.collection, 'SULPHUR', comma=True)}`\n"
                                                                   f"Ender Pearl: `{validate(myStats.collection, 'ENDER_PEARL', comma=True)}`\n"
                                                                   f"Ghast Tear: `{validate(myStats.collection, 'GHAST_TEAR', comma=True)}`\n"
                                                                   f"Slimeball: `{validate(myStats.collection, 'SLIME_BALL', comma=True)}`\n"
                                                                   f"Blaze Rod: `{validate(myStats.collection, 'BLAZE_ROD', comma=True)}`\n"
                                                                   f"Magma Cream: `{validate(myStats.collection, 'MAGMA_CREAM', comma=True)}`\n"},
                            {'name': 'Fishing Collection', 'value': f"Raw Fish: `{validate(myStats.collection, 'RAW_FISH', comma=True)}`\n"
                                                                    f"Raw Salmon: `{validate(myStats.collection, 'RAW_FISH:1', comma=True)}`\n"
                                                                    f"Clownfish: `{validate(myStats.collection, 'RAW_FISH:2', comma=True)}`\n"
                                                                    f"Pufferfish: `{validate(myStats.collection, 'RAW_FISH:3', comma=True)}`\n"
                                                                    f"Prismarine Shard: `{validate(myStats.collection, '', comma=True)}`\n"
                                                                    f"Prismarine Crystals: `{validate(myStats.collection, 'PRISMARINE_CRYSTALS', comma=True)}`\n"
                                                                    f"Clay: `{validate(myStats.collection, 'PRISMARINE_SHARD', comma=True)}`\n"
                                                                    f"Lily Pad: `{validate(myStats.collection, 'WATER_LILY', comma=True)}`\n"
                                                                    f"Ink Sack: `{validate(myStats.collection, 'INK_SACK:4', comma=True)}`\n"
                                                                    f"Sponge: `{validate(myStats.collection, 'SPONGE', comma=True)}`\n"}
                        ]
                else:
                    toSort = []
                    for i, profile in enumerate(profiles):
                        profileID = SBuser.getProfileByName(profile)
                        SBuser.setProfile(profileID=profileID)
                        members = SBuser.getProfileMembers()
                        myStats = SBuser.profile.members[SBuser.UUID]
                        skills = True if "experience_skill_farming" in myStats else False
                        collections = True if "collection" in myStats else False
                        inventory = True if "inv_contents" in myStats else False
                        rows = dict(await self.bot.pool.fetch('select uuid, username from usernames where uuid=' + ' or uuid='.join([f"'{x}'" for x in members.keys()])))
                        emb['pages'][str(i)] = [
                            {'description': f'Skyblock - **{profile}** [{profileID}]'},
                            {'name': 'Members', 'value': wrap_by_space(' '.join([(f"**{rows[x]}**" if x == SBuser.UUID else rows[x]
                                                                                  ) if x in rows else (await self.UsernameFromUUUID(x)) for x in members.keys() ]), 2)},
                            {'name': 'API Settings', 'value': f'{"**Skills**" if skills else "~~Skills~~"}, '
                                                              f'{"**Collections**" if collections else "~~Collections~~"},\n'
                                                              f'{"**Inventory**" if inventory else "~~Inventory~~"}'},
                            {'name': 'Purse', 'value': validate(myStats, 'coin_purse', decimal=True)},
                            {'name': 'Fairy Souls Collected', 'value': validate(myStats, 'fairy_souls_collected')},
                            {'name': 'Armor', 'value': ' '.join(SBuser.getArmor()), 'inline': False},
                        ]
                        toSort.append({'last_save': myStats['last_save'] if 'last_save' in myStats else 0, 'page': emb['pages'][str(i)]})
                    for i, profile in enumerate(sorted(toSort, key=lambda k:  -k['last_save'])):
                        emb['pages'][str(i)] = profile['page']
                supporter = await self.bot.pool.fetchrow('select B.phrase from hypixel A, donators B where A.userid = B.userid and A.useruuid=$1', SBuser.UUID)
                if supporter:
                    if supporter['phrase']: emb['embed']['description'] = supporter['phrase']
                    emb['thumbnail'] = 'https://i.ibb.co/MPy1s9P/image.png'
                elif playerRank['rank'] in ['MVP+', 'MVP++', 'Helper', 'Moderator', 'Admin']:
                    if "rankPlusColor" not in SBuser.player.JSON: SBuser.player.JSON["rankPlusColor"] = 'RED'
                    if playerRank['rank'].upper() == 'MVP+': emb['thumbnail'] = self.rank[SBuser.player.JSON["rankPlusColor"]][1]
                    elif playerRank['rank'].upper() == 'MVP++': emb['thumbnail'] = self.rank[SBuser.player.JSON["rankPlusColor"]][2]
                    else: emb['thumbnail'] = self.rank[playerRank['rank'].upper()][1]
                if SBuser.player.JSON["uuid"] in ["9aaad1cac88c4564b95bb18269db19d6"]: emb['thumbnail'] = "https://i.ibb.co/mJ0BTnm/image.png"
                embed = discord.Embed(**emb["embed"])
                embed.set_thumbnail(url=emb["thumbnail"])
                for page in range(len(emb["pages"])):
                    for field in emb["pages"][str(page)]:
                        if 'description' in field:
                            embed.description = field["description"]
                        elif field:
                            embed.add_field(**field)
                    if 'image' in emb:
                        embed.set_image(url=emb["image"])
                    embed.set_footer(text=emb["footer"]["text"], icon_url=emb["footer"]["icon_url"])
                    embeds[page] = embed
                    del embed
                    embed = discord.Embed(**emb["embed"])
                    embed.set_thumbnail(url=emb["thumbnail"])
                time_taken = datetime.datetime.now() - start
                logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
            await self.send(ctx, embeds=embeds)
            await self._discord_account(ctx, SBuser.player.JSON, playerRank["rank"])

    @skyblock.command(case_insensitive=True)
    @commands.check(isAllowed)
    async def test(self, ctx, *, args:str=''):
        split = args.split()
        user = split[0] if len(split) > 0 else None
        sbProfile = split[1] if len(split) > 1 else None
        if user in ['Grapes', 'Peach', 'Mango', 'Papaya', 'Watermelon',
                    'Lemon', 'Cucumber', 'Kiwi', 'Blueberry', 'Raspberry',
                    'Pomegranate', 'Orange', 'Pineapple', 'Zucchini', 'Pear',
                    'Apple', 'Lime', 'Banana', 'Tomato', 'Strawberry', 'Coconut']:
            sbProfile = user
            user = ''
        if ctx.invoked_subcommand is None:
            async with ctx.channel.typing():
                permissions = ctx.channel.permissions_for(ctx.me)
                if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
                if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
                if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
                if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
                    data = await self._get_user(ctx)
                    if not data: return
                    user = data['useruuid']
                try: SBuser = self.bot.hypixel.Skyblock(user)
                except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
                except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
                except self.bot.hypixel.SkyblockNotPlayed: return await ctx.send(f'Looks like {user} never played SkyBlock before.')
                profiles = SBuser.getProfiles()
                playerName = SBuser.player.getName()
                if sbProfile and sbProfile not in profiles: return await ctx.send(f"Looks like {playerName} doesn't have any profile by the name {sbProfile}")
                if not profiles: return await ctx.send(f"Looks like {playerName} doesn't have any SkyBlock profile.")
                if sbProfile:
                    if not isAllowed(ctx): return await ctx.send('Oops, this feature is still being worked on. Try again later')
                    profileID = SBuser.getProfileByName(sbProfile)
                    SBuser.setProfile(profileID=profileID)
                    debug = True
                    test = await SBuser.getStats(debug=debug)
                    if debug:
                        c = Counter()
                        for k in [x for x in test.values()]: c.update(k)
                        test['total'] = dict(c)
                        return await ctx.send('\n'.join([f"{x[0]} -> {x[1]}" for x in test.items()]))
                    return await ctx.send(test)

    @skyblock.command(case_insensitive=True)
    @commands.is_owner()
    async def decompile(self, ctx, user, sbProfile):
        async with ctx.channel.typing():
            permissions = ctx.channel.permissions_for(ctx.me)
            if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
            if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
            if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
            try: SBuser = self.bot.hypixel.Skyblock(user)
            except self.bot.hypixel.PlayerNotFoundException: return await ctx.send(f"Couldn't find the user `{user}`")
            except self.bot.hypixel.HypixelAPIError: return await ctx.send('There seems to be an error with the API. Try again later.')
            except self.bot.hypixel.SkyblockNotPlayed: return await ctx.send(f'Looks like {user} never played SkyBlock before.')
            profiles = SBuser.getProfiles()
            playerName = SBuser.player.getName()
            if sbProfile not in profiles: return await ctx.send(f"Looks like {playerName} doesn't have any profile by the name {sbProfile}")
            if not profiles: return await ctx.send(f"Looks like {playerName} doesn't have any SkyBlock profile.")
            profileID = SBuser.getProfileByName(sbProfile)
            SBuser.setProfile(profileID=profileID)
            myStats = SBuser.profile.members[SBuser.UUID]
            files = []
            for x in myStats:
                try:
                    if 'data' in myStats[x]:
                        file = io.BytesIO()
                        b64 = base64.b64decode(myStats[x]['data'])
                        file.write(b64)
                        file.seek(0)
                        files.append(discord.File(file, f'{x}.nbt'))
                except Exception as error: continue
            await ctx.send(files=files)

    @skyblock.command(aliases=['mb'], case_insensitive=True, hidden=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def magmaboss(self, ctx):
        r = await self.bot.session.get("https://hypixel-api.inventivetalent.org/api/skyblock/bosstimer/magma/estimatedSpawn")
        j = await r.json()
        estimate = human_timedelta(datetime.datetime.utcfromtimestamp(j['estimate'] / 1000))
        em = discord.Embed(title='Magma Boss Timer',
                           description=f"**Boss is spawning**\nin {estimate}",
                           colour=discord.Colour.orange())
        em.set_thumbnail(url="https://gamepedia.cursecdn.com/minecraft_gamepedia/e/ed/Magma_Cube.png")
        em.set_footer(icon_url=self.bot.user.avatar_url, text=self.bot.footer)
        await ctx.send(embed=em)

    @skyblock.command(aliases=['da'], case_insensitive=True, hidden=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def darkauction(self, ctx):
        now = datetime.datetime.utcnow()
        seconds = (datetime.timedelta(hours=24) - (now - now.replace(hour=0, minute=55, second=0, microsecond=0))).total_seconds() % (24 * 3600)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        m = f"{int(m):02d} {'minutes' if m != 1 else 'minute'}{' and ' if s else ''}" if m else ""
        s = f"{int(s):02d} {'seconds' if int(s) != 1 else 'second'}" if m else ""
        em = discord.Embed(title='Dark Auction Timer',
                           description=f"**Dark auction is starting**\nin {m}{s}",
                           color = discord.Colour.orange())
        em.set_thumbnail(url="https://i.ibb.co/nRNjJ8b/body.png")
        em.set_footer(icon_url=self.bot.user.avatar_url, text=self.bot.footer)
        await ctx.send(embed=em)

def setup(bot):
    h = Skyblock(bot)
    bot.add_cog(h)
