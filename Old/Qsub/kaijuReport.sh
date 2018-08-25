#!/usr/bin/env bash


#$ -N array_job
# -t start-stop
#$ -tc 10
#$ -S /bin/bash


module load kaiju

#species
kaijuReport -t /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/nodes.dmp -n /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/names.dmp -i /group/transreg/nidil/experiment_data/$SGE_TASK_ID/kaiju/kaiju_merged.out -r species -o /group/transreg/nidil/experiment_data/$SGE_TASK_ID/kaiju/kaiju.out.species.$SGE_TASK_ID.summary
#genus
kaijuReport -t /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/nodes.dmp -n /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/names.dmp -i /group/transreg/nidil/experiment_data/$SGE_TASK_ID/kaiju/kaiju_merged.out -r genus -o /group/transreg/nidil/experiment_data/$SGE_TASK_ID/kaiju/kaiju.out.genus.$SGE_TASK_ID.summary
#phylum
kaijuReport -t /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/nodes.dmp -n /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/names.dmp -i /group/transreg/nidil/experiment_data/$SGE_TASK_ID/kaiju/kaiju_merged.out -r phylum -o /group/transreg/nidil/experiment_data/$SGE_TASK_ID/kaiju/kaiju.out.phylum.$SGE_TASK_ID.summary