# from PIL import Image, ImageDraw, ImageFont
# from io import BytesIO
import random
import json
import aiohttp
from urllib.parse import quote as uriquote

try:
    from lxml import etree
except ImportError:
    from bs4 import BeautifulSoup
from urllib.parse import parse_qs, quote_plus

def rainbow():
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    return color

def get_fmt(d, h, m, s):
    msg = ''
    day = 'days' if d > 1 else 'day'
    hour = 'hours' if h > 1 else 'hour'
    minute = 'minutes' if m > 1 else 'minute'
    second = 'seconds' if s > 1 else 'second'
    if d != 0: msg += f'{d} {day},'
    if h != 0: msg += f'{h} {hour},'
    if m != 0: msg += f'{m} {minute},'
    if s != 0: msg += f'{s} {second},'
    msg = msg.split(',')
    msg.remove('')
    return msg

# def _banner(thumbnail, address, motd, players):
#     file = BytesIO()
#     canvas = Image.new('RGBA', (560, 95), (255, 255, 255, 0))
#     font = ImageFont.truetype('settings/cheeseusauceu.ttf', 25)
#     font_small = ImageFont.truetype('settings/cheeseusauceu.ttf', 20)
#
#     if thumbnail: thumbnail = Image.open(thumbnail)
#     else: thumbnail = Image.open('thumbnails/unknown_server.png')
#
#     canvas_w, canvas_h = canvas.size
#     thumbnail_w, thumbnail_h = thumbnail.size
#
#     offset = int(15), int((canvas_h - thumbnail_h) / 2)
#     try: canvas.paste(thumbnail, offset, mask=thumbnail)
#     except: canvas.paste(thumbnail, offset)
#
#     draw = ImageDraw.Draw(canvas)  # Starts Drawing on background
#
#     draw.text((thumbnail_w + 30, thumbnail_h - thumbnail_h * 0.9), f'{address}', font=font, fill='white')  # Server ip
#
#     draw.text((thumbnail_w + 30, thumbnail_h - thumbnail_h * 0.45), f'{motd.title()}', font=font_small, fill='white')  # Motd
#
#     draw.text((thumbnail_w + 30, thumbnail_h - thumbnail_h * 0.05), f'{players} Players', font=font_small, fill='white')  # Players
#  # Pastes favicon
#
#     canvas.save(file, 'PNG')
#     file.seek(0)
#     return file

def find_all(predicate, seq):
    elements = []
    for element in seq:
        if predicate(element):
            elements.append(element)
    if elements: return elements
    return None

async def get_google_entries(query, session=None):
    if not session:
        session = aiohttp.ClientSession()
    url = 'https://www.google.com/search?q={}'.format(uriquote(query))
    params = {
        'safe': 'off',
        'lr': 'lang_en',
        'h1': 'en'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
    }
    entries = []
    async with session.get(url, params=params, headers=headers) as resp:
        if resp.status != 200:
            async with session.get("https://www.googleapis.com/customsearch/v1?q=" + quote_plus(query) + "&start=" + '1' + "&key=AIzaSyC7TI8bLA8j5EIZi_DAbCzzneh2S4zTvks&cx=011960534013073771649:wdlshrj29vi") as resp:
                result = json.loads(await resp.text())
            return None, result['items'][0]['link']

        try:
            root = etree.fromstring(await resp.text(), etree.HTMLParser())
            search_nodes = root.findall(".//div[@class='g']")
            for node in search_nodes:
                url_node = node.find('.//h3/a')
                if url_node is None:
                    continue
                url = url_node.attrib['href']
                if not url.startswith('/url?'):
                    continue
                url = parse_qs(url[5:])['q'][0]
                entries.append(url)
        except NameError:
            root = BeautifulSoup(await resp.text(), 'html.parser')
            for result in root.find_all("div", class_='g'):
                url_node = result.find('h3')
                if url_node:
                    for link in url_node.find_all('a', href=True):
                        url = link['href']
                        if not url.startswith('/url?'):
                            continue
                        url = parse_qs(url[5:])['q'][0]
                        entries.append(url)
    return entries, root

def getRank(json):
    """ This function returns a player's rank, from their data. """
    JSON = json
    playerRank = {'wasStaff': False}  # Creating dictionary.
    possibleRankLocations = ['packageRank', 'newPackageRank', 'monthlyPackageRank', 'rank']
    # May need to add support for multiple monthlyPackageRank's in future.

    for Location in possibleRankLocations:
        if Location in JSON:
            if Location == 'rank' and JSON[Location] == 'NORMAL':
                playerRank['wasStaff'] = True
            elif JSON[Location].title() == 'None':
                pass
            else:
                dirtyRank = JSON[Location].title()
                dirtyRank = dirtyRank.replace("_", " ").replace("Mvp", "MVP").replace("Vip", "VIP").replace("Superstar", "MVP++")  # pylint: disable=line-too-long
                playerRank['rank'] = dirtyRank.replace(" Plus", "+")

    if 'rank' not in playerRank:
        playerRank['rank'] = 'Non'

    return playerRank
