import numpy as np
import time

total = 0
for _ in range(100):
    s1, s2 = np.random.random_sample([2000]), np.random.random_sample([2000])
    start = time.time()
    np.subtract(s2, s1)
    total += (time.time() - start)

print 'subtract time: {:.3f} s'.format(total / 100)
