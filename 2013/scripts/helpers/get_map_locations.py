__author__ = 'karl_leswing'
import Tkinter
from PIL import ImageDraw, Image, ImageTk
from sys import argv
import sys

data_dir = '../../data'

window = Tkinter.Tk(className="bla")

image = Image.open(sys.argv[1] if len(argv) >= 2 else data_dir + '/images/blank_bracket.png')
canvas = Tkinter.Canvas(window, width=image.size[0], height=image.size[1])
canvas.pack()
image_tk = ImageTk.PhotoImage(image)
canvas.create_image(image.size[0] // 2, image.size[1] // 2, image=image_tk)


def callback(event):
    fout = open(data_dir + '/locations.txt', 'a')
    fout.write("%s,%s\n" % (event.x, event.y))
    fout.close()


canvas.bind("<Button-1>", callback)
Tkinter.mainloop()