from submodular_approximation import approximator
from submodular_approximation import probabilistic_coverage
from linetimer import CodeTimer
import random
import matplotlib.pyplot as plt
def cardinality(S):
    large_set = set()
    for s in S:
        large_set |= s
    return len(large_set)        
    

ap = approximator.approximator(cardinality,4)

X = [set([k for k in range(2*j,2*j+random.randint(1,10))]) for j in range(100)]
#print(X)
#print(cardinality(X[:4]))
n = 20
# with CodeTimer():
#     S_g = ap.greedy_fit(X,n)
# with CodeTimer():
#     S = ap.pairwise_fit(X,n)
leg = []
values = []
k_s = list(range(2,8))
for k in k_s:
    with CodeTimer():
        ap = approximator.approximator(cardinality,k)
        S_h,marges = ap.approximate_fit(X, n)
        #print(S_h)
        plt.plot(marges)
        print(len(S_h))
        print("Value",cardinality(S_h),"K =",k)
        leg.append("K ="+ str(k))
        values.append(cardinality(S_h))
plt.legend(leg)
plt.figure()
plt.plot(k_s,values)
plt.show()
print()
print(cardinality(S_h))
    







