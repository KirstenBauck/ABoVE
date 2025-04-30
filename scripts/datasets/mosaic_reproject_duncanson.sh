#!/bin/bash
#SBATCH --job-name=mosaic_reproject_duncanson       # Job name
#SBATCH --output=mosaic_reproject_duncanson_%j.out  # Standard output and error log
#SBATCH --ntasks=1                                  # Number of tasks
#SBATCH --cpus-per-task=32                          # Number of CPU cores per task
#SBATCH --time=10:00:00                             # Walltime
#SBATCH --mem=512G                                  # Memory per node

# Load necessary modules
module load gdal/3.7.2

directory="/projects/arctic/share/ABoVE_Biomass"

# Mosaic - Need a directory of all tiles
gdalbuildvrt "$directory/Duncanson2025/mosaic.vrt" \
    "$directory/Duncanson2025/duncanson_tiles/*.tif"
gdal_translate -of GTiff -co COMPRESS=LZW -co BIGTIFF=YES -co TILED=YES \
    "$directory/Duncanson2025/mosaic.vrt" \
    "$directory/Duncanson2025/Duncanson2025_ABoVE_merged.tif"

# Reproject
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co BIGTIFF=YES -co TILED=YES \
    "$directory/Duncanson2025/Duncanson2025_ABoVE_merged.tif" \
    "$directory/Duncanson2025/Duncanson2025_epsg4326.tif"
gdal_translate -of VRT -projwin -170 85 -50 40 \
    "$directory/Duncanson2025/Duncanson2025_epsg4326.tif" \
    "$directory/Duncanson2025/subset_esri.vrt"
gdalwarp -t_srs "ESRI:102001" -dstnodata -9999 -co COMPRESS=LZW \
    -co BIGTIFF=YES -co TILED=YES "$directory/Duncanson2025/subset_esri.vrt" \
    "$directory/Duncanson2025/Duncanson2025_102001.tif"

# Make into a bigtiff for better memory usage
gdal_translate -of GTiff -co BIGTIFF=YES -co COMPRESS=LZW -co TILED=YES \
    "$directory/Duncanson2025/Duncanson2025_102001.tif" \
    "$directory/Duncanson2025/Duncanson2025_102001.tif"