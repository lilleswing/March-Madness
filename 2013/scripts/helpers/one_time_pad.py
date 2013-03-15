__author__ = 'karl_leswing'
import sys
import os


def cipher(infile, outfile, padfile):
    block_size = 65536
    while 1:
        data = infile.read(block_size)
        if not data:
            break
        pad = padfile.read(len(data))
        encoded = ''.join([ chr(ord(a) ^ ord(b)) for a, b in zip(data, pad) ])
        outfile.write(encoded)


if __name__ == '__main__':
    infile = sys.argv[1]
    padfile = sys.argv[2]
    outfile = os.path.join(os.path.dirname(os.path.abspath(infile)), 'kenpom.db')
    cipher(open(infile), open(outfile, 'wb'), open(padfile))
