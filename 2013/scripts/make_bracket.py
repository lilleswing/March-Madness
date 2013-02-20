import string
from PIL import Image
__author__ = 'karl_leswing'


if __name__ == '__main__':
    places = open('../data/locations.txt').readlines()
    places = map(string.strip, places)
    places = map(lambda x: map(int, x.split(',')), places)
    background = Image.open('../data/images/blank_bracket.png')
    for place in places:
        team = Image.open('../data/images/teams/Duke.gif')
        background.paste(team, (place[0], place[1]))
    background.save('../data/images/full_bracket.png')
