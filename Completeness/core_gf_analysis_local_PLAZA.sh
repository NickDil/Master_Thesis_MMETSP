#!/usr/bin/env bash

# use cluster version (arrayjob)
#Script to do the core GF completeness analysis from command line

echo "Make sure you are in a '/path/to/experiment_data directory!'"
echo "What is you clade_taxID (eg. Eukaryota = 2759)?"
read MY_CLADE
echo "What is your first experiment_id?"
read MY_START

echo "What is your last experiment_id?"
read MY_STOP


# Loading necessary modules
module load python/x86_64/2.7.2

for EXP_ID in $(seq $MY_START $MY_STOP);

# Launching python wrapper for core GF analysis from TRAPID, with correct parameters.
# Print starting date/time
do echo "Start core gf completeness analysis of experiment $EXP_ID at : `date`";
mkdir $EXP_ID/completeness;
chmod 777 $EXP_ID/completeness;
python /home/nidil/Documents/trapid_develop/app/scripts/python/run_core_gf_analysis_trapid.py $MY_CLADE $EXP_ID --label None --species_perc 0.9 --top_hits 5 --output_dir /group/transreg/nidil/experiment_data/$EXP_ID/completeness/ > $EXP_ID/completeness/core_gfs_completeness_$MY_CLADE_$EXP_ID.out 2> $EXP_ID/completeness/core_gfs_completeness_$MY_CLADE_$EXP_ID.err;
done

# python /home/nidil/Documents/trapid_develop/app/scripts/python/run_core_gfs.py -sp 0.9 -o "core_gfs_$MY_CLADE.tsv" "db_trapid_02" $MY_CLADE




