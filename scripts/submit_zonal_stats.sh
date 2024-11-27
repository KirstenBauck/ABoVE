#!/bin/bash
#SBATCH --job-name=zonal_stats_job      # Job name
#SBATCH --output=zonal_stats_%j.out     # Standard output and error log (%j will be replaced by the job ID)
#SBATCH --ntasks=1                      # Number of tasks
#SBATCH --cpus-per-task=32              # Number of CPU cores per task
#SBATCH --time=12:00:00                 # Walltime
#SBATCH --mem=512G                      # Memory per node

# Load necessary modules
source /packages/anaconda3/2024.02/etc/profile.d/conda/sh
module load anaconda3/2024.02 
module load gdal/3.7.2
conda activate ABoVE2024  

# Check for command-line arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: sbatch submit_zonal_stats.sh <input_raster_file> <script_type> <coverage_ratio>"
    exit 1
fi

# Positional arguments from the sbatch command
infile=$1
script_type=$2
coverage_ratio=$3

# Run the Python script with the provided arguments
python3 zonal_stats.py --infile "$infile" --script_type "$script_type" --coverage_ratio $coverage_ratio