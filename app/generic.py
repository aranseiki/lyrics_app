from json import loads
from pprint import pprint

from bs4 import BeautifulSoup
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


def get_api_auth_bearer(
    env_var_name: str = 'LYRICS_APP_CLIENT_BEARER',
) -> dict[str, str]:
    token_lyrics_app = ler_variavel_ambiente(
        nome_variavel = env_var_name,
        variavel_sistema = True,
    )

    header = {'Authorization': f'Bearer {token_lyrics_app}'}

    return header


def get_artist_base_data(
    artist: str,
    header: dict[str, str],
    url_base:str = 'https://api.genius.com/',
) -> tuple[str, dict[str, str]]:
    search_artist_endpoint = f'search?q={artist.upper()}'
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


def get_song_details(
    song: str,
    song_data_list: list[dict[str, str]],
):    
    selected_data_information = {
        'artist_name': '',
        'artist_id': '',
        'full_title': '',
        'url': ''
    }

    for song_data in song_data_list:
        try:
            full_title = remover_acentos(
                song_data['result']['full_title']
            )

            if (
                full_title.upper().__contains__(
                    remover_acentos(song).upper()
                )
            ):
                selected_data_information['title'] = full_title
                selected_data_information['url'] = song_data[
                    'result'
                ]['url']
                selected_data_information['artist_name'] = song_data[
                    'result'
                ]['primary_artist']['name']
                selected_data_information['artist_id'] = song_data[
                    'result'
                ]['primary_artist']['id']
                selected_data_information['full_title'] = full_title

                break
        except:
            ...

    return selected_data_information


def extract_lyrics_content(
    selected_data_information: dict[str, str],
) -> list[str]:
    headers = {
        "User-Agent": (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/119.0.0.0 Safari/537.36'
        )
    }
    url = selected_data_information['url']

    response = get(url, headers = headers)
    response.raise_for_status()
    html_content = BeautifulSoup(response.text, 'html.parser')
    lyrics_divs = html_content.find_all(
        'div',
        {'data-lyrics-container': 'true'}
    )

    lyrics_content: list[str] = []
    for index_div in range(len(lyrics_divs)):
        lyrics_content = [
            str(item.text).strip()
            for item in lyrics_divs[index_div].children
                if (not str(item.text) == '')
        ]

    return lyrics_content


def search_lyrics(artist: str, song: str,):
    header_api = get_api_auth_bearer()

    base_data = get_artist_base_data(artist, header_api)

    song_data_list = base_data['response']['hits']

    selected_data_information = get_song_details(
        song,
        song_data_list,
    )

    if selected_data_information['full_title'] == '':
        raise SystemError(
            'Não foi possível localizar a música solicitada.'
        )

    lyrics_content = extract_lyrics_content(selected_data_information)

    cls()

    show_lyrics_details(
        selected_data_information,
        lyrics_content
    )


def show_lyrics_details(
    selected_data_information: dict[str, str],
    lyrics_content: list[str],
):
    song_metadata = {
        'artist_name': selected_data_information['artist_name'],
        'title': selected_data_information['title']
    }

    print('Artist:', song_metadata['artist_name'])
    print('Title:', song_metadata['title'], '\n')
    [print(item) for item in lyrics_content]
    print('\n')
