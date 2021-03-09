from linetimer import CodeTimer
import math
class probabilistic_coverage:
    def __init__(self,events,sensors,values,r_s,soft_edges = False,soft_edge_eps = 0):
        self.events = events
        self.sensors = sensors
        self.values = values
        self.r_s = r_s
        self.sensor_sets = []
        self.soft_edges = soft_edges
        self.soft_edge_eps = soft_edge_eps
        
        for s in self.sensors:
            sensor_set = []
            for j,e in enumerate(self.events):
                if self.get_prob(e,s,soft = self.soft_edges) > self.soft_edge_eps:
                        sensor_set.append(j)

                    
            self.sensor_sets.append(sensor_set)
        print(len(self.sensor_sets))

    def get_X(self):
        return list(range(len(self.sensor_sets)))
    
    def objective(self,S):
        """
        S is now a list of indices of data data points

        Need to change this for soft edges
        """

        total_events  = set()
        for s in S:
            total_events |= set(self.sensor_sets[s])

        if not self.soft_edges:
            value = sum([self.values[i] for i in total_events])
        else:
            value = sum([(1-self.get_event_prob_product(e, S,self.soft_edges))*self.values[e] for e in total_events])
            
        return value

    def get_prob(self,event,x, soft = False):
        if soft:
            return math.exp(-math.pow(self.dist(event,x),2)/math.pow(self.r_s,2))
        else:
            return 1 if self.dist(x,event) < self.r_s else 0    
    
    def get_event_prob_product(self,e,S,soft):
        probs = [1-self.get_prob(self.events[e],self.sensors[x],soft)+ 0.000001 for x in S]
        #print(probs)
        return math.exp(sum(map(math.log, probs)))
            
    def dist(self,p1,p2):
        return math.sqrt(math.pow(p1[0]-p2[0],2)+ math.pow(p1[1]-p2[1],2))

    def greedy(self,n,timing = False):
        X = list(range(len(self.sensor_sets)))
        S = []
        for i in range(n):
            x = max(X,key = lambda x: self.objective(S+[x])-self.objective(S))
            S.append(x)
            X.remove(x)
        return S

    def greedy_with_timing(self,n):
        ct = CodeTimer()
        X = list(range(len(self.sensor_sets)))
        S = []
        times = []
        cummulative_time = 0
        for _ in range(n):
            with ct:
                x = max(X,key = lambda x: self.objective(S+[x])-self.objective(S))
                S.append(x)
                X.remove(x)
            cummulative_time += ct.took
            times.append(cummulative_time)
        return S, times


    def marginal(self,x,S):
        return self.objective(S+[x])-self.objective(S)

    