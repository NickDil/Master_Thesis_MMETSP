#!/usr/bin/env bash

# Load modules
module load python/x86_64/2.7.2

# set clade if not in -v argument
# export MY_CLADE=2759
# export MY_SPEC=0.9

# Tell the SGE that this is an array job, with "tasks" to be numbered example: 806-985 (= exp_ID)
# -t 9752-9938 #put dollar sign in after hash to activate
# Tell the SGE to run at most 10 tasks at the same time:
# -tc 10
# on two cores
# -pe serial 2
# When a single command in the array job is sent to a compute node,
# its task number is stored in the variable SGE_TASK_ID,
# so we can use the value of that variable to get the results we want:




#Create directory
mkdir $SGE_TASK_ID/completeness
chmod 777 $SGE_TASK_ID/completeness

#execute cGF analysis wrapper
echo "[START] core gf completeness analysis of experiment $SGE_TASK_ID: `date`"
python /home/nidil/Documents/core-gf-analysis/run_core_gf_analysis_trapid_eggnog.py $MY_CLADE $SGE_TASK_ID -sp $MY_SPEC -o /group/transreg/nidil/bigupload/experiment_data/$SGE_TASK_ID/completeness/ > "$SGE_TASK_ID/completeness/core_gfs_completeness_$MY_CLADE.$SGE_TASK_ID.$MY_SPEC.out" 2> "$SGE_TASK_ID/completeness/core_gfs_completeness_$MY_CLADE.$SGE_TASK_ID.$MY_SPEC.err"
echo "[STOP] core gf completeness analysis of experiment $SGE_TASK_ID: `date`"
