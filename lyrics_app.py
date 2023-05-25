from json import loads
from pprint import pprint

from py_rpautom.python_utils import cls, ler_variavel_ambiente, remover_acentos
from requests import get

cls()
token_lyrics_app = ler_variavel_ambiente(
    nome_variavel='token_lyrics_app',
    variavel_sistema=True,
)
header = {'Authorization': f'Bearer {token_lyrics_app}'}

artist = 'Vanessa Carlton'
music = 'Pretty Baby'

url_base = 'https://api.genius.com/'
endpoint = f'search?q={artist.upper()}'

data1 = loads(get(url=''.join((url_base, endpoint)), headers=header).content)

artist_id = ''
for response in data1['response']['hits']:
    try:
        infobox1 = {
            'artist_name': response['result']['primary_artist']['name'],
            'artist_id': response['result']['primary_artist']['id'],
            'full_title': response['result']['full_title'],
        }

        if infobox1['artist_name'].upper() == artist.upper():
            artist_id = infobox1['artist_id']
            break
    except:
        ...

page_number = 1
# artists/8568/songs?page=30
next_page = None
validation_title = False
title_song = ''
while not next_page == 'null':
    print('next_page:', page_number)
    endpoint = f'artists/{artist_id}/songs?page={page_number}'
    data2 = loads(
        get(
            url=''.join((url_base, endpoint, '/songs')), headers=header
        ).content
    )
    next_page = data2['response']['next_page']

    if next_page is None:
        next_page = 'null'
        continue

    page_number = next_page

    for response in data2['response']['songs']:
        try:
            infobox2 = {
                'title': response['title'],
                'url': ''
            }

            if (
                remover_acentos(infobox2['title'].upper())
                == remover_acentos(music).upper()
            ):
                title_song = infobox2['title']
                infobox2['url'] = response['url']
                validation_title = True
                break

        except:
            ...
    if validation_title is True:
        break

if (next_page == 'null') and (title_song == ''):
    raise SystemError(
        'Não foi possível localizar a música solicitada.'
    )

html_content = get(infobox2['url'])

validation_show = False
validation_number = 0
skiping_list = [
    b'",{',
    b'"tag',
    b'":',
    b'"br',
    b'"},',
    b'/a><br>',
    b'',
    b'"html',
    b'"body',
    b'"data',
    b'":{',
    b'"name',
    b'"inread-ad',
    b'"p',
    b'"',
    b"'",
    b'desktop_',
    b'"root',
    b'"],',
    b'"},{',
    b'"a',
    b'"href',
    b'"attributes',
    b'"id',
    b'"pending',
    b'"editorialState',
    b'"unreviewed',
    b'",',
    b'"classification',
    b'":[',
    b'":[{',
    b'"children',
    b'" data-id=',
    b'"17777149',
    b'n<a href=',
    b'n<a href=',
]

infobox3 = {
    'artist_name': infobox1['artist_name'],
    'title': infobox2['title']
}

lyrics_content = []
for item in b''.join(html_content.content.splitlines()).split(b'\\'):
    if item.__contains__(b'"body') and validation_number < 1:
        validation_number = validation_number + 1
        validation_show = True

    if item.__contains__(b'lyricsPlaceholderReason'):
        validation_show = False

    if validation_show is True and item not in skiping_list:
        lyrics_content.append(item)
        ...

print(infobox3['artist_name'])
print(infobox3['title'], '\n')

[print(verse.decode(encoding='utf8')) for verse in lyrics_content]
