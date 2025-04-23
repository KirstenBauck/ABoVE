#!/bin/bash
#SBATCH --job-name=combined_mask                # Job name
#SBATCH --output=combined_mask_%j.out           # Standard output and error log
#SBATCH --ntasks=1                              # Number of tasks
#SBATCH --cpus-per-task=32                      # Number of CPU cores per task
#SBATCH --time=01:00:00                         # Walltime
#SBATCH --mem=512G                              # Memory per node

# Load necessary modules
source /packages/anaconda3/2024.02/etc/profile.d/conda/sh
module load anaconda3/2024.02 
conda activate ABoVE2024  

# Run the Python script with the provided arguments
python3 combined_mask.py
