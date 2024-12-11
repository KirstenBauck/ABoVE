#!/bin/bash
#SBATCH --job-name=gdal_bigtiff_conversion
#SBATCH --output=gdal_conversion_%j.log
#SBATCH --time=05:00:00         # Set a suitable time limit
#SBATCH --ntasks=1             # Number of tasks (processes)
#SBATCH --cpus-per-task=16      # Number of CPU cores per task
#SBATCH --mem=64GB              # Memory allocation per node/task

module load gdal/3.7.2                # Load the GDAL module (if necessary)

gdal_translate -of GTiff -co BIGTIFF=YES /projects/arctic/share/ABoVE_Biomass/Duncanson2023/Duncanson2023_102001.tif /projects/arctic/share/ABoVE_Biomass/Duncanson2023/Duncanson2023_102001_bigtiff.tif

gdal_translate -of GTiff -co BIGTIFF=YES /projects/arctic/share/ABoVE_Biomass/Matasci2018/matasci_102001.tif /projects/arctic/share/ABoVE_Biomass/Matasci2018/matasci_102001_bigtiff.tif
