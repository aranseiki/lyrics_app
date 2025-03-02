from app.generic import search_lyrics
from py_rpautom.python_utils import cls


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

try:
    search_lyrics(artist, song)
except Exception as error:
    print(error.args[0], '\n')
