#!/usr/bin/env bash
# LAUNCH from /group/transreg/nidil/Brute_force_analysis
# GO
module load python/x86_64/3.5.1
module load R/x86_64/3.4.0
module load gcc

cd /group/transreg/nidil/Brute_force_analysis

#!/bin/sh

GOTERM=$( cat /group/transreg/nidil/Brute_force_analysis/ONLY_go_terms_min_25_max_500_nogs_from_nogs_in_mmetsp_mincomp0.6_minocc2.tsv | awk "NR==$SGE_TASK_ID")

echo $GOTERM

# Loop over NOGs and calculate NOG vector matrix
python3 /home/nidil/Documents/Project_TRAPID/Scripts/Compare/python/python_scripts/NOG_matrix_wrapper.py Data/REASSEMBLIES_V2_main.csv /home/nidil/Documents/Project_TRAPID/Scripts/ -GO $GOTERM -mc 0.6 -mo 2

# Cluster Nog matrix
python3 /home/nidil/Documents/Project_TRAPID/Scripts/Compare/python/python_scripts/FLAME_clustering.py NOG_vectors_mincomp0.6_minocc2_$GOTERM/NOG_vectors_mincomp0.6_minocc2_$GOTERM.txt ~/Documents/Project_TRAPID/Scripts/flame-clustering/sample -axis 01 -d 4 -knn 15 -write -metadata_type phylum_MMETSP -data_main NOG_vectors_mincomp0.6_minocc2_$GOTERM/filtered_mincomp0.6_data_main.csv -o NOG_vectors_mincomp0.6_minocc2_$GOTERM

# Enrichment analysis
/group/transreg/Tools/dreec_enrichment/enricher NOG_vectors_mincomp0.6_minocc2_$GOTERM/FLAME_output_d4_knn15_axis01/phylum_MMETSP_metadata.txt NOG_vectors_mincomp0.6_minocc2_$GOTERM/FLAME_output_d4_knn15_axis01/FLAME_output_d4_knn15_axis0.txt -d > NOG_vectors_mincomp0.6_minocc2_$GOTERM/FLAME_output_d4_knn15_axis01/enricher_output_default_depleted.txt