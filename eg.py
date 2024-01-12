from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, Host
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import networkx as nx
import numpy as np
import sys
import math 
import matplotlib.pyplot as plt
from mininet.node import RemoteController

 # Add this line

# Rest of your code...


def read_file(file):
    file_path = 'file.gml'  # Change this line with the correct path
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


def haversine_distance(lat1, lon1, lat2, lon2):
    # distance between latitudes and longitudes
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
    if delay == None:
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

def main(file_data):
    graph = nx.parse_gml(file_data)
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

    # Determine optimal k
    second_derivative = np.diff(np.diff(wcss))
    optimal_k = np.argmax(second_derivative) + 2

    cent = initialize(node_list, optimal_k, graph)
    centroids, labels, wcs = k_means(node_list, optimal_k, distance, cent, graph)

    # Visualize clustering
    latitude = [float(c[2]) for c in node_list]
    longitude = [float(c[4]) for c in node_list]
    c_latitude = [float(c[2]) for c in centroids]
    c_longitude = [float(c[4]) for c in centroids]

    plt.scatter(longitude, latitude, c=labels)
    plt.scatter(c_longitude, c_latitude, color='red')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

    # Assign controllers to clusters
    num_controllers = 4
    controller_assignments = assign_controllers(labels, num_controllers)
    print(controller_assignments)
    print("Controllers in Mininet topology:", net.controllers)


    # Create Mininet topology
    mininet_topology = create_mininet_topology(controller_assignments)
    mininet_topology.build()
    CLI(mininet_topology)
    mininet_topology.stop()

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

def cluster_nodes(graph):
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
    print(optimal_k)

    cent = initialize(node_list, optimal_k, graph)
    centroids, labels, wcs = k_means(node_list, optimal_k, distance, cent, graph)

    return node_list, labels


def assign_controllers(labels, num_controllers):
    controller_assignments = {}
    for i in range(len(labels)):
        cluster_id = labels[i]
        controller_assignments[f'switch{i + 1}'] = f'c{cluster_id % num_controllers}'

    return controller_assignments

def create_mininet_topology(controller_assignments):
    net = Mininet(topo=None, build=False)

    
    controller_names = set(controller_assignments.values())
    for controller_name in controller_names:
        controller = net.addController(controller_name, controller=RemoteController, ip='127.0.0.1', port=6633)

    # Create switches based on clustering
    switches = {}
    for switch_id, controller_id in controller_assignments.items():
        switches[switch_id] = net.addSwitch(switch_id, cls=OVSKernelSwitch)

    
    h1 = net.addHost('h1', cls=Host)
    h2 = net.addHost('h2', cls=Host)

    # Create links based on clustering
    for switch_id, controller_id in controller_assignments.items():
        net.addLink(switches[switch_id], h1)
        net.addLink(switches[switch_id], h2)
        net.get(switch_id).start([net.get(controller_id)])

    

    return net



if __name__ == "__main__":
    
    file_data = read_file('gml')
    graph = nx.parse_gml(file_data)
    node_list, labels = cluster_nodes(graph)
    controller_assignments = assign_controllers(labels, num_controllers=4)

    
    mininet_topology = create_mininet_topology(controller_assignments)

    

    mininet_topology.build()
    CLI(mininet_topology)
    mininet_topology.stop()


if __name__ == "__main__":
    file_data = read_file('file.gml')
    main(file_data)
