#!/bin/bash
#SBATCH --job-name=download_duncanson       # Job name
#SBATCH --output=download_duncanson_%j.out  # Standard output and error log
#SBATCH --ntasks=1                          # Number of tasks
#SBATCH --cpus-per-task=32                  # Number of CPU cores per task
#SBATCH --time=72:00:00                     # Walltime
#SBATCH --mem=256G                          # Memory per node

# Load necessary modules
source /packages/anaconda3/2024.02/etc/profile.d/conda/sh
module load anaconda3/2024.02 
conda activate ABoVE2024

python3 download_duncanson.py