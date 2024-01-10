from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.link import TCLink
import networkx as nx
import numpy as np
import sys
import math
import pandas as pd
import matplotlib.pyplot as plt
from mininet.log import setLogLevel


setLogLevel('info')

def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def haversine_distance(lat1, lon1, lat2, lon2):
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0
    a = (pow(math.sin(dLat / 2), 2) +
         pow(math.sin(dLon / 2), 2) *
         math.cos(lat1) * math.cos(lat2))
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return abs(rad * c)

def distance(p1, p2, graph, centroids):
    lat1 = float(p1[2])
    long1 = float(p1[4])
    lat2 = float(p2[2])
    long2 = float(p2[4])
    CC_time = 0
    for c in centroids:
        CC_distance = haversine_distance(float(c[2]), float(c[4]), lat2, long2)
        CC_time += (CC_distance / (10 * 1000))
    delay = graph.get_edge_data(p1[0], p2[0])

    link_label = 1
    if delay is None:
        link_label = 1e-10
    else:
        if 'LinkLabel' in delay.keys():
            link_label = delay['LinkLabel']
            link_label = link_label.replace("<", "")
            if "Gbps" in link_label:
                link_label = float(link_label.replace("Gbps", "")) * 1000
            elif "Mbps" in link_label:
                link_label = float(link_label.replace("Mbps", ""))
        else:
            link_label = 5 * 1000

    dist = haversine_distance(lat1, long1, lat2, long2)
    return 0.7 * (dist / link_label) + 0.3 * (CC_time)

def create_mininet_topology(graph, k):
    class CustomTopology(Topo):
        def __init__(self, graph, k, **opts):
            super(CustomTopology, self).__init__(**opts)
            self.graph = graph
            self.k = k
            switch_count = 1

            switch_names = {}
            host_count = 1
            for node_id, node_data in graph.nodes(data=True):
                switch_name = f'S{switch_count}'
                switch_dpid = format(switch_count, '016x')  # Set a unique dpid for each switch
                switch_count += 1

                switch_names[node_id] = switch_name

                self.addSwitch(switch_name, dpid=switch_dpid)

                for i in range(2):
                    host_name = f'H{host_count}'
                    host_count += 1
                    self.addHost(host_name)
                    self.addLink(host_name, switch_name)

            for edge in graph.edges(data=True):
                source, target, edge_data = edge
                link_label = edge_data.get('LinkLabel', '1Gbps')
                bandwidth = 10 if "Gbps" in link_label else (0.0025 if "Mbps" in link_label else 0.000155)
                self.addLink(switch_names[source], switch_names[target], bw=bandwidth, delay='1ms')

    topo = CustomTopology(graph, k)
    net = Mininet(topo=topo, link=TCLink)

    controllers = []
    for i in range(k):
        controller = RemoteController(f'c{i + 1}', ip='127.0.0.1', port=6653 + i)
        controllers.append(controller)
        net.addController(controller)

    # Connect switches to controllers
    for i, switch in enumerate(net.switches):
        controller_index = i % k  
        controller = controllers[controller_index]
        net.addLink(switch, controller)

    return net
def k_means(X, k, distance_func, centroids, graph, max_iters=1000, tol=1e-4):
    old_labels = np.zeros(len(X))
    for _ in range(max_iters):
        distances = np.array([[distance_func(x, c, graph, centroids) for c in centroids] for x in X])
        labels = np.argmin(distances, axis=1)
        new_centroids = []
        lat_mean = 0
        long_mean = 0
        count = 0
        for i in range(0, k):
            for j in range(0, len(labels)):
                if i == labels[j]:
                    count += 1
                    lat_mean = lat_mean + float(X[j][2])
                    long_mean = long_mean + float(X[j][4])
            if count != 0:
                new_centroids.append(['', 'Australia', lat_mean / count, '1', long_mean / count])
        if (old_labels == labels).all():
            break
        old_labels = labels
        centroids = new_centroids
    wcss = 0
    for i in range(len(labels)):
        c_d = centroids[labels[i]]
        p_d = X[i]
        wcss += distance_func(p_d, c_d, graph, centroids) ** 2
    return centroids, labels, wcss

def initialize(data, k, graph):
    data = np.array(data)
    centroids = []
    centroids.append(data[np.random.randint(data.shape[0]), :])
    for c_id in range(k - 1):
        dist = []
        for i in range(data.shape[0]):
            point = data[i, :]
            d = sys.maxsize
            for j in range(len(centroids)):
                temp_dist = distance(point, centroids[j], graph, centroids)
                d = min(d, temp_dist)
            dist.append(d)
        dist = np.array(dist)
        next_centroid = data[np.argmax(dist), :]
        centroids.append(next_centroid)
        dist = []
    return centroids

def main(file_path):
    gml_data = read_file(file_path)
    graph = nx.parse_gml(gml_data)
    
    # Find the optimal k
    node_list = []
    for node_id, node_data in graph.nodes(data=True):
        temp = [
            node_id,
            node_data.get('Country', ''),
            node_data.get('Latitude', ''),
            node_data.get('Internal', ''),
            node_data.get('Longitude', '')
        ]
        node_list.append(temp)

    wcss = []
    for k in range(1, 11):
        cent = initialize(node_list, k, graph)
        centroids, labels, wcs = k_means(node_list, k, distance, cent, graph)
        wcss.append(wcs)

    plt.plot(range(1, 11), wcss, marker='o')
    plt.title('Elbow Method for Optimal k')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Within-Cluster Sum of Squares (WCSS)')
    plt.show()

    second_derivative = np.diff(np.diff(wcss))
    optimal_k = np.argmax(second_derivative) + 2
    print(f"Optimal k: {optimal_k}")

    # Create Mininet topology
    mininet_topo = create_mininet_topology(graph, optimal_k)

    # Start Mininet
    mininet_topo.start()
    mininet_topo.pingAll()
    mininet_topo.stop()

if __name__ == "__main__":
    main('file.gml') 
