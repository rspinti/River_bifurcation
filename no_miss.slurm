#!/bin/bash

# --------------------------------------------------------------
### PART 1: Requests resources to run your job.
# --------------------------------------------------------------
### Optional. Set the job name
#SBATCH --job-name=everything_else
### Optional. Set the output filename.
### SLURM reads %x as the job name and %j as the job ID
#SBATCH --output=%x-%j.out
### REQUIRED. Specify the PI group for this job
#SBATCH --account=lecondon
### Optional. Request email when job begins and ends
### SBATCH --mail-type=ALL
### Optional. Specify email address to use for notification
### SBATCH --mail-user=<YOUR NETID>@email.arizona.edu
### REQUIRED. Set the partition for your job.
#SBATCH --partition=standard
### REQUIRED. Set the number of cores that will be used for this job.
#SBATCH --ntasks=6
### REQUIRED. Set the memory required for this job.
#SBATCH --mem=6gb
### REQUIRED. Specify the time required for this job, hhh:mm:ss
#SBATCH --time=48:00:00


# --------------------------------------------------------------
### PART 2: Executes bash commands to run your job
# --------------------------------------------------------------
### Load required modules/libraries if needed
module load python/3.6/3.6.5
source /home/u8/rspinti/virtual_envs/bifurcation_env/bin/activate
### change to your script’s directory
cd /xdisk/lecondon/rspinti/river_bifurcation/testing_workflow
### Run your work
python run_workflow.py
sleep 10
