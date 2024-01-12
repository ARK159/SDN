
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from collections import Counter
import math
import networkx as nx
import sys


def read_file(file):
    with open('gml','r') as file:
        lines=file.readlines()
    return lines

def haversine_distance(lat1, lon1, lat2, lon2):
     
    # distance between latitudes
    # and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
 
    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0
 
    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) +
         pow(math.sin(dLon / 2), 2) *
             math.cos(lat1) * math.cos(lat2))
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return abs(rad * c)

def distance_func(p1, p2):
    
    lat1=float(p1[2])
    long1=float(p1[4])
    
    lat2=float(p2[2])
    long2=float(p2[4])
    CC_time=0
    cores=[]
    
    # for c in master_df['Cluster'].unique():
    #     if c!=0:
    #         mean_lat=0
    #         mean_long=0
    #         for i in range(len(datasets)):
    #             # print(len(master_df[i]))
    #             if master_df.loc[i]['Cluster']==c:
    #                 mean_lat=mean_lat+float(datasets[i][2])
    #                 mean_long+=float(datasets[i][4])
    #         cores.append((mean_lat,mean_long))
    # CC_time=0
    # if len(cores)>0:
    #     for i in range(len(cores)):
    #         for j in range(len(cores)):
                
    #             if i!=j:
    #                 dist=haversine_distance(cores[i][0],cores[i][1],cores[j][0],cores[j][1])
    #                 CC_time+=(dist/(10*1000))

    bw=graph.get_edge_data(p1[0],p2[0])
    # print(cores)
    if bw==None:   
        link_label=7*1000
    else:
        if 'LinkLabel' in bw.keys():
            link_label=bw['LinkLabel']
            link_label = link_label.replace("<", "")
            if "Gbps" in link_label:
                link_label = float(link_label.replace("Gbps", "")) * 1000  
            elif "Mbps" in link_label:
                link_label = float(link_label.replace("Mbps", ""))
                
        else:
            link_label=155
                
    dist=haversine_distance(lat1,long1,lat2,long2)
    
    if dist ==None: 
        print("hello")
    return (dist/link_label)


def output_unprocessed_point():
    subdata                = master_df[['Points','Cluster']]
    unprocessed_data       = subdata[subdata['Cluster']==0]
    index_unprocessed_data = unprocessed_data['Cluster'].index[0]
    return master_df.loc[index_unprocessed_data]['Points']
    
    
def check_processed(testpt):
    for i in range(len(master_df)):
        if (np.array(testpt)==master_df.loc[i]['Points']).all():
            cluster_value = master_df.loc[i]['Cluster']
            if cluster_value==0:
                return 'not assigned'
            else:
                return 'assigned'
            
            
def calculate_neighbors(pt):
    df = pd.DataFrame(columns=['neighbors','nbr_distance','core_distance','reach_distance'])
    nbrs = []
    distance = []
    # print(datasets.shape)
    for i in range(datasets.shape[0]):
        # print(pt,"  ",datasets[i])
        if (pt!=datasets[i]).any():
            # print(pt,' ',datasets[i])
            
            dist = distance_func(pt,datasets[i])
            # print(dist)
            # print(dist)
            if dist <eps:
                nbrs.append(datasets[i])
                distance.append(dist)
    # print(len(nbrs))
    df['neighbors'] = nbrs
    df['nbr_distance'] = distance
    df = df.sort_values('nbr_distance')
    df.index = range(len(df))
    if len(df)>=minpts:
        df['core_distance'] = [df.loc[minpts-1]['nbr_distance']]*len(df)
        df['reach_distance'] = df[['nbr_distance','core_distance']].max(axis=1)
        core_dist_decision  = 'defined'
    else:    
        df['core_distance'] = [20]*len(df)
        df['reach_distance'] = [2]*len(df)
        core_dist_decision  = 'undefined'
    
    return df, df['neighbors'].values,core_dist_decision


def update_p(p,Cluster,N):
    for i in range(master_df.shape[0]):
            if (np.array(p)==master_df.loc[i]['Points']).all():
                master_df.loc[i,'Cluster']       = Cluster
                master_df.loc[i,'Core Distance'] = N['core_distance'].values[0]
                
                
def update_neighbor_data(N):
    for i in range(len(N)):
        pt             = N['neighbors'][i]
        reach_distance = N['reach_distance'][i]
        for j in range(master_df.shape[0]):
                
                if (pt==master_df.loc[j]['Points']).all():
                    existing_reach_dist     = master_df.loc[j]['Reachability Distance']
                    
                    if existing_reach_dist == 2 or (existing_reach_dist >reach_distance):
                        master_df.loc[j,'Reachability Distance']=reach_distance


file_data=read_file('gml')
graph=nx.parse_gml(file_data)
    # print("Nodes",graph.nodes(data=True))
    # print("Edges",graph.edges(data=True))
    # print(graph.graph)
node_list = []
for node_id, node_data in graph.nodes(data=True):
    temp= [
    node_id,
    node_data.get('Country', ''),
    node_data.get('Latitude', ''),
    node_data.get('Internal', ''),
    node_data.get('Longitude', '')
    ]
    node_list.append(temp)

# print(node_list)


X=np.array(node_list)
# np.random.seed(101)
# datasets = np.random.shuffle(X)
datasets = X

