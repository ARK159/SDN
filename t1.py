
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
