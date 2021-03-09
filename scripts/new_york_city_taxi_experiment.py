from submodular_approximation import probabilistic_coverage
from submodular_approximation import approximator
from linetimer import CodeTimer
import os
import geopandas as gpd
import earthpy as et
import pandas as pd
import json
import datetime
import math
def open_locations_data():
    print(os.listdir("../../"))
    US_SURVEY_FOOT_TO_METER = 1200/3937
    locations = gpd.read_file("../../taxi_data/taxi_zones.shp")
    centroids_meters = []
    centroids_feet = []
    
    for row in locations.iterrows():
        #print(row[1].get("geometry"))
        geometry  =  row[1].get("geometry")
        centroids_meters.append((geometry.centroid.x*US_SURVEY_FOOT_TO_METER,geometry.centroid.y*US_SURVEY_FOOT_TO_METER))
        centroids_feet.append((geometry.centroid.x,geometry.centroid.y))

    return centroids_meters,centroids_feet

def open_ride_data(start_time,end_time):
    #returns number of pick ups indexed by locationID
    file_path = "../../taxi_data/fhv_tripdata_2020-01.csv"

    #Open file and convert column to datetime format
    df = pd.read_csv(file_path)

    #Collect the where the time of day constraint is met 
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    ride_sets =[df.loc[(df['pickup_datetime'] > start_time+datetime.timedelta(days=i)) & (df['pickup_datetime'] < end_time+datetime.timedelta(days=i))] for i in range(31)]
    rides = pd.concat(ride_sets)
    
    #compute the average values
    counts = [len(rides.loc[rides["PULocationID"] == i])/31 for i in range(1,264)]
    return counts



def compute_bound_sequential(alphas):
    """
    Function computes a bound compared to optimal given a set of approximation factors.
    
    """
    n = len(alphas)
    sum_alphas = sum(1/a for a in alphas)
    exponent = -(1/n)*sum_alphas
    #print(1- math.exp(exponent))
    return 1- math.exp(exponent)
    
    
def compute_theoretical_alphas(S_g,S,problem):
    """
    Function Computes the theoretical alphas using the minimum possible approximation factor a_min = f(x_i^g|S_{i-1})/f(x_i|S_{i-1})
    """
    #theoretical_alphas_lb = [problem.marginal(S_g_l[i],S_lower[:i])/max([problem.marginal(S_lower[i],S_lower[:i]),0.00001] )for i in range(n)]
    theoretical_alphas = []
    for i in range(len(S)):
        if problem.marginal(S_g[i],S[:i]) > 0.0001:
            theoretical_alphas.append(problem.marginal(S_g[i],S[:i])/max([problem.marginal(S[i],S[:i]),0.00001] )) 
        else:
            print("numerator zero")
            theoretical_alphas.append(1)
    return theoretical_alphas    


