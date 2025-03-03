from pprint import pprint

from py_rpautom.python_utils import (
    cls,
    ler_variavel_ambiente,
    remover_acentos
)
from requests import get


def api_error_validation(
    base_data: dict[str, str],
) -> tuple[str, str]:
    error_description = base_data.get('error_description')
    error = base_data.get('error')
    return (
        error,
        error_description,
    )


def clean_data(data: str) -> str:
    import re

    pattern = re.compile(r"[^\w\s\s]")
    pattern = re.compile(r'[^\w]')
    data_cleaned = pattern.sub('', data)
    return data_cleaned


def format_lyrics_content(lyrics_content: list[str],):
    new_lyrics_content = []

    for lyrics_content_count, line in enumerate(lyrics_content):
        if lyrics_content[lyrics_content_count].startswith('(') \
        or lyrics_content[lyrics_content_count].startswith('['):
            new_lyrics_content.append('')

        new_lyrics_content.append(line)

    return new_lyrics_content


def get_api_auth_bearer(
    env_var_name: str = 'LYRICS_APP_CLIENT_BEARER',
) -> dict[str, str]:
    token_lyrics_app = ler_variavel_ambiente(
        nome_variavel = env_var_name,
        variavel_sistema = True,
    )

    header = {'Authorization': f'Bearer {token_lyrics_app}'}

    return header


def get_artist_by_song_base_data(
    song_data_list: str,
    artist: str,
    song: str,
    data_information: dict[str, str],
) -> tuple[str, dict[str, str]]:
    for song_data in song_data_list:
        song_data_artist_name = clean_data(
            song_data['result']['primary_artist']['name']
        )
        song_data_song_tile = clean_data(
            song_data['result']['title']
        )
        song_data_lyrics_state = clean_data(
            song_data['result']['lyrics_state']
        )
        artist = clean_data(artist)
        song = clean_data(song)

        if remover_acentos(song_data_artist_name.upper()).__contains__(remover_acentos(artist.upper())):
            data_information['artist_name'] = song_data_artist_name
            data_information['artist_id'] = song_data['result']['primary_artist']['id']

            if remover_acentos(song_data_song_tile.upper()).__contains__(remover_acentos(song.upper())):
                data_information['url'] = song_data['result']['url']
                data_information['title'] = song_data['result']['title']
                data_information['lyrics_state'] = song_data_lyrics_state

            if song_data_lyrics_state.upper() == 'COMPLETE':
                break

    return data_information


def get_song_base_by_search(
    song: str,
    artist: str,
    header: dict[str, str],
    url_base: str = 'https://api.genius.com/',
) -> tuple[str, dict[str, str]]:
    from json import loads

    search_artist_endpoint = f'search?q="{song.upper()} {artist.upper()}"'
    url_search_artist = ''.join((url_base, search_artist_endpoint))
    base_data = loads(
        get(url=url_search_artist, headers=header).content
    )

    error_data = api_error_validation(base_data)
    if (error_data[0] is not None):
        raise SystemError(
            f'Error: {error_data[0]}\n Description: {error_data[1]}'
        )
    
    return base_data


def extract_lyrics_content(
    data_information: dict[str, str],
) -> list[str]:
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/119.0.0.0 Safari/537.36'
        )
    }

    url = data_information['url']

    response = get(url, headers = headers)
    response.raise_for_status()
    html_content = BeautifulSoup(response.text, 'html.parser')
    lyrics_divs = html_content.find_all(
        'div',
        {'data-lyrics-container': 'true'}
    )

    lyrics_content: list[str] = []
    for index_div in range(len(lyrics_divs)):
        for item in lyrics_divs[index_div].children:
            line_temp = []
            if (str(item).__contains__('<br/>')):
                line_temp += [
                    items.strip()
                    for items in item.strings
                ]
            elif (not str(item.text) == ''):
                line_temp.append(str(item.text).strip())
            else:
                line_temp.append('BLANKLINESTAG')
        
            lyrics_content += [
                line
                for line in line_temp
            ]

    lyrics_content_temp = []
    for item in lyrics_content:
        line_temp = ''
        if (not item == 'BLANKLINESTAG'):
            line_temp = str(item).strip()
            lyrics_content_temp.append(line_temp)
            
    lyrics_content = lyrics_content_temp

    return lyrics_content


def search_lyrics(artist: str, song: str,):
    data_information = {
        'artist_name': '',
        'artist_id': '',
        'title': '',
        'url': '',
        'lyrics_state': ''
    }

    header_api = get_api_auth_bearer()

    song_base_data = get_song_base_by_search(song, artist, header_api)

    if song_base_data['response']['hits'] == []:
        raise SystemError(
            'Há algo de errado com a busca, verifique a ortografia.'
        )

    song_data_list = song_base_data['response']['hits']

    data_information = get_artist_by_song_base_data(
        song_data_list,
        artist,
        song,
        data_information,
    )

    if data_information['artist_name'] == '':
        raise SystemError(
            'Não foi possível localizar o artista solicitado.'
        )

    if data_information['title'] == '':
        raise SystemError(
            'Não foi possível localizar a música solicitada.'
        )

    lyrics_content = extract_lyrics_content(data_information)

    cls()

    show_lyrics_details(
        data_information,
        lyrics_content
    )


def show_lyrics_details(
    data_information: dict[str, str],
    lyrics_content: list[str],
):
    song_metadata = {
        'artist_name': data_information['artist_name'],
        'title': data_information['title'],
        'url': data_information['url'],
        'lyrics_state': data_information['lyrics_state'],
    }

    print('Artist:', song_metadata['artist_name'])
    print('Title:', song_metadata['title'])
    print('Webpage Lyrics URL:', song_metadata['url'])
    print('Lyrics Status:', song_metadata['lyrics_state'], '\n')
    lyrics_content = format_lyrics_content(lyrics_content = lyrics_content)

    [print(item) for item in lyrics_content]
    print('\n')
