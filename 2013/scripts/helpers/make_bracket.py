import string
import ImageDraw
import ImageFont
from PIL import Image

__author__ = 'karl_leswing'
data_dir = '../data'

font = ImageFont.truetype('helpers/interstate-black.ttf', 20)


def multiline_write(draw, place, lines):
    y_loc = place[1]
    for line in lines:
        draw.text((place[0], y_loc), line, fill=(0, 0, 255), font=font)
        y_loc += 15


def make_bracket(winners, outfile):
    places = open(data_dir + '/locations.txt').readlines()
    places = map(string.strip, places)
    places = map(lambda x: map(int, x.split(',')), places)
    background = Image.open(data_dir + '/images/blank_bracket.png')
    draw = ImageDraw.Draw(background)
    for i in xrange(0, len(winners)):
        place = places[i]
        team = Image.open(data_dir + '/images/teams/Duke.gif')
        #background.paste(team, (place[0], place[1]))
        #draw.text((place[0], place[1]), winners[i], fill=(0, 0, 255))
        multiline_write(draw, place, winners[i])
    background.save(outfile)


if __name__ == '__main__':
    data_dir = '../../data'
    font = ImageFont.truetype('interstate-black.ttf', 20)
    make_bracket([("Karl", "100-50")] * 63, data_dir + '/images/full_bracket.png')
