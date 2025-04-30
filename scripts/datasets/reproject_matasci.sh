#!/bin/bash
#SBATCH --job-name=reproject_matasci        # Job name
#SBATCH --output=reproject_matasci_%j.out   # Standard output and error log
#SBATCH --ntasks=1                          # Number of tasks
#SBATCH --cpus-per-task=32                  # Number of CPU cores per task
#SBATCH --time=03:00:00                     # Walltime
#SBATCH --mem=512G                          # Memory per node

# Load necessary modules
module load gdal/3.7.2

directory="/projects/arctic/share/ABoVE_Biomass"

# Reproject
gdalwarp -t_srs ESRI:102001 -co COMPRESS=LZW -co BIGTIFF=YES -co TILED=YES \
    "$directory/Matasci2018/matasci_4326.tif" \
    "$directory/Matasci2018/matasci_102001.tif"

# Make into a bigtif for better memory
gdal_translate -of GTiff -co BIGTIFF=YES "$directory/Matasci2018/matasci_102001.tif" \
 "$directory/Matasci2018/matasci_102001_bigtiff.tif"