def effectiveness_experiment(n):
    """
    Function run the performance efffective expirements. First it collects the problem to run the problem on and then the
    exectues the greedy and pairwise algorithms on each of the sets of data and records them to a json file.
    """
    
    #get york city geo data
    centroids_meters, centroids_feet = open_locations_data()
    r_s = 3000
    experiment_data = []

    #Collect Data for testing
    count_sets = []
    for t in range(12):
        start_time = datetime.datetime(2020,1,1,0, 0, 0)+datetime.timedelta(hours=2*t)
        end_time = datetime.datetime(2020,1,1,2, 0, 0)+datetime.timedelta(hours=2*t)
        print(start_time)
        counts = open_ride_data(start_time,end_time)
        count_sets.append(counts)

    # begin executing data
    for t in range(12):
        estimated_bounds = []
        theoretical_bounds = []
        greedy_values = []
        lb_values = []
        
        #logging
        start_time = datetime.datetime(2020,1,1,0, 0, 0)+datetime.timedelta(hours=2*t)
        end_time = datetime.datetime(2020,1,1,2, 0, 0)+datetime.timedelta(hours=2*t)
        print(start_time)
        counts = count_sets[t]
        
        #set up timers
        g_timer = CodeTimer("greedy time",unit = "s")
        lb_timer = CodeTimer("lb time", unit = "s")
        ub_timer = CodeTimer("ub time", unit = "s")

        trial_data = {"n":n,"t":t}
        
        #initalize problem
        problem = probabilistic_coverage.probabilistic_coverage(centroids_meters,centroids_meters,counts,r_s,soft_edges = False, soft_edge_eps = 0.0005)
        X = problem.get_X()
        ap = approximator.approximator(problem.objective,2)
        
        # execute Algorithms
        with g_timer:
            S = ap.greedy_fit(X,n)
        trial_data["greedy_time"] = g_timer.took
        with lb_timer:
            S_lower = ap.pairwise_fit(X,n,lb=True)
        trial_data["lb_time"] = lb_timer.took
        with ub_timer:
            S_upper = ap.pairwise_fit(X,n,lb=False)
        trial_data["ub_time"] = ub_timer.took


        # Lower Bound Approximation Analysis
        print("computing bounds for lower bound algo")
        S_g_l = ap.find_greedy_choices(S_lower,X)
        S_u_l = ap.find_greedy_choices(S_lower,X,upperbound=True)
        

        theoretical_alphas_lb = compute_theoretical_alphas(S_g_l,S_lower,problem)
        trial_data["theoretical_bounds_lb"] = [compute_bound_sequential(theoretical_alphas_lb[:i+1])for i in range(len(theoretical_alphas_lb))]

        estimated_alphas_lb = [ap.pairwise_upperbound(S_u_l[i],S_lower[:i])/max([ap.pairwise_lowerbound(S_lower[i],S_lower[:i]),0.0000001] )for i in range(n)]
        trial_data["estimated_bounds_lb"] = [compute_bound_sequential(estimated_alphas_lb[:i+1])for i in range(len(estimated_alphas_lb))]

        print("computing bounds for upper bound algo")
        S_g_u = ap.find_greedy_choices(S_upper,X)

        theoretical_alphas_ub = compute_theoretical_alphas(S_g_u,S_upper,problem)
        trial_data["theoretical_bounds_ub"] = [compute_bound_sequential(theoretical_alphas_ub[:i+1])for i in range(len(theoretical_alphas_ub))]

        estimated_alphas_ub = [ap.pairwise_upperbound(S_upper[i],S_upper[:i])/max([ap.pairwise_lowerbound(S_upper[i],S_upper[:i]),0.00001] )for i in range(n)]
        trial_data["estimated_bounds_ub"] = [compute_bound_sequential(estimated_alphas_ub[:i+1])for i in range(len(estimated_alphas_ub))]
    
        trial_data["greedy_values"] = [ap.f(S[:i])for i in range(1,len(S)+1)]
        trial_data["lb_values"] = [ap.f(S_lower[:i])for i in range(1,len(S)+1)]
        trial_data["ub_values"] = [ap.f(S_upper[:i])for i in range(1,len(S)+1)]
        
        experiment_data.append(trial_data)

    print(experiment_data)
    now = datetime.datetime.now()
    date_time = now.strftime("%m-%d-%Y_%H-%M")
    print("date and time:",date_time)	
    with open('../../Experimental_Data/experiment '+date_time+"_soft.json", 'w+') as outfile:
        json.dump(experiment_data, outfile)
    
def speed_experiment(n):
    #open geographic information
    centroids_meters,centroids_feet = open_locations_data()
    r_s = 3000
    experiment_data = []
    
    #get count sets for the observations
    with open('../../Experimental_Data/countdata.json', 'r') as infile:
        count_sets = json.load(infile)
    total_data = []
    
    #Run the speed test 10 times to take average of later
    for i in range(10):
        speed_data = []
        for t in range(12):
            data = {"t":t}
            print("Time:",t)
            data['g_times'] = []
            data['lb_times'] = []
            data['ub_times'] = []
            counts = count_sets[t]
            timer  = CodeTimer()
            problem = probabilistic_coverage.probabilistic_coverage(centroids_meters,centroids_meters,counts,r_s,soft_edges = True,soft_edge_eps = 0.005)
            n_s = list(range(1,n+1,3))
            X = problem.get_X()
            ap = approximator.approximator(problem.objective,2)
            #S, times = problem.greedy_with_timing(n)
            
            #execute the 3 algorithms
            for n_i in n_s:
                print("n = ",n_i)
                print("Classical Greedy")
                with timer:
                    S = ap.greedy_fit(X,n_i)
                data['g_times'].append(timer.took)

                print("Pessimisitic Greedy")
                with timer:
                    S = ap.pairwise_fit(X,n_i,lb = True)
                data['lb_times'].append(timer.took)

                print("Optimistic Greedy")
                with timer:
                    S = ap.pairwise_fit(X,n_i,lb = False)
                data['ub_times'].append(timer.took)
            print(data)
            speed_data.append(data)
        total_data.append(speed_data)
        
        #save the data 
        now = datetime.datetime.now()
        date_time = now.strftime("%m-%d-%Y_%H-%M")
        with open('../../../Experimental_Data/speed experiment '+date_time+"_soft.json", 'w+') as outfile:
            json.dump(speed_data, outfile)

if __name__ == "__main__":
    print("Starting Expirement")
    #centroids_meters,centroids_feet = open_locations_data()
    #effectiveness_experiment(40)
    speed_experiment(10)
    
    