__author__ = 'karl_leswing'
from pybrain.datasets            import SupervisedDataSet
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
import cPickle as pickle
import numpy as np

#generate some data
np.random.seed(93939393)
data = SupervisedDataSet(2, 1)
for x in xrange(10):
    y = x * 3
    z = x + y + 0.2 * np.random.randn()
    data.addSample((x, y), (z,))

#build a network and train it

print 'creating net1'
net1 = buildNetwork( data.indim, 2, data.outdim )
trainer1 = BackpropTrainer(net1, dataset=data, verbose=True)
for i in xrange(10):
    trainer1.trainEpochs(1)

    pickle.dump(net1, open('../testNetwork.dump', 'w'))
    net2 = pickle.load(open('../testNetwork.dump'))
    #print 'loaded net2 using pickle'
    print '\tvalue after: %.2f'%(net2.activate((1, 4))[0])
    print '\tvalue after %d epochs: %.2f'%(i, net1.activate((1, 4))[0])


print # So far, so good. Let's test pickle

# save the trained net1
pickle.dump(net1, open('../testNetwork.dump', 'w'))

# reload as net2
net2 = pickle.load(open('../testNetwork.dump'))
print 'loaded net2 using pickle'
print '\tvalue after: %.2f'%(net2.activate((1, 4))[0])