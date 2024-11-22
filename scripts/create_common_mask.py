import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
import numpy as np
import geopandas as gpd
import argparse

# Function to read and resample raster
def read_and_resample(file_path, transform, width, height):
    with rasterio.open(file_path) as src:
        # Create an empty array for the resampled data
        resampled_data = np.empty((src.count, height, width), dtype=src.dtypes[0])
        # Loop over each band in the raster
        for band_index in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, band_index),
                destination=resampled_data[band_index - 1],
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=src.crs,
                resampling=Resampling.bilinear
            )
        # Return the resampled data, CRS, and nodata value
        return resampled_data, src.crs, src.nodata

def calculate_common_bounds_overlap(tif_files):
    common_bounds = None
    for file_path in tif_files:
        with rasterio.open(file_path) as src:
            bounds = src.bounds
        if common_bounds is None:
            common_bounds = bounds
        else:
            common_bounds = rasterio.coords.BoundingBox(
                left = max(common_bounds.left, bounds.left),
                bottom = max(common_bounds.bottom, bounds.bottom),
                right = min(common_bounds.right, bounds.right),
                top = min(common_bounds.top, bounds.top),
            )
    return common_bounds

def calculate_alaska_bounds():
    canadaAlaska = "/projects/arctic/share/ABoVE_Biomass/OtherSpatialDatasets/CanadaAlaska_Boundaries.shp"
    shapes = gpd.read_file(canadaAlaska)
    bounds = shapes.iloc[-1]['geometry'].bounds
    return bounds

def create_na_mask(type):

    if type == "Canada":
        # Paths not included:
            # Kraatz: Way too small
            # Wang: Doesnt cover that much of the area
            # Xu: Resolution is jsut too high
        # These are the file paths we should use for the Canada region
        file_paths = ["/projects/arctic/share/ABoVE_Biomass/Duncanson2023/Duncanson2023_102001.tif", 
                        "/projects/arctic/share/ABoVE_Biomass/Guindon2023/Guindon2023_102001.tif",
                        "/projects/arctic/share/ABoVE_Biomass/Matasci2018/matasci_102001.tif",
                        "/projects/arctic/share/ABoVE_Biomass/Soto-Navarro2020/Soto2020_102001.tif",
                        "/projects/arctic/share/ABoVE_Biomass/SpawnGibbs2020/SpawnGibbs2020_mask_102001.tif"]
        # Calculate common bound based on where they all overlap
        target_shape = calculate_common_bounds_overlap(file_paths)
        
    elif type == "Alaska":
        # These are the file paths we should use for the Alaska region
        file_paths = ["/projects/arctic/share/ABoVE_Biomass/Duncanson2023/Duncanson2023_102001.tif", 
                        "/projects/arctic/share/ABoVE_Biomass/Soto-Navarro2020/Soto2020_102001.tif",
                      "/projects/arctic/share/ABoVE_Biomass/SpawnGibbs2020/SpawnGibbs2020_mask_102001.tif"]
        #target_shape = calculate_alaska_bounds()
        target_shape = calculate_common_bounds_overlap(file_paths)

    # Set desired resolution and inirialize common NA array
    resolution = 300 # Use corsest resolution (exluding Xu)
    width = int((target_shape[2] - target_shape[0]) / resolution)
    height = int((target_shape[3] - target_shape[1]) / resolution)
    transform = rasterio.transform.from_bounds(*target_shape, width, height)
    common_na_mask = np.zeros((height, width), dtype=bool)

    # Resample each tif file and get the data for NA
    for path in file_paths:
        resampled_data, crs, nodata = read_and_resample(path, transform, width, height)
        # True where there is an NA in the current resampled raster
        common_na_mask |= np.all((np.isnan(resampled_data) | (resampled_data == nodata)), axis=0)

    # Save the common NA mask
    mask_profile = {
        'driver': 'GTiff',
        'dtype': 'uint8',
        'count': 1,
        'height': height,
        'width': width,
        'transform': transform,
        'crs': crs}
    with rasterio.open(f"/projects/arctic/share/ABoVE_Biomass/OtherSpatialDatasets/CommonNA_{type}_Mask.tif", "w", **mask_profile) as mask_dst:
        mask_dst.write(common_na_mask.astype(np.uint8), 1)

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Common NA Mask Script")
    parser.add_argument('--type', type=str, choices=['Alaska', 'Canada'], required=True, help="Type of script to run (Alaska or Canada)")
    args = parser.parse_args()

    # Run script
    create_na_mask(args.type)
    