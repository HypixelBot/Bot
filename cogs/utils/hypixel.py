""" Simple Hypixel-API in Python, by Snuggle | 2017-09-30 to 2017-10-28 """
import base64
import gzip
import aiohttp
from collections import Counter

import io
from argparse import Namespace

from cogs.utils import jnbt

__version__ = '0.7.4'
# pylint: disable=C0103
# TODO: Add more comments. Explain what's happening!
# TODO: Add API-usage stat-tracking. Like a counter of the number of requests and how many per minute etc.

import cogs.utils.leveling as leveling
from cogs.utils.leaderboard import *
from datetime import datetime
from bs4 import BeautifulSoup
from random import choice
from time import time
import grequests
import logging
import json
import re

log = logging.getLogger(__name__)

cookies = {'__cfduid': 'daaeaf1450d83d155ac7cbb8de5ceae691543011409', '_ga': 'GA1.2.2133704436.1543011417', '_gat_gtag_UA_34641859_1': '1', '_gid': 'GA1.2.1346189589.1543011417', 'cf_clearance': 'b537c87e05567a4f4d039933edd3a20357e9e65f-1543011413-3600-150', 'xfNew_session': '00c3d36348a7f8b81732a0c439a59317'}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}

HYPIXEL_API_URL = 'https://api.hypixel.net/'
UUIDResolverAPI = "https://namemc.com/profile/"

HYPIXEL_API_KEY_LENGTH = 36 # This is the length of a Hypixel-API key. Don't change from 36.
verified_api_keys = []

requestCache = {}
cacheTime = 60

with open('settings/skyblock/items.json') as f: blocksJSON = json.load(f)
with open('settings/skyblock/enchantments.json') as f: enchatmentsJSON = json.load(f)
with open('settings/skyblock/fairy.json') as f: fairyJSON = json.load(f)
with open('settings/skyblock/skills.json') as f: skillsJSON = json.load(f)
with open('settings/skyblock/resources/skills.json') as f: skillResources = json.load(f)
with open('settings/skyblock/resources/slayer.json') as f: slayerJSON = json.load(f)

def noCodes(txt): return re.sub('(§[0-9a-f])', '', txt)

def asyncinit(cls):
    __new__ = cls.__new__

    async def init(obj, *arg, **kwarg):
        await obj.__init__(*arg, **kwarg)
        return obj

    def new(cls, *arg, **kwarg):
        obj = __new__(cls, *arg, **kwarg)
        coro = init(obj, *arg, **kwarg)
        #coro.__init__ = lambda *_1, **_2: None
        return coro

    cls.__new__ = new
    return cls

class PlayerNotFoundException(Exception):
    """ Simple exception if a player/UUID is not found. This exception can usually be ignored.
        You can catch this exception with ``except hypixel.PlayerNotFoundException:`` """
    pass

class GuildIDNotValid(Exception):
    """ Simple exception if a Guild is not found using a GuildID. This exception can usually be ignored.
        You can catch this exception with ``except hypixel.GuildIDNotValid:`` """
    pass

class GuildNotFound(Exception):
    pass

class HypixelAPIError(Exception):
    """ Simple exception if something's gone very wrong and the program can't continue. """
    pass

class HypixelAPIThrottle(Exception):
    pass

class SkyblockNotPlayed(Exception):
    """ Simple exception if a player hasn't played skyblock. This exception can usually be ignored.
        You can catch this exception with ``except hypixel.SkyblockNotPlayed:`` """
    pass

class SkyblockProfileFailed(Exception):
    """ Simple exception if a Skyblock profile is not found. This exception can usually be ignored.
        You can catch this exception with ``except hypixel.SkyblockProfileFailed:`` """
    pass

