import datetime
from timeit import default_timer

import requests

from cogs.utils.chat_formatting import *
from hypixel.utils.functions import *


class Verfiy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)

    @commands.command(hidden=True, enabled=False)
    async def HiddenGuild(self, ctx, search):
        msg = await ctx.send('Hypixel doesn\'t let me fetch users from their website so this will take some time.\nThis command is still a Work In Progress, so have patience if it fails.')
        async with ctx.channel.typing():
            start = datetime.datetime.now()
            guildID = None
            permissions = ctx.channel.permissions_for(ctx.me)
            if not permissions.send_messages: return await ctx.author.send(f'I don\'t have permissions to send messages in <#{ctx.channel.id}>')
            if not permissions.embed_links: return await ctx.send('I don\'t have permissions to send embed links.')
            if not permissions.add_reactions: return await ctx.send('I don\'t have permissions to add reactions.')
            if not permissions.read_message_history: return await ctx.send('I don\'t have permissions to read messages history')
            if search == '' or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
                temp_user = await self.utils._get_user(ctx)
                if not temp_user: return
                temp_user = temp_user['useruuid']
                try: temp_player = self.bot.hypixel.Player(temp_user)
                except self.bot.hypixel.HypixelAPIError as error: return await ctx.send('There seems to be an error with the API. Try again later.')
                except self.bot.hypixel.HypixelAPIThrottle: return await ctx.send('There\'s a global throttle. Try again later.')
                guildID = temp_player.getGuildID()
                if not guildID: await ctx.send('Debug: you\'re not in a guild.')
            if len(search) <= 16 and not guildID:
                try:
                    temp_player = self.bot.hypixel.Player(search)
                    guildID = temp_player.getGuildID()
                    if not temp_player.getGuildID(): await ctx.send('Debug: guild ID not found from player')
                except self.bot.hypixel.PlayerNotFoundException: pass
                except Exception as error:
                    await ctx.send('Debug: there was an error executing the code.')
                    print(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
            if not guildID:
                temp_guild = self.bot.hypixel.getJSON('findGuild', byName=search)
                if not temp_guild['guild']: await ctx.send('Debug: guild not found by name.')
                else: guildID = temp_guild['guild']
            if guildID:
                guild = self.bot.hypixel.Guild(guildID)
                guildJSON = guild.JSON
                guildMembers = {}
                rows = dict(await self.bot.pool.fetch('select uuid, username from usernames where uuid=' + ' or uuid='.join([f"'{x['uuid']}'" for x in guildJSON['members']])))
                with requests.Session() as session:
                    total_start_time = default_timer()
                    for m in guildJSON['members']:
                        if m['uuid'] in rows:
                            if m['rank'] in guildMembers: guildMembers[m['rank']].append(rows[m['uuid']])
                            else: guildMembers[m['rank']] = [rows[m['uuid']]]
                            continue
                        user = self.bot.hypixel.UsernameFromUuid(session, m['uuid'])
                        if not user: continue
                        user = user['name']
                        elapsed = default_timer() - total_start_time
                        time_completed_at = "{:5.2f}s".format(elapsed)
                        await self.bot.pool.execute(f"insert into usernames(uuid, username) values('{m['uuid']}', '{user}')")
                        if m['rank'] in guildMembers: guildMembers[m['rank']].append(user)
                        else: guildMembers[m['rank']] = [user]
                try:
                    gLevel = guild.getLevel()
                except KeyError:
                    gLevel = 0
                gName = guild.getName()
                gDescription = guild.getDescription()
                gCreation = guild.createdat()
                embeds = {}
                emb = {
                    'embed': {'title': str(gName),
                              'url': f'https://hypixel.net/guilds/{gName}'.replace(' ', '%20'),
                              'color': discord.Color.green()},
                    'footer': {'text': self.bot.footer,
                               'icon_url': self.bot.user.avatar_url},
                    'pages': {
                        '0': [
                            {'description': gDescription},
                            {'name': 'Guild Master', 'value': guildMembers['GUILDMASTER' if 'GUILDMASTER' in guildMembers else 'Guild Master'][0]}
                            # {'image': gImage if gImage else None},
                        ]
                    }
                }
                page = 0
                # for x in members:
                #     rank = x['rank'].title()
                #     name = x['name']
                #     if [x for x in emb['pages'][str(page)] if 'name' in x and x['name'].startswith(rank)]:
                #         if len(emb['pages'][str(page)][y()]['value'] + f"{escape(name)}, ") >= 500:
                #             page+=1
                #             emb['pages'][str(page)] = [{'name': f'{rank} | Page {page+1}/_last_page', 'value': f"{escape(name)}", 'inline': False}]
                #         emb['pages'][str(page)][y()]['value'] += f", {escape(name)}"
                #     else:
                #         emb['pages']['0'].append({'name': rank, 'value': f"{escape(name)}", 'inline': False})
                if 'ranks' in guildJSON:
                    ranks = guildJSON['ranks']
                    ranks = [r['name'].lower() for r in sorted(ranks, key=lambda x: x['priority'], reverse=True)]
                else:
                    ranks = ['guildmaster', 'officer', 'member']
                totalMembers = 1
                for rank in ranks:
                    for r, members in guildMembers.items():
                        if r.lower() != rank.lower(): continue
                        if r.lower() == 'guildmaster': r = 'Guild Master'
                        emb['pages'][str(page)].append({'name': r.title(), 'value': '', 'inline': False})
                        for member in members:
                            totalMembers += 1
                            if len(emb['pages'][str(page)][-1]['value'] + f"{escape(member)}, ") >= 900:
                                page += 1
                                emb['pages'][str(page)] = [{'name': f'{r.title()} | Page {page + 1}/_last_page', 'value': '', 'inline': False}]
                            emb['pages'][str(page)][-1]['value'] += f"{escape(member)}, "
                        emb['pages'][str(page)][-1]['value'] = emb['pages'][str(page)][-1]['value'][:-2]
                emb['pages']['info'] = [
                    
                    {'name': 'Guild Information',
                                         'value': f"**Name**: {str(gName)}\n"
                                                                               f"**Created**: {gCreation}\n"
                                                                               f"**Members**: {totalMembers}\n"
                                                                               f"**Level**: {gLevel}", 'inline': False}]
                embed = discord.Embed(**emb["embed"])
                for _page in emb["pages"]:
                    for field in emb["pages"][str(_page)]:
                        if not field: continue
                        if 'image' in field:
                            if field['image']: embed.set_image(url=field["image"])
                        elif 'description' in field:
                            if field['description']: embed.description = field['description']
                        else:
                            field['name'] = field['name'].replace('_last_page', str(page + 1))
                            embed.add_field(**field)
                    embed.set_footer(text=emb["footer"]["text"], icon_url=emb["footer"]["icon_url"])
                    embeds[_page] = embed
                    embed = discord.Embed(**emb["embed"])
                # for rank, members in guildMembers.items():
                #     if rank == 'GUILDMASTER': rank = 'Guild Master'
                #     emb['pages'][str(page)].append({'name': rank.title(), 'value': '', 'inline': False})
                #     for member in members:
                #         if len(emb['pages'][str(page)][-1]['value'] + f"{escape(member)}, ") >= 500:
                #             page+=1
                #             emb['pages'][str(page)] = [{'name': f'{rank.title()} | Page {page+1}/_last_page', 'value': '', 'inline': False}]
                #         emb['pages'][str(page)][-1]['value'] += f"{escape(member)}, "
                #     emb['pages'][str(page)][-1]['value'] = emb['pages'][str(page)][-1]['value'][:-2]
                # emb['pages']['info'] = [
                #     {'name': 'Guild Information', 'value': f"**Name**: {str(gName)}\n"
                #                                            f"**Created**: {gCreation}\n"
                #                                            f"**Members**: {sum([len(guildMembers[x]) for x in guildMembers])}\n"
                #                                            f"**Level**: {gLevel}",
                #      'inline': False}
                # ]
            else:
                return await ctx.send(f'Couldn\'t find anything with that name!')
        time_taken = datetime.datetime.now() - start
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        try:
            await msg.delete()
        except Exception:
            pass
        if embeds: await self.utils.send(ctx, embeds=embeds)
        #         xJSON = xguild.JSON
        #         guildMembers = await xguild.getMembers()
        #         try: gLevel = xguild.getLevel()
        #         except KeyError: gLevel = 0
        #         gName = xguild.getName()
        #         gDescription = xguild.getDescription()
        #         gCreation = xguild.createdat()
        #         gImage = await xguild.getGuildBanner()
        #         try: gAchievements = xJSON['achievements']
        #         except KeyError: gAchievements = False
        #         if gDescription and len(gDescription) > 2000: gDescription = '`Description Too Long`'
        #         embeds = {}
        #         emb = {
        #             'embed': {'title': str(gName),
        #                       'url': f'https://hypixel.net/guilds/{gName}'.replace(' ', '%20'),
        #                       'color': discord.Color.green()},
        #             'footer': {'text': self.bot.footer,
        #                        'icon_url': self.bot.user.avatar_url},
        #             'pages': {
        #                 '0': [
        #                     {'description': gDescription},
        #                     {'image': gImage if gImage else None},
        #                 ]
        #             }
        #         }
        #         page = 0
        #         for rank, members in guildMembers.items():
        #             if rank == 'GUILDMASTER': rank = 'Guild Master'
        #             emb['pages'][str(page)].append({'name': rank.title(), 'value': '', 'inline': False})
        #             for member in members:
        #                 if len(emb['pages'][str(page)][-1]['value'] + f"{escape(member)}, ") >= 500:
        #                     page+=1
        #                     emb['pages'][str(page)] = [{'name': f'{rank.title()} | Page {page+1}/_last_page', 'value': '', 'inline': False}]
        #                 emb['pages'][str(page)][-1]['value'] += f"{escape(member)}, "
        #             emb['pages'][str(page)][-1]['value'] = emb['pages'][str(page)][-1]['value'][:-2]
        #         emb['pages']['info'] = [
        #             {'name': 'Guild Information', 'value': f"**Name**: {str(gName)}\n"
        #                                                    f"**Created**: {gCreation}\n"
        #                                                    f"**Members**: {sum([len(guildMembers[x]) for x in guildMembers])}\n"
        #                                                    f"**Level**: {gLevel}",
        #              'inline': False}
        #         ]
        #         if gAchievements:
        #             emb['pages']['info'].append({'name': 'Achievements', 'value': '\n'.join([f"**{x.title().replace('_', ' ')}**: {gAchievements[x]}" for x in gAchievements]), 'inline': False})
        #         embed = discord.Embed(**emb["embed"])
        #         for _page in emb["pages"]:
        #             for field in emb["pages"][str(_page)]:
        #                 if not field: continue
        #                 if 'image' in field:
        #                     if field['image']: embed.set_image(url=field["image"])
        #                 elif 'description' in field:
        #                     if field['description']: embed.description = field['description']
        #                 else:
        #                     field['name'] = field['name'].replace('_last_page', str(page + 1))
        #                     embed.add_field(**field)
        #             embed.set_footer(text=emb["footer"]["text"], icon_url=emb["footer"]["icon_url"])
        #             embeds[_page] = embed
        #             embed = discord.Embed(**emb["embed"])
        #     else: return await ctx.send(f'Couldn\'t find a guild/player with the name {guild}!')
        # time_taken = datetime.datetime.now() - start
        # logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')
        # if embeds: await self.send(ctx, embeds=embeds)


def setup(bot):
    h = Verfiy(bot)
    bot.add_cog(h)
