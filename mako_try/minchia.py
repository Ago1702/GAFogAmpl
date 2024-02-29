import numpy as np
from scipy.stats import truncnorm
import matplotlib.pyplot as plt

scale = 8
_range = 12
size = 10000000

X = truncnorm(a=-_range/scale, b=+_range/scale, scale=scale, loc=12).rvs(size=size)
X = X.round().astype(int)

bins = 2 * _range
v = np.array(plt.hist(X, bins, edgecolor="k", density=True)[0])
v = v/v[12]*0.75
for i in v:
    print(np.random.binomial(1, i, 5))
    print(i)
plt.show()