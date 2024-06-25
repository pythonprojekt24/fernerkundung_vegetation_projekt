import geopandas as gpd
from shapely.geometry import LineString
import rasterio
import numpy as np
import matplotlib.pyplot as plt

# Define the coordinates for Munich and Mantova
munich_coords = (11.5820, 48.1351)  # (longitude, latitude)
mantova_coords = (10.7925, 45.1562)  # (longitude, latitude)

# Create a LineString from Munich to Mantova
line = LineString([munich_coords, mantova_coords])

# Load the DGM (Digital Elevation Model) raster
dgm_path = 'path_to_your_dgm_file.tif'
dgm_raster = rasterio.open(dgm_path)

# Load the End of Season raster with a time dimension
eos_path = 'path_to_your_eos_file.tif'
eos_raster = rasterio.open(eos_path)

# Extract coordinates along the line
num_points = 100  # Number of points to sample along the line
coords = [(line.interpolate(float(i) / (num_points - 1), normalized=True).x,
           line.interpolate(float(i) / (num_points - 1), normalized=True).y)
          for i in range(num_points)]

# Extract DGM values along the line
dgm_values = []

for coord in coords:
    row, col = dgm_raster.index(*coord)
    dgm_value = dgm_raster.read(1)[row, col]
    dgm_values.append(dgm_value)

# Initialize a list to store EOS values for each time step
eos_values = []

# Extract End of Season values along the line for each time step
for t in range(eos_raster.count):
    eos_values_time = []
    for coord in coords:
        row, col = eos_raster.index(*coord)
        eos_value = eos_raster.read(t + 1)[row, col]  # Read the layer corresponding to time step t
        eos_values_time.append(eos_value)
    eos_values.append(eos_values_time)

# Create an array of distances along the line
distances = np.linspace(0, line.length, num_points)

# Plotting the profile line with distances on the x-axis
fig, ax1 = plt.subplots()

# Plot DGM values (static) as a line
color = 'tab:blue'
ax1.set_xlabel('Distance (m)')
ax1.set_ylabel('Elevation (m)', color=color)
ax1.plot(distances, dgm_values, color=color, label='Elevation')
ax1.tick_params(axis='y', labelcolor=color)

# Create a second y-axis to plot EOS values
ax2 = ax1.twinx()
color = 'tab:green'
ax2.set_ylabel('End of Season Value', color=color)

# Plot EOS values for each time step
for i, eos_values_time in enumerate(eos_values):
    ax2.plot(distances, eos_values_time, color=color, alpha=0.5, label=f'EOS Time step {i}')
    
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.title('Profile Line from Munich to Mantova')
fig.legend(loc='upper right')
plt.show()

print("Profile line created successfully!")






# # Define the coordinates for Munich and Mantova
# munich_coords = (11.5820, 48.1351)  # (longitude, latitude)
# mantova_coords = (10.7925, 45.1562)  # (longitude, latitude)

# # Create a LineString from Munich to Mantova
# line = LineString([munich_coords, mantova_coords])

# # Load the raster data
# raster_path = 'path_to_your_raster_file.tif'
# raster = rasterio.open(raster_path)

# # Extract raster values along the line
# coords = [(x, y) for x, y in zip(*line.xy)]
# values = []

# for coord in coords:
#     row, col = raster.index(*coord)
#     value = raster.read(1)[row, col]
#     values.append(value)

# # Optionally, plot the values
# plt.plot(values)
# plt.xlabel('Point along the line')
# plt.ylabel('Raster value')
# plt.title('Raster values along the line from Munich to Mantova')
# plt.show()

# print("Raster values extracted successfully!")

########################## Hier ist die zeitl. Ebene noch nicht drinnen
# import geopandas as gpd
# from shapely.geometry import LineString
# import rasterio
# import numpy as np
# import matplotlib.pyplot as plt

# # Define the coordinates for Munich and Mantova
# munich_coords = (11.5820, 48.1351)  # (longitude, latitude)
# mantova_coords = (10.7925, 45.1562)  # (longitude, latitude)

# # Create a LineString from Munich to Mantova
# line = LineString([munich_coords, mantova_coords])

# # Load the DGM (Digital Elevation Model) raster
# dgm_path = 'path_to_your_dgm_file.tif'
# dgm_raster = rasterio.open(dgm_path)

# # Load the End of Season raster
# eos_path = 'path_to_your_end_of_season_file.tif'
# eos_raster = rasterio.open(eos_path)

# # Extract coordinates along the line
# num_points = 100  # Number of points to sample along the line
# coords = [(line.interpolate(float(i) / (num_points - 1), normalized=True).x,
#            line.interpolate(float(i) / (num_points - 1), normalized=True).y)
#           for i in range(num_points)]

# # Extract DGM and End of Season values along the line
# dgm_values = []
# eos_values = []

# for coord in coords:
#     row, col = dgm_raster.index(*coord)
#     dgm_value = dgm_raster.read(1)[row, col]
#     eos_value = eos_raster.read(1)[row, col]
#     dgm_values.append(dgm_value)
#     eos_values.append(eos_value)

# # Create a distance array for the x-axis
# distances = np.linspace(0, line.length, num_points)

# # Plotting the profile line
# fig, ax1 = plt.subplots()

# # Plot DGM values
# color = 'tab:blue'
# ax1.set_xlabel('Distance (m)')
# ax1.set_ylabel('Elevation (m)', color=color)
# ax1.plot(distances, dgm_values, color=color)
# ax1.tick_params(axis='y', labelcolor=color)

# # Create a second y-axis to plot EOS values
# ax2 = ax1.twinx()
# color = 'tab:green'
# ax2.set_ylabel('End of Season Value', color=color)
# ax2.plot(distances, eos_values, color=color)
# ax2.tick_params(axis='y', labelcolor=color)

# fig.tight_layout()
# plt.title('Profile Line from Munich to Mantova')
# plt.show()

# print("Profile line created successfully!")

