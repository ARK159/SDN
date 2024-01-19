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


def main(mininet_topology, file_data):
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

    second_derivative = np.diff(np.diff(wcss))
    optimal_k = np.argmax(second_derivative) + 2

    cent = initialize(node_list, optimal_k, graph)
    centroids, labels, wcs = k_means(node_list, optimal_k, distance, cent, graph)

    latitude = [float(c[2]) for c in node_list]
    longitude = [float(c[4]) for c in node_list]
    c_latitude = [float(c[2]) for c in centroids]
    c_longitude = [float(c[4]) for c in centroids]

  

    plt.scatter(longitude, latitude, c=labels)
    plt.scatter(c_longitude, c_latitude, color='red', label='Centroids')  # Plot centroids
    plt.scatter([float(c[4]) for c in centroids], [float(c[2]) for c in centroids], color='blue', label='Controllers')  # Plot controllers
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.show()

    # Assign controllers before calling create_mininet_topology
    num_controllers = 4
    controller_assignments = assign_controllers(labels, num_controllers)

    # Print the coordinates of controllers
    mininet_topology, controller_names = create_mininet_topology(mininet_topology, graph, controller_assignments, centroids)  # Fix the function call
    for i, controller_name in enumerate(controller_names):
        controller_lat = float(centroids[i][2])
        controller_long = float(centroids[i][4])
        print(f"Controller {controller_name} coordinates: Latitude {controller_lat}, Longitude {controller_long}")
    # Continue with the remaining code
    print(controller_assignments)

    # Use the returned mininet_topology instance
    mininet_topology.build()
    CLI(mininet_topology)
    mininet_topology.stop()


def assign_controllers(labels, num_controllers):
    controller_assignments = {}
    for i in range(len(labels)):
        cluster_id = labels[i]
        controller_assignments[f'switch{i + 1}'] = f'c{cluster_id % num_controllers}'

    return controller_assignments



def create_mininet_topology(net, graph, controller_assignments, centroids):
    # Extract unique controller names from the assignments
    controller_names = set(controller_assignments.values())

    # Assign unique IP addresses to controllers
    controller_ips = ['127.0.0.{}'.format(i + 1) for i in range(len(controller_names))]
    print("Controller IPs:", controller_ips)
    print("Controller Names:", controller_names)

    # Iterate through each unique controller name and add a RemoteController instance with a unique IP
    for i, controller_name in enumerate(controller_names):
        controller = net.addController(controller_name, controller=RemoteController, ip=controller_ips[i], port=6633)

        # Set the controller's position to the centroid coordinates
        controller_lat = float(centroids[i][2])
        controller_long = float(centroids[i][4])
        controller.params['lat'] = controller_lat
        controller.params['long'] = controller_long

    # Create switches based on controller assignments
    switches = {}
    for switch_id, controller_id in controller_assignments.items():
        switches[switch_id] = net.addSwitch(switch_id, cls=OVSKernelSwitch)

    # Connect switches based on graph edges
    for edge in graph.edges():
        switch_id1, switch_id2 = edge
        if switch_id1 in switches and switch_id2 in switches:
            net.addLink(switches[switch_id1], switches[switch_id2])

    # Assign unique IP addresses to hosts
    host_ips = ['10.0.0.{}'.format(i + 1) for i in range(len(controller_assignments) * 2)]

    # Add hosts to the Mininet topology with unique IP addresses
    hosts = [net.addHost('h{}'.format(i + 1), cls=Host, ip=host_ips[i]) for i in range(len(host_ips))]

    # Connect switches to hosts
    for switch_id, controller_id in controller_assignments.items():
        for i in range(2):
            host_index = int(switch_id[6:]) * 2 + i
            if host_index < len(hosts):
                net.addLink(switches[switch_id], hosts[host_index])

        # Start the switch with its assigned controller
        net.get(switch_id).start([net.get(controller_id)])
        print("Switch {} connected to Controller {}".format(switch_id, controller_id))

    return net, controller_names
   





if __name__ == "__main__":
    setLogLevel('info')
    file_data = read_file('file.gml')
    mininet_topology = Mininet(topo=None, build=False)
    main(mininet_topology, file_data)
