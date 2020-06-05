from cogs.utils.mojang import *
from cogs.utils.chat_formatting import *
from cogs.utils.paginator import Pages
from cogs.utils.checks import *
from string import punctuation
from cogs.utils import misc
from io import BytesIO
from time import time
# from PIL import Image
import logging
import discord
import base64
import re

punctuation = punctuation.replace('_', '')

log = logging.getLogger(__name__)

# noinspection PyUnboundLocalVariable
class Minecraft(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.Mojang_username = 'https://api.mojang.com/users/profiles/minecraft/{username}'
		self.Mojang_history = 'https://api.mojang.com/user/profiles/{uuid}/names'
		self.MinecraftAvatar = 'https://avatar.yourminecraftservers.com/avatar/{background}/{not_found_mode}/{figure}/{size}/{nick}.png'
		self.requestCache = {}
		self.disabled_users = ['9aaad1cac88c4564b95bb18269db19d6']
		self.servers = {'hypixel': 'mc.hypixel.net',
						'mineplex': 'mineplex.com'}
		self.cacheTime = 60

	def cleanCache(self):
		""" This function is occasionally called to clean the cache of any expired objects. """
		itemsToRemove = []
		for item in self.requestCache:
			try:
				if self.requestCache[item]['cacheTime'] < time():
					itemsToRemove.append(item)
			except:
				pass
		for item in itemsToRemove:
			self.requestCache.pop(item)

	async def cog_before_invoke(self, ctx):
		# try: await ctx.message.delete()
		# except: pass
		await ctx.trigger_typing()
		permissions = ctx.channel.permissions_for(ctx.me)
		if not permissions.send_messages:
			return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')

	async def _get_user(self, ctx):
		mention = True
		if ctx.message.mentions:
			author = ctx.message.mentions[0]
		else:
			author = ctx.message.author
			mention = False
		data = await self.bot.pool.fetchrow('select * from hypixel where userid=$1', author.id)
		if data:
			return data[1], data[0], True
		if mention:
			await ctx.send('That user doesn\'t seem to have their minecraft account associated')
			return None, None, None
		else:
			await ctx.send_help(ctx.command)
			return None, None, None

	@commands.command('history')
	@commands.cooldown(rate=5, per=60, type=commands.BucketType.user)
	async def _history(self, ctx, user: str = None):
		"""Gives you the name history of a player"""
		permissions = ctx.channel.permissions_for(ctx.me)
		if not permissions.send_messages: return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
		if not permissions.embed_links: return await ctx.send('Bot does not have embed links permission.')
		if not permissions.add_reactions: return await ctx.send('Bot does not have add reactions permission.')
		if user and any(char in user for char in punctuation) and not ctx.message.mentions: return await ctx.send('Illegal characters used.', delete_after=20)
		uuid = False
		if user and len(user.replace('-', '')) == 32:
			uuid = True
		if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
			user, member, uuid = await self._get_user(ctx)
			if not user:
				return
		if uuid:
			if self.Mojang_history.format(uuid = user) in self.requestCache: r = self.requestCache[self.Mojang_history.format(uuid = user)]
			else:
				response = await self.bot.session.get(self.Mojang_history.format(uuid = user))
				if not(str(response.status).startswith('2')) and response.reason != 'OK': return await ctx.send('Service is not working.')
				elif str(response.status).startswith('2'):
					if response.reason == 'No Content': return await ctx.send('That user doesn\'t exist.')
					r = await response.json()
					response.close()
					self.requestCache[self.Mojang_history.format(uuid = user)] = r
			users=[escape(m['name']) for m in reversed(r)]
			users[0] = f"**{users[0]}**"
			p = Pages(ctx = ctx, entries = users, per_page = 20)
			p.embed.title = f'{users[0]} past names'
			p.embed.colour = 0x738bd7
			await p.paginate()

		if not uuid:
			if not user: return await ctx.send('Cannot search for a player if none is given.')
			if self.Mojang_username.format(username=user) in self.requestCache:
				response = self.requestCache[self.Mojang_username.format(username=user)]
				cached = True
			else:
				response = await self.bot.session.get(self.Mojang_username.format(username=user))
				cached = False
			if not cached and not (str(response.status).startswith('2')) and response.reason != 'OK':
				return await ctx.send('Service is not working.')
			elif cached or str(response.status).startswith('2'):
				if not cached and response.reason == 'No Content':
					return await ctx.send('That user doesn\'t exist.')
				r1 = await response.json() if not cached else response
				self.requestCache[self.Mojang_username.format(username=user)] = r1
				if self.Mojang_history.format(uuid=r1['id']) in self.requestCache:
					response = self.requestCache[self.Mojang_history.format(uuid=r1['id'])]
					cached = True
				else:
					if not cached: response.close()
					response = await self.bot.session.get(self.Mojang_history.format(uuid=r1['id']))
					cached = False
				if not cached and not (str(response.status).startswith('2')) and response.reason != 'OK':
					return await ctx.send('Service is not working.')
				r2 = await response.json() if not cached else response
				if not cached: response.close()
				self.requestCache[self.Mojang_history.format(uuid=r1['id'])] = r2
				users=[escape(m['name']) for m in reversed(r2)]
				users[0] = f"**{users[0]}**"
				p = Pages(ctx = ctx, entries = users, per_page = 20)
				p.embed.title = f'{user} past names'
				p.embed.colour = 0x738bd7
				await p.paginate()

	@commands.command('skin')
	@commands.cooldown(rate=5, per=60, type=commands.BucketType.user)
	async def _skin(self, ctx, user: str = None):
		"""Displays someone's skin"""
		permissions = ctx.channel.permissions_for(ctx.me)
		if not permissions.embed_links:
			return await ctx.send('Bot does not have embed links permission.')
		if user and any(char in user for char in punctuation) and not ctx.message.mentions: return await ctx.send('Illegal characters used.', delete_after=20)
		uuid = False
		if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
			user, member, uuid = await self._get_user(ctx)
			if not user:
				return

		if len(user) == 32:
			uuid = True
		try:
			if uuid:
				em = discord.Embed()
				em.title = 'Click me to get the raw skin image'
				em.url = f'https://visage.surgeplay.com/skin/{user}'
				em.set_thumbnail(url = f'https://visage.surgeplay.com/head/64/{user}')
				em.set_image(url = f'https://visage.surgeplay.com/full/256/{user}')
				return await ctx.send(embed = em)
			if not uuid:
				if not user: return await ctx.send('Cannot search for a player if none is given.')
				mojang_response = await Mojang(self.bot.session).getUUID(user)
				if not mojang_response['code'].startswith('2') and mojang_response['reason'] != 'OK':
					return await ctx.send('Service is not working.')
				elif mojang_response['code'].startswith('2'):
					if mojang_response['reason'] == 'No Content': return await ctx.send('That user doesn\'t exist.')
					em = discord.Embed()
					em.title='Click me to get the raw skin image'
					em.url = f'https://visage.surgeplay.com/skin/{mojang_response["uuid"]}'
					em.set_thumbnail(url = f'https://visage.surgeplay.com/head/64/{mojang_response["uuid"]}')
					em.set_image(url = f'https://visage.surgeplay.com/full/256/{mojang_response["uuid"]}')
					await ctx.send(embed=em)
		except KeyError:
			em = discord.Embed(description = 'Couldn\'t find anyone with that username.')
			em.set_footer(text = self.bot.footer, icon_url = self.bot.user.avatar_url)
			await ctx.send(embed = em, delete_after = 10)

	@commands.command('uuid')
	@commands.cooldown(rate=5, per=60, type=commands.BucketType.user)
	async def _uuid(self, ctx, user: str = None):
		"""Want to know someone\'s uuid?"""
		if user and any(char in user for char in punctuation) and not ctx.message.mentions: return await ctx.send('Illegal characters used.', delete_after=20)
		if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
			user, member, uuid = await self._get_user(ctx)
			if uuid: return await ctx.send(f'{self.bot.get_user(member)}\'s uuid is `{user}`')
			if not user: return
		if not user: return await ctx.send('Cannot search for a player if none is given.')
		response = await Mojang(self.bot.session).getUUID(user)
		if not response['code'].startswith('2') and response['reason'] != 'OK':
			return await ctx.send('Service is not working.')
		elif response['code'].startswith('2'):
			if response['reason'] == 'No Content': return await ctx.send('That user doesn\'t exist.')
			if response['uuid']: return await ctx.send(f'{response["name"]}\'s uuid is `{response["uuid"]}`')

	# @commands.command('minime')
	# @commands.is_owner()
	# @commands.cooldown(rate=5, per=60, type=commands.BucketType.user)
	# async def _minime(self, ctx, user: str = None):
	# 	"""Gives a minime of your minecraft skin."""
	# 	permissions = ctx.channel.permissions_for(ctx.me)
	# 	if not permissions.embed_links:
	# 		return await ctx.author.send(f'The bot doesn\'t have permissions to send messages in <#{ctx.channel.id}>')
	# 	if not permissions.attach_files:
	# 		return await ctx.send('Bot does not have permissions to send files.')
	# 	return await ctx.send('This service is currently not working.', delete_after=10)
	# 	if user and any(char in user for char in punctuation) and not ctx.message.mentions: return await ctx.send('Illegal characters used.', delete_after=20)
	# 	if not user or ctx.message.mentions and ctx.message.mentions[0].id != self.bot.user.id:
	# 		user, member, uuid = await self._get_user(ctx)
	# 		if uuid:
	# 			response = requests.get(self.Mojang_history.format(uuid=user))
	# 			if response.status_code != 204:
	# 				users = [escape(m['name']) for m in reversed(response.json())]
	# 				user = users[0]
	# 		if not user: return
	# 	print(user)
	# 	url = self.MinecraftAvatar.format(background='trnsp', not_found_mode='not_found', figure='classic', size='128', nick=user)
	# 	response = requests.get(url)
	# 	if response.reason == 'OK':
	# 		file = BytesIO()
	# 		Image.open(BytesIO(response.content)).save(file, format='PNG')
	# 		file.seek(0)
	# 		await ctx.send(file = discord.File(file, f'{user}.png'))
	# 	else:
	# 		await ctx.send('Couldn\'t find that user.', delete_after=20)
    #
	# @_minime.error
	# async def _minime_error(self, ctx, error):
	# 	if isinstance(error, commands.errors.CommandOnCooldown):
	# 		if str(ctx.author.id) in self.bot.voted: return await ctx.reinvoke()
	# 		else: return await ctx.send(f'You can use this command again in {int(error.retry_after):.1f} seconds.\nOr you can upvote to remove the cooldown `h!upvote`')
	# 	elif isinstance(error, commands.errors.MissingRequiredArgument):
	# 		return await self.bot.formatter.format_help_for(ctx, ctx.command, delete_after=25)
	# 	else:
	# 		await ctx.send('Oops, something went wrong. The error has been sent to my owner.')
	# 		trace = traceback.format_exception(type(error), error, error.__traceback__)
	# 		return logging.error(f'Guild: {ctx.guild.name} | {ctx.guild.id}\n'
     #                                                              f'Users: {ctx.author} | {ctx.author.id}\n'
     #                                                              f'Command: {ctx.message.content}\n'
     #                                                              f'```{"".join(trace)}```')

	# @commands.command('server')
	# @commands.cooldown(rate=5, per=60, type=commands.BucketType.user)
	# async def _server(self, ctx, server: str):
	# 	async with ctx.typing():
	# 		permissions = ctx.channel.permissions_for(ctx.me)
	# 		if not permissions.attach_files:
	# 			return await ctx.send('Bot does not have permissions to send files.')
	# 		if server in self.servers:
	# 			server = self.servers[server]
	# 		address = server
	# 		server = MinecraftServer.lookup(server)
	# 		try: status = server.status()
	# 		except: return await ctx.send(f'Failed to gather information about requested server.')
	# 		if type(status.description) is str: pattern1, pattern2 = '^\s+', '§[a-f0-9lonmkr]'; description = re.sub(pattern1, '', re.sub(pattern2, '', status.description))
	# 		elif 'text' in status.description and len(status.description['text']) > 5: pattern1, pattern2 = '^\s+', '§[a-f0-9lonmkr]'; description = re.sub(pattern1, '', re.sub(pattern2, '', status.description['text']))
	# 		elif 'extra' in status.description: description = ''.join([m['text'] for m in status.description['extra']])
	# 		else: description = ''
	# 		motd = re.sub("\n.+", '', description)
	# 		players = f'{status.players.online:,}/{status.players.max:,}'
	# 		file1 = BytesIO()
	# 		data = None
	# 		if status.favicon:
	# 			data = status.favicon.split('base64,')[1]
	# 			Image.open(BytesIO(base64.b64decode(data))).save(file1, format='PNG')
	# 			file1.seek(0)
	# 		if not data: file1 = None
	# 		banner = discord.File(misc._banner(file1, address, motd, players), 'banner.png')
	# 		await ctx.send(file=banner)

def setup(bot):
	bot.add_cog(Minecraft(bot))
