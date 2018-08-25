#!/usr/bin/env bash
# LAUNCH from /group/transreg/nidil/Brute_force_analysis
# GO
module load python/x86_64/3.6.5
module load R/x86_64/3.4.0
module load gcc

cd /home/nidil/Documents/Project_TRAPID/brute_force_pipeline2

#!/bin/sh

GOTERM=$( cut -f 1 /home/nidil/Documents/Project_TRAPID/GO_terms_M260 | awk "NR==$SGE_TASK_ID")

echo $GOTERM

CONFIG='{
  "data_location": "/group/transreg/frbuc/trapid_mmetsp_reassembly_apr_2018/tmp/",
  "project_script_location": "/home/nidil/Documents/Project_TRAPID/Scripts/",
  "user_id": "65",
  "name": "BF2_'"$GOTERM"'",
  "outdir": "/home/nidil/Documents/Project_TRAPID/brute_force_pipeline2/",
  "metadata_type": "phylum",
  "metadata_cutoff": "5",
  "min_completeness": 0.6,

  "min_occurence": "20",
  "GO": "'$(echo $GOTERM | tr _ :)'",
  "counts": "TRUE",
  "normalize": "TRUE",

  "flame_path":"/home/nidil/Documents/Project_TRAPID/Scripts/flame-clustering/sample",
  "axis": "0",
  "d" : "4",
  "knn" : "15",
  "write": "True",
  "keep": "False",

  "enricher_location": "/group/transreg/Tools/dreec_enrichment/enricher",
  "arguments_string": "-d",

  "greyscale": "FALSE"

}
'
echo $CONFIG > config_$GOTERM.json

python3 /home/nidil/Documents/Project_TRAPID/Scripts/Compare/python/python_scripts/genomic_signature_detection_pipeline.py config_$GOTERM.json

#rm config_$GOTERM.json

