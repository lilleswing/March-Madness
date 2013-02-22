__author__ = 'karl_leswing'
data_dir = '../../data'
old_vals = [
    "0.9",
    "0.7"
]
new_vals = [
    "1.3",
    "0.9"
]

w = open(data_dir + '/training.txt', 'r').read()

for i in xrange(0, len(new_vals)):
    w = w.replace(old_vals[i], new_vals[i])

fout = open(data_dir + '/training.txt', 'w')
fout.write(w)
fout.close()