def getJSON(typeOfRequest, cache=True, **kwargs):
    """ This private function is used for getting JSON from Hypixel's Public API. """
    response = None
    requestEnd = ''
    if typeOfRequest == 'key': api_key = kwargs['key']
    else:
        api_key = choice(verified_api_keys) # Select a random API key from the list available.

        if typeOfRequest == 'player':
            UUIDType = 'uuid'
            uuid = kwargs['uuid']
            if len(uuid) <= 16: UUIDType = 'name' # TODO: I could probably clean this up somehow.

        for name, value in kwargs.items():
            if typeOfRequest == "player" and name == "uuid": name = UUIDType
            requestEnd += f'&{name}={value}'

    cacheURL = HYPIXEL_API_URL + f'{typeOfRequest}?key={"None"}requestEnd{requestEnd}' # TODO: Lowercase
    allURLS = [HYPIXEL_API_URL + f'{typeOfRequest}?key={api_key}{requestEnd}'] # Create request URL.

    # If url exists in request cache, and time hasn't expired...
    if cacheURL in requestCache and requestCache[cacheURL]['cacheTime'] > time(): response = requestCache[cacheURL]['data'] # TODO: Extend cache time
    else:
        requests = (grequests.get(u,  timeout=5) for u in allURLS)
        responses = grequests.imap(requests)
        for r in responses:
            if 'Hypixel | Maintenance' in r.text: raise HypixelAPIError
            try: response = r.json()
            except ValueError: raise HypixelAPIError
    if not response: raise HypixelAPIError(response)
    if response['success'] is False:
        if response['cause'] == 'Global throttle!': raise HypixelAPIThrottle
        raise HypixelAPIError(response)
    if typeOfRequest == 'player':
        if response['player'] is None: raise PlayerNotFoundException(uuid)
    if typeOfRequest != 'key' and cache: # Don't cache key requests.
        requestCache[cacheURL] = {}
        requestCache[cacheURL]['data'] = response
        requestCache[cacheURL]['cacheTime'] = time() + cacheTime # Cache request and clean current cache.
        cleanCache()
    try: return response[typeOfRequest]
    except KeyError: return response

def cleanCache():
    """ This function is occasionally called to clean the cache of any expired objects. """
    itemsToRemove = []
    for item in requestCache:
        try:
            if requestCache[item]['cacheTime'] < time():
                itemsToRemove.append(item)
        except:
            pass
    for item in itemsToRemove:
        requestCache.pop(item)

def setCacheTime(seconds):
    """ This function sets how long the request cache should last, in seconds.

        Parameters
        -----------
        seconds : float
            How long you would like Hypixel-API requests to be cached for.
    """
    try:
        global cacheTime
        cacheTime = float(seconds)
        return f"Cache time has been successfully set to {cacheTime} seconds."
    except ValueError as chainedException:
        raise HypixelAPIError(f"Invalid cache time \"{seconds}\"") from chainedException

def setKeys(api_keys):
    """ This function is used to set your Hypixel API keys.
        It also checks that they are valid/working.

        Raises
        ------
        HypixelAPIError
            If any of the keys are invalid or don't work, this will be raised.

        Parameters
        -----------
        api_keys : list
            A list of the API keys that you would like to use.

            Example: ``['740b8cf8-8aba-f2ed-f7b10119d28']``.
    """
    for api_key in api_keys:
        if len(api_key) == HYPIXEL_API_KEY_LENGTH:
            verified_api_keys.append(api_key)

