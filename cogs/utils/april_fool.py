from random import random

hieroglyphics = {'a': 'ᔑ','b': 'ʖ','c': 'ᓵ','d': '↸','e': 'ᒷ','f': '⎓','g': '⊣','h': '⍑','i': '╎','j': '⋮','k': 'ꖌ','l': 'ꖎ','m': 'ᒲ','n': 'リ','o': '𝙹','p': '!¡','q': 'ᑑ','r': '∷','s': 'ᓭ','t': 'ℸ̣','u': '⚍','v': '⍊', 'w': '∴', 'x': '̇/', 'y': '||', 'z': '⨅'}

def magik(text):
    if random() > 0.7: return ''.join(list(map(lambda x: hieroglyphics[x.lower()] if x.lower() in hieroglyphics else x, text)))
    return text

def prank(emb):
    emb['embed']['title'] = magik(emb['embed']['title'])
    emb['footer']['text'] = magik(emb['footer']['text'])
    for p in emb['pages']:
        for f in emb['pages'][p]:
            if f and 'name' in f: f['name'] = magik(f['name'])
    return emb

