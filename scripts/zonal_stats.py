# Import libraries
import argparse
import os
from multiprocessing import Pool
import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask
from shapely.geometry import shape
from shapely.geometry import box

def process_zone(zone_row, src, file_type, coverage_ratio):
    geometry = zone_row['geometry']
    if file_type == 'CanadaAlaska':
        zone_name = zone_row['postal']
    elif file_type == 'EPA2':
        zone_name = zone_row['NA_L2KEY']

    # Mask raster by geometry
    with rasterio.open(src) as file:
        # Check for intersection first
        file_bounds = box(*file.bounds)
        if not file_bounds.intersects(box(*geometry.bounds)):
            print(f"Shape {zone_name} does not intersect raster, skipping.")
            return (zone_name, None, None, None, None)
        try:
            out_image, out_transform = mask(file, [geometry], crop=True)
            no_data_value = file.nodata
            pixel_area = file.res[0] * file.res[1]
        except ValueError as e:
            print(f"Error processing {zone_name}: {e}")
            return (zone_name, None, None, None, None)

    # Flatten, remove NoData, calculate percentage of shape covered by valid data
    out_image = out_image.flatten()
    if np.isnan(no_data_value):
        valid_data = out_image[~np.isnan(out_image)]
    else:
        valid_data = out_image[out_image != no_data_value]
    valid_pixels = valid_data.size
    valid_area = valid_pixels * pixel_area
    geometry_area = geometry.area
    actual_cover = valid_area / geometry_area

    # Calculate statistics
    if actual_cover >= float(coverage_ratio):
        mean = np.nanmean(valid_data)
        median = np.nanmedian(valid_data)
        sum = np.nansum(valid_data)
        std = np.nanstd(valid_data)
        return (zone_name, mean, median, sum, std)
    print(f"Did not include {zone_name} because coverage ratio was {actual_cover}")
    return (zone_name, None, None, None, None)

def calculate_zonal_stats_parallel(raster_file, shapefile, output_file, file_type, coverage_ratio):
    print(f"Looking at dataset: {raster_file}")
    shapes = gpd.read_file(shapefile)
    
    # Use multiprocessing to process zones in parallel
    with Pool() as pool:
        results = pool.starmap(process_zone, [(row, raster_file, file_type, coverage_ratio) for _, row in shapes.iterrows()])

    # Write results to a file
    with open(output_file, 'w') as f:
        f.write("Zone, Mean, Median, Sum, Std \n")
        for result in results:
            f.write(f"{result[0]}, {result[1]}, {result[2]}, {result[3]}, {result[4]} \n")

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="Zonal Statistics Calculation Script")
    parser.add_argument('--infile', type=str, required=True, help="Path to input raster file")
    parser.add_argument('--script_type', type=str, choices=['EPA2', 'CanadaAlaska'], required=True, help="Type of script to run (EPA2 or CanadaAlaska)")
    parser.add_argument('--coverage_ratio', type=float, required=True, help="Coverage rati (number 0-1)")
    args = parser.parse_args()

    # Check which type of script to run
    if args.script_type == 'EPA2':
        shapefile = "/projects/arctic/share/ABoVE_Biomass/OtherSpatialDatasets/EPA_ecoregion_lvl2_clipped_102001.shp"
    elif args.script_type == 'CanadaAlaska':
        shapefile = "/projects/arctic/share/ABoVE_Biomass/OtherSpatialDatasets/CanadaAlaska_Boundaries_102001.shp"
    
    coverage_ratio_percent = int(args.coverage_ratio * 100)
    
    # Create output file name
    directory = os.path.dirname(args.infile)
    folder_name = os.path.basename(directory)
    output_file = f"zonal_stats_{args.script_type}_{folder_name}_{coverage_ratio_percent}.txt"

    # Run parallel zonal stats and write to file
    calculate_zonal_stats_parallel(args.infile, shapefile, output_file, args.script_type, args.coverage_ratio)