# eps=0.
# val=()
# minerror =sys.maxsize
# while(eps<=0.2):
#     minpts=1
#     while(minpts<10):
#         # print(eps,minpts)
#         master_df                          = pd.DataFrame(columns=['Points','Cluster','Reachability Distance','Core Distance'])
#         master_df['Points']                = [list(X[i]) for i in range(X.shape[0])]
#         master_df['Cluster']               = [0] *(X.shape[0])
#         master_df['Reachability Distance'] = [2]*X.shape[0]
#         master_df['Core Distance']         = [2]*X.shape[0]
#         unclustered_data                   = len(master_df[master_df['Cluster']==0])
#         Cluster                            = 1
#         master_df.head()

#         max_iters=0
#         while unclustered_data>0 and max_iters<30:
            
#             p                             = output_unprocessed_point()
            
#             N,nbrs_p,coredist_decision    = calculate_neighbors(p)
#             # print(coredist_decision)
#             # print(nbrs_p)
#             if coredist_decision=='defined':
#                 _              = update_p(p,Cluster,N)
#                 _              = update_neighbor_data(N)
#             for i in range(len(nbrs_p)):
#                 # print("hello")
#                 if check_processed(nbrs_p[i]) == 'not assigned':
#                     N_new,nbrs_q,coredist_decision = calculate_neighbors(nbrs_p[i])
#                     if coredist_decision=='defined':
#                         _              = update_p(nbrs_p[i],Cluster,N_new)
#                         _              = update_neighbor_data(N_new)
#             Cluster = Cluster+1
#             unclustered_data = len(master_df[master_df['Cluster']==0])
#             max_iters+=1
            
#         error=master_df['Reachability Distance'].sum()
#         if error<minerror:
#             val=(eps,minpts)
#         print('minpts=',minpts,'   ','eps=',eps)
#         print(master_df)
#         minpts+=1
#     eps+=0.01

eps=0.2
minpts=2
master_df                          = pd.DataFrame(columns=['Points','Cluster','Reachability Distance','Core Distance'])
master_df['Points']                = [list(X[i]) for i in range(X.shape[0])]
master_df['Cluster']               = [0] *(X.shape[0])
master_df['Reachability Distance'] = [2]*X.shape[0]
master_df['Core Distance']         = [2]*X.shape[0]
unclustered_data                   = len(master_df[master_df['Cluster']==0])
Cluster                            = 1
master_df.head()

max_iters=0
while unclustered_data>0 and max_iters<10:
    
    p                             = output_unprocessed_point()
    
    N,nbrs_p,coredist_decision    = calculate_neighbors(p)
    # print(coredist_decision)
    # print(nbrs_p)
    if coredist_decision=='defined':
        _              = update_p(p,Cluster,N)
        _              = update_neighbor_data(N)
    for i in range(len(nbrs_p)):
        # print("hello")
        if check_processed(nbrs_p[i]) == 'not assigned':
            N_new,nbrs_q,coredist_decision = calculate_neighbors(nbrs_p[i])
            if coredist_decision=='defined':
                _              = update_p(nbrs_p[i],Cluster,N_new)
                _              = update_neighbor_data(N_new)
    Cluster = Cluster+1
    unclustered_data = len(master_df[master_df['Cluster']==0])
    max_iters+=1
# master_df.sort_values(by='Cluster')
# print(master_df)

# df=master_df.copy()

# colors = plt.cm.nipy_spectral(np.linspace(0, 1, len(set(df['Cluster']))))

# Plot the reachability distances with cluster colors
# plt.figure(figsize=(10, 2))

# for i, (point, cluster, reachability_distance) in enumerate(zip(df['Points'], df['Cluster'], df['Reachability Distance'])):
#     plt.bar(i, reachability_distance, color=colors[cluster],width=0.1)

# plt.title('OPTICS Reachability Distances with Cluster Colors')
# plt.ylabel('Reachability Distance')
# plt.xlabel('Ordered Points')
# plt.show()

latitude=[float(c[2]) for c in X]
longitude=[float(c[4]) for c in X]

centroids=[]

# for c in master_df['Cluster'].unique():
#     if c!=0:
#         mean_lat=0
#         mean_long=0
#         for i in range(len(datasets)):
#             # print(len(master_df[i]))
#             if master_df.loc[i]['Cluster']==c:
#                 mean_lat=mean_lat+float(datasets[i][2])
#                 mean_long+=float(datasets[i][4])
#         centroids.append((mean_lat,mean_long))
df=master_df[master_df['Cluster']==0]
# print(df)
import sys

# Assuming distance_func is defined somewhere in your code
# def distance_func(x1, y1, x2, y2):
#     # Your distance calculation logic goes here
#     pass

cluster=None
mind=100
loc=None

for i in range(len(master_df)):
    pt1=master_df.iloc[i]['Points']
    loc=None
    cluster=None
    mind=100
    for j in range(len(master_df)):
        pt2=master_df.iloc[j]['Points']
        
        if j!=i and master_df.iloc[i]['Cluster']==0 and master_df.iloc[j]['Cluster']!=0:
            print(i,' ',j)
            dist=distance_func(pt1,pt2)
            print(pt1,' ',pt2,' ',dist)
            if dist<mind:
                mind=dist
                loc=i
                cluster=master_df.iloc[j]['Cluster']
                
   
    if loc!=None:
        print(loc)
        print(cluster)
        print(master_df.iloc[loc])
        master_df['Cluster'][loc] = cluster
        print(master_df)
        




print(master_df)
            
            






 

plt.scatter(longitude,latitude,c=master_df['Cluster'])
plt.show()