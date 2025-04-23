#!/bin/bash
#SBATCH --job-name=create_common_na_mask        # Job name
#SBATCH --output=create_common_na_mask_%j.out   # Standard output and error log
#SBATCH --ntasks=1                              # Number of tasks
#SBATCH --cpus-per-task=32                      # Number of CPU cores per task
#SBATCH --time=06:00:00                         # Walltime
#SBATCH --mem=512G                              # Memory per node

# Load necessary modules
source /packages/anaconda3/2024.02/etc/profile.d/conda/sh
module load anaconda3/2024.02 
conda activate ABoVE2024  

# Check for command-line arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: sbatch submit_na_mask.sh <type>"
    exit 1
fi

# Positional arguments from the sbatch command
type=$1

# Run the Python script with the provided arguments
python3 create_common_mask.py --type "$type"