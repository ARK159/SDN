import networkx as nx
import numpy as np
import sys
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
from sklearn.cluster import KMeans


def read_file(file):
    with open('gml','r') as file:
        lines=file.readlines()
    return lines

def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Radius of the Earth in kilometers (mean value)
    R = 6371.0

    # Calculate the distance
    distance = R * c

    return distance

def distance(p1, p2,graph):
    lat1=float(p1[2])
    long1=float(p1[4])
    
    lat2=float(p2[2])
    long2=float(p2[4])
    
    delay=graph.get_edge_data(p1[0],p2[0])
    if delay==None:
        link_label=10*1000
    else:
        if 'LinkLabel' in delay.keys():
            link_label=delay['LinkLabel']
            link_label = link_label.replace("<", "")
            if "Gbps" in link_label:
                link_label = float(link_label.replace("Gbps", "")) * 1000  
            elif "Mbps" in link_label:
                link_label = float(link_label.replace("Mbps", ""))
        else:
            link_label=155
    
    dist=haversine_distance(lat1,long1,lat2,long2)
    
    return (dist/link_label)
def convert_to_graph(file_data):
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
        # Add more attributes as needed
        ]
        
        node_list.append(temp)
        # print(node_list)
    print(node_list[:3])
    centroids=initialize(node_list,3,graph)
    k_means(node_list,3,distance,centroids,graph)

def k_means(X, k, distance_func,centroids,graph,max_iters=10, tol=1e-4):
    
    old_labels=np.zeros(len(X))
    for _ in range(max_iters):
        # Assign each data point to the closest centroid using the custom distance function
        distances = np.array([[distance_func(x, c,graph) for c in centroids] for x in X])
        print(distances)
        labels = np.argmin(distances, axis=1)
        print(labels)
        new_centroids=[]
        lat_mean=0
        long_mean=0
        count=0
        for i in range(0,k):
            for j in range(0,len(labels)):
                
                if i==labels[j]:
                    count+=1
                    lat_mean=lat_mean+float(X[j][2])
                    long_mean=long_mean+float(X[j][4])
            new_centroids.append(['','Australia',lat_mean/count,'1',long_mean/count])
        if (old_labels==labels).all():
            break
        old_labels=labels
        centroids=new_centroids
    print(centroids)
    return centroids
                    
                
                
            
        
        
        
        

    


# initialization algorithm
def initialize(data, k, graph):
    '''
    initialized the centroids for K-means++
    inputs:
        data - numpy array of data points having shape (200, 2)
        k - number of clusters 
    '''
    ## initialize the centroids list and add
    ## a randomly selected data point to the list
    data=np.array(data)
    centroids = []
    centroids.append(data[np.random.randint(
            data.shape[0]), :])
    # plot(data, np.array(centroids))
  
    ## compute remaining k - 1 centroids
    for c_id in range(k - 1):
         
        ## initialize a list to store distances of data
        ## points from nearest centroid
        dist = []
        for i in range(data.shape[0]):
            point = data[i, :]
            d = sys.maxsize
             
            ## compute distance of 'point' from each of the previously
            ## selected centroid and store the minimum distance
            for j in range(len(centroids)):
                temp_dist = distance(point, centroids[j],graph)
                d = min(d, temp_dist)
            dist.append(d)
             
        ## select data point with maximum distance as our next centroid
        dist = np.array(dist)
        next_centroid = data[np.argmax(dist), :]
        centroids.append(next_centroid)
        dist = []
        # plot(data, np.array(centroids))
    return centroids
  











    
if __name__=="__main__":
    file_data=read_file('gml')
    convert_to_graph(file_data)