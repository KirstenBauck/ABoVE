import requests
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds
from rasterio.crs import CRS
import os
from bs4 import BeautifulSoup

# TODO: order data to be downloaded at https://daac.ornl.gov/ABOVE/guides/Boreal_AGB_Density_ICESat2.html
# Then replace URL with current download link
url = "https://daac.ornl.gov/orders/d26d750cd503ca71fbc30e2caa67c03f/download_links.html"

# ABoVE data region bounds (approximate): Alaska and parts of Canada
min_lat, max_lat = 	45, 75
min_lon, max_lon = -180, -50

# Directory to save the relevant .tif files
output_dir = "../data/Duncanson2023"
os.makedirs(output_dir, exist_ok=True)

# Function to check if a raster is in the ABoVE region based on its bounds
def is_within_above_region(bounds):
    left, bottom, right, top = bounds
    return (
        min_lat <= bottom <= max_lat and min_lat <= top <= max_lat and
        min_lon <= left <= max_lon and min_lon <= right <= max_lon
    )

# Fetch the HTML page content
response = requests.get(url)
response.raise_for_status()

# Parse the HTML content for links to .tif files
soup = BeautifulSoup(response.text, "html.parser")
tif_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.tif')]

# Process each .tif file link
for link in tif_links:
    file_name = os.path.join(output_dir, os.path.basename(link))

    # Check if file already exists
    if os.path.exists(file_name):
        print(f"{file_name} already exists, skipping download.")
        continue

    print(f"Checking {link}...")
    file_response = requests.get(link, stream=True)
    file_response.raise_for_status()
    
    # Load entire file into memory
    with MemoryFile(file_response.content) as memfile:
        try:
            with memfile.open() as dataset:
                original_bounds = dataset.bounds
                original_crs = dataset.crs

                bounds_epsg4326 = transform_bounds(original_crs, 
                                                    CRS.from_epsg(4326), 
                                                    original_bounds.left, 
                                                    original_bounds.bottom, 
                                                    original_bounds.right, 
                                                    original_bounds.top)

                # Check if dataset's bounds are within the ABoVE region
                if is_within_above_region(bounds_epsg4326):
                    print(f"File within ABoVE region; saving to {file_name}")
                    
                    # Save file to disk
                    with open(file_name, "wb") as out_file:
                        out_file.write(file_response.content)
                else:
                    print(f"File outside ABoVE region; skipping download.")
        except rasterio.errors.RasterioIOError:
            print(f"Could not open {link} - skipping due to read error.")