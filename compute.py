from keras.layers import Dense, Input
from keras.models import Model
import numpy as np
import time


img_input = Input([2000])
layer = Dense(2000)(img_input)
model = Model(img_input, layer)

data = np.random.random_sample([2000])
start = time.time()
for _ in range(100):
    model.predict(np.array([data]))
print 'compute time: {:.3f} s'.format((time.time() - start) / 100)