class Player:
    """ This class represents a player on Hypixel as a single object.
        A player has a UUID, a username, statistics etc.

        Raises
        ------
        PlayerNotFoundException
            If the player cannot be found, this will be raised.

        Parameters
        -----------
        Username/UUID : string
            Either the UUID or the username (Depreciated) for a Minecraft player.

        Attributes
        -----------
        JSON : string
            The raw JSON receieved from the Hypixel API.

        UUID : string
            The player's UUID.
    """

    JSON = None
    UUID = None

    def __init__(self, UUID, cache=True):
        """ This is called whenever someone uses hypixel.Player('Snuggle').
            Get player's UUID, if it's a username. Get Hypixel-API data. """
        self.UUID = UUID
        self.JSON = getJSON('player', cache=cache, uuid=UUID) # Get player's Hypixel-API JSON information.
        if len(UUID) <= 16: # If the UUID isn't actually a UUID... *rolls eyes* Lazy people.
            JSON = self.JSON
            self.UUID = JSON['uuid'] # Pretend that nothing happened and get the UUID from the API.

    def getName(self):
        """ Just return player's name. """
        JSON = self.JSON
        return JSON['displayname']

    def getLevel(self):
        """ This function calls leveling.py to calculate a player's network level. """
        JSON = self.JSON
        try:
            networkExp = JSON['networkExp']
        except KeyError:
            networkExp = 0
        try:
            networkLevel = JSON['networkLevel']
        except KeyError:
            networkLevel = 0
        exp = leveling.Leveling().getExperience(networkExp, networkLevel)
        myoutput = leveling.Leveling().getExactLevel(exp)
        return myoutput

    def getPercentageToNextLevel(self):
        """ This function calls leveling.py to calculate a player's network level percentage. """
        JSON = self.JSON
        try:
            networkExp = JSON['networkExp']
        except KeyError:
            networkExp = 0
        try:
            networkLevel = JSON['networkLevel']
        except KeyError:
            networkLevel = 0
        exp = leveling.Leveling().getExperience(networkExp, networkLevel)
        myoutput = leveling.Leveling().getPercentageToNextLevel(exp)
        return myoutput

    def getMcVersion(self):
        try: return self.JSON['mcVersionRp']
        except: return 'Non'

    def getRank(self):
        """ This function returns a player's rank, from their data. """
        JSON = self.JSON
        playerRank = {'wasStaff': False, 'prefix': None}  # Creating dictionary.
        possibleRankLocations = ['packageRank', 'newPackageRank', 'monthlyPackageRank', 'rank', 'prefix']
        # May need to add support for multiple monthlyPackageRank's in future.

        for Location in possibleRankLocations:
            if Location in JSON:
                if Location == 'rank' and JSON[Location] == 'NORMAL': playerRank['wasStaff'] = True
                elif Location == 'prefix':
                    playerRank['prefix'] = re.sub('§.', '', JSON[Location][3:-1])
                elif JSON[Location].title() == 'None': pass
                else:
                    dirtyRank = JSON[Location].title()
                    dirtyRank = dirtyRank.replace("_", " ").replace("Mvp", "MVP").replace("Vip", "VIP").replace("Superstar", "MVP++") # pylint: disable=line-too-long
                    playerRank['rank'] = dirtyRank.replace(" Plus", "+")

        if 'rank' not in playerRank:
            playerRank['rank'] = 'Non'

        return playerRank

    def getGuildID(self):
        """ This function is used to get a GuildID from a player. """
        UUID = self.UUID
        GuildID = getJSON('findGuild', byUuid=UUID)
        return GuildID['guild']

    def getSession(self):
        """ This function is used to get a player's session information. """
        UUID = self.UUID
        try:
            session = getJSON('status', uuid=UUID)
        except HypixelAPIError:
            session = None
        return session

    def getFriends(self):
        """ This function is used to get player's friends. """
        UUID = self.UUID
        try:
            friends = getJSON('friends', uuid=UUID)
        except HypixelAPIError:
            friends = None
        return friends

    def getGuildName(self):
        GuildID = self.getGuildID()
        if GuildID:
            Guild = getJSON('guild', id = GuildID)
            GuildName = Guild['name']
            return GuildName
        return 'None'

    def getLogin(self):
        firstLogin = datetime.utcfromtimestamp(int(self.JSON['firstLogin']) // 1000) if 'firstLogin' in self.JSON else None
        lastLogin = datetime.utcfromtimestamp(int(self.JSON['lastLogin']) // 1000) if 'lastLogin' in self.JSON else None
        return firstLogin, lastLogin

    def getOnlineStatus(self):
        if 'lastLogin' in self.JSON and 'lastLogout' in self.JSON:
            return self.JSON['lastLogin'] > self.JSON['lastLogout']

class Skyblock:
    """ This class represents a Skyblock player on Hypixel as a single object.
        A Skyblock player has a UUID, a username, statistics etc.

        Raises
        ------
        PlayerNotFoundException
            If the player cannot be found, this will be raised.

        Parameters
        -----------
        Username/UUID : string
            Either the UUID or the username (Depreciated) for a Minecraft player.

        Attributes
        -----------
        JSON : string
            The raw JSON receieved from the Hypixel API.

        UUID : string
            The player's UUID.
    """
    def __init__(self, UUID, cache=True):
        self.UUID = UUID
        self.player = Player(UUID)
        if len(UUID) <= 16: self.UUID = self.player.UUID

        try: self.profiles = self.player.JSON['stats']['SkyBlock']['profiles']
        except KeyError: raise SkyblockNotPlayed(self.UUID)
        if not self.profiles: raise SkyblockNotPlayed(self.UUID)

        self.profileStats = {}

        for x in self.profiles:
            profile = getJSON('skyblock/profile', cache=cache, profile=x)
            if profile['success']:
                self.profileStats[x] = Namespace(**profile['profile'])
            else: raise SkyblockProfileFailed(profile['cause'])

        self.profile = self.profileStats[next(iter(self.profiles.keys()))]

    def setProfile(self, name = None, profileID = None):
        if name: profileID = self.getProfileByName(name)
        self.profile = self.profileStats[profileID]

    def decompile(self, data):
        b64 = base64.b64decode(data)
        bio = io.BytesIO(b64)
        gzf = gzip.GzipFile(fileobj=bio)
        # guff = gzf.read()

        j = jnbt.read(gzf)
        return j

    def getProfileByName(self, name):
        for y in self.profiles.values():
            if y['cute_name'] == name: return y['profile_id']
        return None

    def getProfiles(self):
        return [y['cute_name'] for y in self.profiles.values()]

    def getProfileMembers(self):
        temp = {}
        for p in self.profile.members.items():
            stats = p[1]
            temp[p[0]] = Namespace(**stats)
        return temp

    def getArmor(self):
        player = self.profile.members[self.UUID]

        if 'inv_armor' not in player: return ['Unknown']
        data = player['inv_armor']['data']
        j = self.decompile(data)

        items = []

        for item in j["i"]:
            txt = ''
            if not item: continue
            tag = item['tag'] if 'tag' in item else None
            if tag and 'display' in item['tag']:
                if 'Name' in item['tag']['display']:
                    txt += f"`{noCodes(item['tag']['display']['Name'])}`\n"
                else:
                    txt += f"`{next(filter(lambda x: x['type'] == item['id'], blocksJSON))['name']}`\n"
            # if 'Lore' in item['tag']['display']:
            #     txt += noCodes('\n'.join(item['tag']['display']['Lore']))
            # txt += '\n```'
            else:
                txt += f'x{item["Count"]} '
                txt += f"**{next(filter(lambda x: x['type'] == item['id'], blocksJSON))['name']}**\n"
                if tag and len(item['tag']) > 1 and 'ench' in item['tag']:
                    for ench in item['tag']['ench']:
                        txt += next(filter(lambda x: x['id'] == ench['id'], enchatmentsJSON))['displayName'], ench['lvl']
            items.append(txt)

        return reversed(items) if items else ['Naked']

    async def getSkills(self):
        player = self.profile.members[self.UUID]
        async with aiohttp.ClientSession() as session:
            r = await session.get('https://api.hypixel.net/resources/skyblock/skills')

        async def getLevel(exp, skill):
            skillsJSON = await r.json()
            if skillsJSON['success']:
                try:
                    level = next(filter(lambda y: y['totalExpRequired'] > exp, skillsJSON['collections'][skill.upper()]['levels']))['level'] - 1
                    NextLevel = skillsJSON['collections'][skill.upper()]['levels'][level]['totalExpRequired'] - exp
                except:
                    level = len(skillsJSON['collections'][skill.upper()]['levels'])
                    NextLevel = 0
                return {
                    'level': level,
                    'NextLevel': NextLevel,
                    'totalExp': exp
                }

        skills = {
            x.split('_')[-1].title(): '' for x in player if x.startswith('experience_skill_')
        }
        for skill in skills:
            skills[skill] = await getLevel(player[f'experience_skill_{skill.lower()}'], skill)

        return skills

    async def getStats(self, debug=False):
        player = self.profile.members[self.UUID]

        stats = {
            'Health': 100, 'Defense': 0, 'Strength': 0, 'Speed': 100, 'Crit Chance': 20, 'Crit Damage': 50,
            'Intelligence': 100, 'Attack Speed': 0
        }
        debugStats = {
            'armor': {'Health': 0, 'Defense': 0, 'Strength': 0, 'Speed': 0, 'Crit Chance': 0, 'Crit Damage': 0, 'Intelligence': 0, 'Attack Speed': 0},
            'fairy': {'Health': 100, 'Defense': 0, 'Strength': 0, 'Speed': 100, 'Crit Chance': 20, 'Crit Damage': 50, 'Intelligence': 100, 'Attack Speed': 0},
            'talismans': {'Health': 0, 'Defense': 0, 'Strength': 0, 'Speed': 0, 'Crit Chance': 0, 'Crit Damage': 0, 'Intelligence': 0, 'Attack Speed': 0},
            'skills': {'Health': 0, 'Defense': 0, 'Strength': 0, 'Speed': 0, 'Crit Chance': 0, 'Crit Damage': 0, 'Intelligence': 0, 'Attack Speed': 0},
            'slayer': {'Health': 0, 'Defense': 0, 'Strength': 0, 'Speed': 0, 'Crit Chance': 0, 'Crit Damage': 0, 'Intelligence': 0, 'Attack Speed': 0},
        }
        talismans = {
            'SPEED_TALISMAN': False, 'FIRE_TALISMAN': False, 'INTIMIDATION_TALISMAN': False,
            'GRAVITY_TALISMAN': False, 'RING_POTION_AFFINITY': False, 'LAVA_TALISMAN': False,
            'MAGNETIC_TALISMAN': False, 'SPIDER_TALISMAN': False, 'HEALING_TALISMAN': False,
            'VACCINE_TALISMAN': False, 'BAT_TALISMAN': False, 'FEATHER_ARTIFACT': False,
            'HASTE_RING': False, 'PIGS_FOOT': False, 'NIGHT_CRYSTAL': False,
            'DAY_CRYSTAL': False,  'EXPERIENCE_ARTIFACT': False,
            'ENDER_ARTIFACT': False, 'BAT_ARTIFACT': False,  'CANDY_ARTIFACT': False,
            'ARTIFACT_POTION_AFFINITY': False, 'FISH_AFFINITY_TALISMAN': False, 'SPIDER_RING': False,
            'SEA_CREATURE_ARTIFACT': False, 'ZOMBIE_RING': False, 'HEALING_RING': False,
            'FARMER_ORB': False, 'RED_CLAW_TALISMAN': False, 'WOOD_TALISMAN': False,
            'SCAVENGER_TALISMAN': False, 'SKELETON_TALISMAN': False, 'WOLF_TALISMAN': False,
            'ETERNAL_CRYSTAL': False, 'BAT_RING': False, 'SPIDER_ARTIFACT': False,
            'TARANTULA_TALISMAN': False, 'RED_CLAW_ARTIFACT': False, 'CANDY_RING': False,
            'ZOMBIE_ARTIFACT': False, 'BAIT_RING': False, 'DEVOUR_RING': False,
            'HUNTER_RING': False, 'RED_CLAW_RING': False,
        }
        def calcStatsFromLore(j, _stats = stats):
            crystal = False
            for item in j['i']:
                if not item: continue
                tag = item['tag'] if 'tag' in item else None
                if tag and 'display' in item['tag']:
                    itemID = tag['ExtraAttributes']['id']
                    # if itemID not in talismans: print(itemID)
                    if 'Lore' in item['tag']['display']:
                        for x in item['tag']['display']['Lore']:
                            txt = noCodes(x)
                            if any([txt.startswith(x) for x in _stats]):
                                txt = txt.split(':')
                                stat = txt[0]
                                amount = int(txt[1].split()[0].replace('%', ''))
                                _stats[stat] += amount

                if 'ExtraAttributes' in tag:
                    ID = tag['ExtraAttributes']['id']
                    if ID in ['NIGHT_CRYSTAL', 'DAY_CRYSTAL'] and not crystal: _stats['Strength'] +=5; _stats['Defense'] +=5; crystal = True
                    if ID == 'SPEED_TALISMAN': _stats['Speed'] +=2
        calcFairyStats = lambda a, b: sum([int(x[a]) for x in fairyJSON if x['fairy_exchanges'] < b])
        def getSkillStats(skill, _stats = stats):
            if not str(skills[skill]['level']).isdigit(): return
            for lvl in skillResources['collections'][skill.upper()]['levels'][:skills[skill]['level']]:
                a = next(filter(lambda v: v.startswith('+') and 'coin' not in v.lower(), lvl['unlocks'])).split()
                if 'Crit' in a: sName = 'Crit ' + a[-1]
                else: sName = a[-1]
                if sName in _stats: _stats[sName] += int(a[0].replace('%', ''))
                else: _stats[sName] = int(a[0].replace('%', ''))

        #Armor#
        if 'inv_armor' not in player: return ['Unknown']
        data = player['inv_armor']['data']
        j = self.decompile(data)
        calcStatsFromLore(j, _stats=debugStats['armor'] if debug else stats)

        #Talisman#
        if 'talisman_bag' not in player: return ['unknown']
        data = player['talisman_bag']['data']
        j = self.decompile(data)
        calcStatsFromLore(j, _stats=debugStats['talismans'] if debug else stats)

        #Fairy Souls#
        for x in stats:
            try:
                if debug: debugStats['fairy'][x] += calcFairyStats(x, player['fairy_exchanges'])
                else: stats[x] += calcFairyStats(x, player['fairy_exchanges'])
            except Exception: continue

        #Skills#
        skills = await self.getSkills()
        for x in skills: getSkillStats(x, _stats=debugStats['skills'] if debug else stats)

        #Slayer#
        bosses = player['slayer_bosses']
        for boss in bosses:
            if 'claimed_levels' in bosses[boss]:
                for level, claimed in bosses[boss]['claimed_levels'].items():
                    try:
                        for x in slayerJSON[boss][level]:
                            if debug: debugStats['slayer'][x] += slayerJSON[boss][level][x]
                            else: stats[x] += slayerJSON[boss][level][x]
                    except: continue
        if debug: return debugStats
        return stats

class Guild:
    """ This class represents a guild on Hypixel as a single object.
        A guild has a name, members etc.

        Parameters
        -----------
        GuildID : string
            The ID for a Guild. This can be found by using :class:`Player.getGuildID()`.


        Attributes
        -----------
        JSON : string
            The raw JSON receieved from the Hypixel API.

        GuildID : string
            The Guild's GuildID.

    """
    JSON = None
    GuildID = None
    def __init__(self, GuildID):
        self.BASE_URL = "https://hypixel.net/"
        # self.session = session
        try:
            if len(GuildID) == 24:
                self.GuildID = GuildID
                self.JSON = getJSON('guild', id=GuildID)
        except Exception as chainedException:
            raise GuildIDNotValid(GuildID) from chainedException

    def getLevel(self): return leveling.GuildLevelUtil().getLevel(self.JSON['exp'])

    def getDescription(self):
        if 'description' in self.JSON: return self.JSON['description']
        else: return 'No description provided.'

    def getName(self): return self.JSON['name']

    def createdat(self):
        return datetime.utcfromtimestamp(self.JSON['created']/1000.0).strftime("%Y-%m-%d %H:%M:%S")

    async def getGuildBanner(self):
        r = await self.session.get(f'{self.BASE_URL}/guilds/{self.JSON["_id"]}/')
        soup = BeautifulSoup(await r.content.read(), 'lxml').find_all(class_="guildHeader ")
        for item in soup:
            return f"{self.BASE_URL}{item.get('style')[23:-3]}" if 'default' not in item.get('style')[23:-3] else None

class Leaderboards:
    JSON = None
    def __init__(self):
        self.JSON = getJSON('leaderboards')

    def Arena(self):
        return ARENA(self.JSON)

    def Battleground(self):
        return BATTLEGROUND(self.JSON)

    def Bedwars(self):
        return BEDWARS(self.JSON)

    def Gingerbread(self):
        return GINGERBREAD(self.JSON)

    def mcgo(self):
        return MCGO(self.JSON)

    def MurderMystery(self):
        return MURDER_MYSTERY(self.JSON)

    def Paintball(self):
        return PAINTBALL(self.JSON)

    def Prototype(self):
        return PROTOTYPE(self.JSON)

    def Quakecraft(self):
        return QUAKECRAFT(self.JSON)

    def Skyclash(self):
        return SKYCLASH(self.JSON)

    def Skywars(self):
        return SKYWARS(self.JSON)

    def Speeduhc(self):
        return SPEED_UHC(self.JSON)

    def SuperSmash(self):
        return SUPER_SMASH(self.JSON)

    def SurvivalGames(self):
        return SURVIVAL_GAMES(self.JSON)

    def TnTGames(self):
        return TNTGAMES(self.JSON)

    def TrueCombat(self):
        return TRUE_COMBAT(self.JSON)

    def uhc(self):
        return UHC(self.JSON)

    def VampireZ(self):
        return VAMPIREZ(self.JSON)

    def Walls(self):
        return WALLS(self.JSON)

    def Walls3(self):
        return WALLS3(self.JSON)

def GetUsers(members):
    allURLS = []
    URLStoRequest = []
    memberList = []
    for member in members:  # For each member, use the API to get their username.
        if UUIDResolverAPI + member in requestCache:
            allURLS.append(requestCache[UUIDResolverAPI + member])
        else:
            allURLS.append(UUIDResolverAPI + member)
            URLStoRequest.append(UUIDResolverAPI + member)
    requests = (grequests.get(u) for u in URLStoRequest)
    responses = grequests.map(requests)
    i = 0
    for uindex, user in enumerate(allURLS):
        try:
            if user.startswith(UUIDResolverAPI):
                allURLS[uindex] = {'content': responses[i].content, 'uuid': user.split('/')[-1]}
                i += 1
        except AttributeError:
            pass
        except json.JSONDecodeError:
            pass
    for name in allURLS:
        if type(name) != str:
            soup = BeautifulSoup(name['content'], 'lxml')
            for link in soup.find_all('a'):
                item = link.get('href')
                if 'mine.ly' in item:
                    memberList.append(item[16:].split('.')[0])
                    requestCache[UUIDResolverAPI + name['uuid']] = item[16:].split('.')[0]
        else:
            memberList.append(name)
    return memberList

uuidCache = []

def UsernameFromUuid(session, uuid):
    base_url = "https://sessionserver.mojang.com/session/minecraft/profile/"
    x = list(filter(lambda n: n.get('id') == uuid.replace('-', ''), uuidCache))
    if len(x) == 1:
        return x[0]
    with session.get(base_url + uuid) as response:
        data = response.json()
        if response.status_code != 200:
            print("FAILURE::{0}".format(base_url + uuid))
        # Return .csv data for future consumption
        uuidCache.append(data)
        return data
