#!/bin/bash
#SBATCH --job-name=mosaic_reproject_duncanson       # Job name
#SBATCH --output=mosaic_reproject_duncanson_%j.out  # Standard output and error log
#SBATCH --ntasks=1                                  # Number of tasks
#SBATCH --cpus-per-task=32                          # Number of CPU cores per task
#SBATCH --time=10:00:00                             # Walltime
#SBATCH --mem=512G                                  # Memory per node

# Load necessary modules
module load gdal/3.7.2

# Mosaic
gdalbuildvrt /projects/arctic/share/ABoVE_Biomass/Duncanson2025/mosaic.vrt /projects/arctic/share/ABoVE_Biomass/Duncanson2025/duncanson_tiles/*.tif
gdal_translate -of GTiff -co COMPRESS=LZW -co BIGTIFF=YES -co TILED=YES /projects/arctic/share/ABoVE_Biomass/Duncanson2025/mosaic.vrt /projects/arctic/share/ABoVE_Biomass/Duncanson2025/Duncanson2025_ABoVE_merged.tif

# Reproject
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co BIGTIFF=YES -co TILED=YES /projects/arctic/share/ABoVE_Biomass/Duncanson2025/Duncanson2025_ABoVE_merged.tif /projects/arctic/share/ABoVE_Biomass/Duncanson2025/Duncanson2025_epsg4326.tif
gdal_translate -of VRT -projwin -170 85 -50 40 /projects/arctic/share/ABoVE_Biomass/Duncanson2025/Duncanson2025_epsg4326.tif /projects/arctic/share/ABoVE_Biomass/Duncanson2025/subset_esri.vrt
gdalwarp -t_srs "ESRI:102001" -dstnodata -9999 -co COMPRESS=LZW -co BIGTIFF=YES -co TILED=YES /projects/arctic/share/ABoVE_Biomass/Duncanson2025/subset_esri.vrt /projects/arctic/share/ABoVE_Biomass/Duncanson2025/Duncanson2025_102001.tif

# Make into a bigtiff for better memory usage
gdal_translate -of GTiff -co BIGTIFF=YES -co COMPRESS=LZW -co TILED=YES \
    /projects/arctic/share/ABoVE_Biomass/Duncanson2025/Duncanson2025_102001.tif \
    /projects/arctic/share/ABoVE_Biomass/Duncanson2025/Duncanson2025_BigTIFF.tif