from app.generic import search_lyrics
from py_rpautom.python_utils import cls, abrir_arquivo_texto


cls()

artist = 'James Blunt'
song = 'You\'re beautiful'
# song = 'You are beautiful'
# song = '1973'

# artist = 'IU'
# song = '느리게 하는 일 (What I’m Doing Slow)'
# song = 'Blueming'

# artist = 'Avril Lavigne'
# song = 'Complicated'
# song = 'I\'m with you'

# artist = 'fresno'
# song = 'quebre as correntes'
# song = 'pólo'

def start_lyrics(artist, song):
    try:
        search_lyrics(artist, song)
    except Exception as error:
        print(error.args[0], '\n')

tracklist_content = abrir_arquivo_texto(
    caminho='./data/tracklist.txt', encoding='utf8'
).splitlines()

for track in tracklist_content[1:]:
    track_number, song_title, artist_name = track.split(';')

    start_lyrics(artist_name, song_title)
    input('Pressione Enter para continuar...')
