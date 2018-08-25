#!/usr/bin/env bash
#specify axis, knn and d with -v MY_AXIS=0,MY_KNN=15,MY_D=4
module load python/x86_64/3.5.1
python3 /home/nidil/Documents/Project_TRAPID/Scripts/Compare/python/python_scripts/FLAME_clustering.py /home/nidil/Documents/Project_TRAPID/Scripts/Compare/Results/REASSEMBLIES_V2_results/NOG_vectors_mincomp0.6_minocc2_None_counts/NOG_vectors_mincomp0.6_minocc2_None_counts.txt /home/nidil/Documents/Project_TRAPID/Scripts/flame-clustering/sample -axis $MY_AXIS -d $MY_D -knn $MY_KNN -write