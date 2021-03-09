import numpy as np
import math
from scipy.special import comb
import itertools

class approximator():
    def __init__(self,f,k):
        #print("Initalizing Approximator")
        self.f = f
        self.k = k
    
    def greedy_fit(self,X,n):
        """
        Basic Greedy fit using full total gradients
        """
        X = X.copy()
        S = []
        for _ in range(n):
            f_S = self.f(S)
            x = max(X, key = lambda x:self.f(S+[x])-f_S)
            S.append(x)
            X.remove(x)
        return S
            
    def pairwise_fit(self,X,n,lb = True):
        X = X.copy()
        S = []
        estimates = np.zeros(len(X))
        f_x = np.zeros(len(X))
        
        for i,x in enumerate(X):
            estimates[i] = self.f([x])
            f_x[i] = estimates[i]
        
        for _ in range(n):
            # select element 
            i_opt = np.argmax(estimates)
            S.append(X[i_opt])
            estimates[i_opt] = -np.inf
            # update estimates
            if lb:
                for i,x in enumerate(X):
                    estimates[i] -= f_x[i] + f_x[i_opt] - self.f([X[i_opt],x])
            else:
                for i,x in enumerate(X):
                    estimates[i] = min([estimates[i],self.f([X[i_opt],x]) - f_x[i_opt]])
        return S
        
    def coeff(self,j,s_n):
        return sum(math.pow(-1,i)*comb(s_n-j,i) for i in range(self.k-j))
    
    
    def compute_estimate(self,S,order_sums_row):
        s_n = len(S)
        approximation = 0
        
        for i in range(self.k):
            c = self.coeff(i,s_n)
            approximation += c*order_sums_row[i]
        return approximation
    
    def update_order_sums(self,x_i,S,X,order_sums):
        #print(order_sums)
        
        # check k
        if self.k==1:
            return
        
        #loop through elements in order sums and update table
        for i in range(len(X)):
            x = X[i]
            
            #update lowest order term
            order_sums[i,1] += self.f([x]+[x_i])- self.f([x_i])
            
            #loop through higher order terms
            for j in range(1,self.k-1):
                combs = itertools.combinations(S,j)
                order_sums[i,j+1] += sum(self.f([x]+[x_i]+list(comb))-self.f([x_i]+list(comb)) for comb in combs)
            
    def approximate_fit(self,X,n):
        X = X.copy()
        S = []
        marginals = []
        order_sums = np.zeros((len(X),self.k))
        #print(order_sums)
        min_estimates = np.zeros(len(X))
        for i,x in enumerate(X):
            order_sums[i,0] = self.f([x])
            min_estimates[i] = order_sums[i,0]
        for _ in range(n):
            #find Selections
            i_opt = np.argmax(min_estimates)
            S.append(X[i_opt])
            marginals.append(min_estimates[i_opt])
            min_estimates[i_opt] = -np.inf
            #update Estimates
            self.update_order_sums(x,S,X,order_sums)
            for i in range(len(X)):
                estimate = self.compute_estimate(S,order_sums[i])
                min_estimates[i] = min([estimate,min_estimates[i]])
            
        
        
        
        return S,marginals
    
    def pairwise_upperbound(self,x,S):
        if len(S) == 0:
            return self.f([x])
        x_k = min(S,key = lambda x_j:self.f([x,x_j])-self.f([x_j]))
        return self.f([x,x_k])-self.f([x_k])

    def pairwise_lowerbound(self,x,S):
        fx = self.f([x])
        marg = fx
        for s in S:
            marg -= fx-self.f([s]+[x])+self.f([s])
        return marg
        

    def find_greedy_choices(self,S,X,upperbound = False):
        X = X.copy()
        S_g = []
        for i in range(len(S)):
            if upperbound:
                x = max(X,key = lambda x:self.pairwise_upperbound(x,S[:i]))
            else:
                x = max(X,key = lambda x: self.f(S[:i]+[x])-self.f(S[:i]) )
            S_g.append(x)
            X.remove(S[i])
        return S_g
            
        
        
        
        
        
        


    
    
