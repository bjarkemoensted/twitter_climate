import os

_here = os.path.abspath(os.path.dirname(__file__))

data_dir = os.path.join(_here, "data")
climate_data_file = os.path.join(data_dir, "climate_raw.p")

climate_results_filename = "climate_results.xlsx"
climate_results_file = os.path.join(data_dir, climate_results_filename)

network_path = r"H:/Alle/data_sharing/"
climate_results_file_network = os.path.join(network_path, climate_results_filename)
