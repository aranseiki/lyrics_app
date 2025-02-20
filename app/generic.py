from json import loads
from pprint import pprint

from py_rpautom.python_utils import (
    cls,
    ler_variavel_ambiente,
    remover_acentos
)
from requests import get


def api_error_get_song_content(
        base_data: dict[str, str],
    ) -> tuple[str, str]:
        error_description = base_data.get('meta').get('message')
        error = str(base_data.get('meta').get('status'))
        return (
            error,
            error_description,
        )


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
) -> tuple[str, dict[str, str]]:
    url_base = 'https://api.genius.com/'
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
    
    return url_base, base_data


def get_artist_data_information(
    artist: str,
    base_data: dict[str, str],
) -> dict[str, str]:
    for song_data in base_data['response']['hits']:
        selected_data_information = {
            'artist_name': '',
            'artist_id': '',
            'full_title': '',
        }

        try:
            if (
                song_data['result']['primary_artist']['name'].upper()
                == artist.upper()
            ):
                selected_data_information['artist_name'] = song_data[
                    'result'
                ]['primary_artist']['name']
                selected_data_information['artist_id'] = song_data[
                    'result'
                ]['primary_artist']['id']
                selected_data_information['full_title'] = song_data[
                    'result'
                ]['full_title']

                break
        except:
            ...

    return selected_data_information


def get_song_content(
    artist_id: int,
    page_number: int,
    url_base: str,
    header_api: dict[str, str],
):
    print('next_page:', page_number)

    endpoint = f'artists/{artist_id}/songs?page={page_number}'
    title_song_endpoint = ''.join((url_base, endpoint, '/songs'))

    title_song_content = loads(
        get(
            url = title_song_endpoint,
            headers = header_api,
        ).content
    )

    error_data = api_error_get_song_content(title_song_content)

    if (
        (error_data[0] is not None)
        and (not error_data[0].startswith('2'))
    ):
        raise SystemError(
            f'Error: {error_data[0]}\n Description: {error_data[1]}'
        )

    next_page = title_song_content['response']['next_page']
    page_number = next_page

    return title_song_content, next_page


def get_song_details(
    music: str,
    url_base: str,
    artist_id: int,
    header_api: dict[str, str],
):
    page_number = 1
    validation_title = False
    title_song = ''
    next_page = None
    while not next_page == 'null':
        title_song_content, page_number = get_song_content(
            artist_id,
            page_number,
            url_base,
            header_api,
        )

        if page_number is None:
            page_number = 'null'
            continue

        (
            validation_title,
            title_song,
            song_information
        ) = get_song_information(
            music,
            title_song_content,
        )

        if validation_title is True:
            break

    return next_page, title_song, song_information


def get_song_information(
    music: str,
    title_song_content: dict[str, str],
):
    for song_data in title_song_content['response']['songs']:
        try:
            song_information = {
                'title': song_data['title'],
                'url': ''
            }

            if (
                remover_acentos(song_information['title'].upper())
                == remover_acentos(music).upper()
            ):
                title_song = song_information['title']
                song_information['url'] = song_data['url']
                validation_title = True

                break
        except:
            ...

    return validation_title, title_song, song_information


def extract_lyrics_content(
    song_details: dict[str, str],
) -> list[bytes]:
    html_content = get(song_details['url'])

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
    return lyrics_content


def search_lyrics(artist: str, music: str,):
    header_api = get_api_auth_bearer()

    url_base, base_data = get_artist_base_data(artist, header_api)

    artist_data_information = get_artist_data_information(
        artist,
        base_data
    )

    artist_id = artist_data_information['artist_id']
    if artist_id == '':
        raise SystemError(
            'Não foi possível localizar o artista da música solicitada.'
        )

    next_page, title_song, song_details = get_song_details(
        music,
        url_base,
        artist_id,
        header_api,
    )

    if (next_page == 'null') and (title_song == ''):
        raise SystemError(
            'Não foi possível localizar a música solicitada.'
        )

    cls()

    lyrics_content = extract_lyrics_content(song_details)

    show_lyrics_details(
        artist_data_information,
        song_details,
        lyrics_content
    )


def show_lyrics_details(
    artist_data_information: dict[str, str],
    song_details: dict[str, str],
    lyrics_content: list[bytes],
):
    song_metadata = {
        'artist_name': artist_data_information['artist_name'],
        'title': song_details['title']
    }

    print(song_metadata['artist_name'])
    print(song_metadata['title'], '\n')

    [print(verse.decode(encoding='utf8')) for verse in lyrics_content]
