#!/usr/bin/env bash

module load python/x86_64/3.5.1
module load perl
module load java
module load gcc
module load kaiju
module load diamond

# Tell the SGE that this is an array job, with "tasks" to be numbered example: 806-985 (= exp_ID)
# -t 9929-9931 #put dollar sign in after hash to activate
# Tell the SGE to run at most 10 tasks at the same time:
# -tc 10
# on two cores
# -pe serial 2
# When a single command in the array job is sent to a compute node,
# its task number is stored in the variable SGE_TASK_ID,
# so we can use the value of that variable to get the results we want:

# do the initial procesing of experiment with ID = SGE_TASK_ID
python3 /home/nidil/Documents/Project_TRAPID/Scripts/Initial_processing/initial_processing.py -C /home/nidil/Documents/Project_TRAPID/Scripts/config_initial_processing.json -exp_ID $SGE_TASK_ID
