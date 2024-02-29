from scipy.stats import norm
import numpy as np


prob = norm(loc=11, scale=5)
a = prob.pdf(12)/0.8
for i in range(24):
    print(f"{i} {prob.pdf(i)/a}")