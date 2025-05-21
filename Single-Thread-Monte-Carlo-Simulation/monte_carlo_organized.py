import matplotlib.pyplot as plt
from typing import Dict, Any, Tuple
import time

from Utilities import NetworkMap

from Simulation import MonteCarloSimulation

from Utilities import visualize_combined_simulation_results, plot_deliveries_per_rain_intensity_combined



if __name__ == '__main__':
   
    try:
        
        place_query = "La Trinidad, Benguet, Philippines"


        """
        ============================================================================================================================================
        🛠️ Initialize and Download Map
        ============================================================================================================================================
        """

        serial_section_start = time.time()

        # Initialize NetworkMap class to process place query
        Network_Map_Instance = NetworkMap(place_query)

        # Download place query using osmnx
        Network_Map_Instance.download_map()
        
        # Convert to NetworkX for analysis
        Network_Map_Instance.network_to_networkx()

        start_node, delivery_nodes = Network_Map_Instance.select_fixed_points(num_delivery_points=20)
        print(f"Start node is: {start_node}")
        print(f"Delivery nodes are: {delivery_nodes}")

        # Find route using nearest neighbor
        route, total_distance, path_sequence = Network_Map_Instance.nearest_neighbor_route()
        
        # Calculate ideal travel time
        Network_Map_Instance.calculate_travel_time(total_distance)

        print(f"Total distance: {total_distance:.2f} meters")
        print(f"Total travel time: {Network_Map_Instance.ideal_delivery_time:.2f} minutes")

        # Initialize random disaster prone nodes
        landslide_prone, flood_prone = Network_Map_Instance.initialize_edge_disaster_attributes()
        

        print(f"Total number of edges: {len(list(Network_Map_Instance.G.edges))}")
        print(f"Number of Landslide prone edges: {len(landslide_prone)}, Number of flood prone edges: {len(flood_prone)}")
        
        serial_section_end = time.time()

        serial_section_time = serial_section_end - serial_section_start

        print(f"Seriel Section time: {serial_section_time}")

        
    
        # Visualize the delivery route
        # fig, ax = Network_Map_Instance.visualize_delivery_route()
        # plt.show()

        # fig, ax = Network_Map_Instance.visualize_delivery_route_with_disaster(landslide_prone, flood_prone)
        # plt.show()



        """
        =============================================================================================================================================
        🚀 Run Simulations
        =============================================================================================================================================
        """
        parallelizable_section_start  = time.time()

        NUM_SIMULATIONS = 100

        simulation_runs = []
        for weather_severity in range(1,6):
            singe_simulation_start_time = time.time()
            simulation = MonteCarloSimulation(
                            Network_Map_Instance.G, 
                            Network_Map_Instance.start_node, 
                            Network_Map_Instance.delivery_nodes, 
                            Network_Map_Instance.ideal_delivery_time)

            
            simulation.run_simulation(num_simulations=NUM_SIMULATIONS, weather_severity=weather_severity)
            

            success_times = [result['time'] for result in simulation.simulation_results['all_runs'] if result['success']]
            failure_times = [0 for result in simulation.simulation_results['all_runs'] if not result['success']]

            print(f"Number of successful runs {len(success_times)} Number of failed deliverier {len(failure_times)}")

            simulation_runs.append(simulation)

        parallelizable_section_end  = time.time()


        parallelizable_section_time = parallelizable_section_end - parallelizable_section_start

        print(f"Parallelizable Section time: {parallelizable_section_time}")

        total_time = serial_section_time + parallelizable_section_time
        print(f"Elapsed time: {total_time} seconds")


        plot_deliveries_per_rain_intensity_combined(simulation_runs)
        visualize_combined_simulation_results(simulation_runs)



    except Exception as e:
        print(f"Error during main function execution: {e}")


