#!/bin/bash
#SBATCH --job-name=reproject_datasets          # Job name
#SBATCH --output=reproject_datasets_%j.out     # Standard output and error log
#SBATCH --ntasks=1                             # Number of tasks
#SBATCH --cpus-per-task=16                     # Number of CPU cores per task
#SBATCH --time=12:00:00                        # Walltime
#SBATCH --mem=512G                             # Memory per node

# Load necessary modules
module load gdal/3.7.2

directory="/projects/arctic/share/ABoVE_Biomass"

#Duncanson2025
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co BIGTIFF=YES -co TILED=YES \
    "$directory/Duncanson2025/Duncanson2025_BigTIFF_masked_Combined.tif" \
    "$directory/Duncanson2025/Duncanson2025_BigTIFF_masked_Combined_4326.tif"

# Guindon2023
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co TILED=YES \
    "$directory/Guindon2023/Guindon2023_102001_masked_Canada.tif" \
    "$directory/Guindon2023/Guindon2023_4326_masked_Canada.tif"

#Matasci2018
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co BIGTIFF=YES -co TILED=YES \
    "$directory/Matasci2018/matasci_102001_bigtiff_masked_Canada.tif" \
    "$directory/Matasci2018/matasci_4326_bigtiff_masked_Canada.tif"

# Soto-Navarro2020
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co TILED=YES \
    "$directory/Soto-Navarro2020/Soto2020_102001_masked_Combined.tif" \
    "$directory/Soto-Navarro2020/Soto2020_4326_masked_Combined.tif"

# Spawn Gibbs
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co TILED=YES \
    "$directory/SpawnGibbs2020/SpawnGibbs2020_mask_102001_masked_Combined.tif" \
    "$directory/SpawnGibbs2020/SpawnGibbs2020_mask_4326_masked_Combined.tif"

# Wang 2020
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co TILED=YES \
    "$directory/Wang2020/Wang102001_masked_ABoVE.tif" \
    "$directory/Wang2020/Wang4326_masked_ABoVE.tif"

# Xu 2021
gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -co TILED=YES \
    "$directory/Xu2021/Xu2021_102001_masked_Combined.tif" \
    "$directory/Xu2021/Xu2021_4326_masked_Combined.tif"

