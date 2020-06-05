from cogs.utils.mojang import *
from hypixel.utils.functions import *


class Verfiy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = utils(self.bot)
        self.uuid_library = {}

    @commands.command(hidden=True, enabled=False)
    async def HiddenSession(self, ctx, user):
        # if str(ctx.author.id) not in self.bot.voted:
        #     return await ctx.send()
        start1 = datetime.datetime.now()
        permissions = ctx.channel.permissions_for(ctx.me)
        if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
        if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
        if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
        if not permissions.read_message_history: return await ctx.send('Bot does not have permissions to read message history.')
        message = await ctx.send('Gathering information.')
        if user == '' or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
            data = await self.utils._get_user(ctx)
            if not data: return
            user = data['useruuid']
        try: player = self.bot.hypixel.Player(user)
        except self.bot.hypixel.PlayerNotFoundException: return await message.edit(content=f"Couldn't find the user `{user}`")
        except self.bot.hypixel.HypixelAPIError: return await message.edit(content='There seems to be an error with the API. Try again later.')
        except self.bot.hypixel.HypixelAPIThrottle: return await ctx.send('There\'s a global throttle. Try again later.')
        friends = player.getFriends()
        session = player.getSession()
        user = player.getName()
        party = []
        if not session: return await message.edit(content='User is not in a game.')
        for friend in friends['records']:
            if friend['uuidSender'] == player.UUID:
                if friend['uuidReceiver'] in session['players']:
                    party.append(friend['uuidReceiver'])
            elif friend['uuidReceiver'] == player.UUID:
                if friend['uuidSender'] in session['players']:
                    party.append(friend['uuidSender'])
        em = discord.Embed(color=discord.Color.orange(), title=f'{user} is in a{(" " + session["gameType"].title()) if "gameType" in session else "n unknown"} game with:\n​')
        # em.set_footer(text=f'Server: {session["server"]}')
        if party:
            players = []
            start = datetime.datetime.now()
            em.add_field(name='Friends:', value='​')
            for i, player in enumerate(party):
                session['players'].remove(player)
                if player not in self.uuid_library:
                    user = await Mojang(self.bot.session).getUser(uuid=player)
                    if not user: return await ctx.send('There seems to be an error with the Mojang API. Try again later.')
                    self.uuid_library[player] = user
                else:
                    user = self.uuid_library[player]
                players.append(user)
                time_taken = (datetime.datetime.now() - start).total_seconds()
                if time_taken > 1:
                    start = datetime.datetime.now()
                    em.set_field_at(index=0, name='Friends', value=f"`{', '.join(sorted(players, key=lambda x: x.lower()))}`")
                    await message.edit(content=None, embed=em)
            em.set_field_at(index=0, name='Friends', value=f"`{', '.join(sorted(players, key=lambda x: x.lower()))}`")
            await message.edit(content=None, embed=em)
        if session:
            em.add_field(name='Players', value='​')
            await message.edit(content=None, embed=em)
            players = []
            start = datetime.datetime.now()
            for i, player in enumerate(session['players']):
                if player not in self.uuid_library:
                    user = await Mojang(self.bot.session).getUser(uuid=player)
                    if not user: return await ctx.send('There seems to be an error with the Mojang API. Try again later.')
                    self.uuid_library[player] = user
                else:
                    user = self.uuid_library[player]
                players.append(user)
                time_taken = (datetime.datetime.now() - start).total_seconds()
                if time_taken > 1:
                    start = datetime.datetime.now()
                    em.set_field_at(index=0 if not party else 1, name='Players', value=f"`{', '.join(sorted(players, key=lambda x: x.lower()))}`", inline=False)
                    await message.edit(content=None, embed=em)
            em.set_field_at(index=0 if not party else 1, name='Players', value=f"`{', '.join(sorted(players, key=lambda x: x.lower()))}`")
            await message.edit(content=None, embed=em)

        time_taken = datetime.datetime.now() - start1
        logging.info(f'{ctx.message.content} - {time_taken.total_seconds()}s [{ctx.message.author.id}]')


def setup(bot):
    h = Verfiy(bot)
    bot.add_cog(h)
