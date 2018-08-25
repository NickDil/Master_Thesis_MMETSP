#!/usr/bin/env bash

module load python/x86_64/3.5.1
module load R/x86_64/3.4.0
module load gcc
module load kaiju/x86_64/1.6.1

#species
kaijuReport -t /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/nodes.dmp -n /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/names.dmp -i $SGE_TASK_ID/kaiju/kaiju_merged.out -r species -o $SGE_TASK_ID/kaiju/kaiju.out.species.$SGE_TASK_ID.summary
#genus
kaijuReport -t /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/nodes.dmp -n /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/names.dmp -i $SGE_TASK_ID/kaiju/kaiju_merged.out -r genus -o $SGE_TASK_ID/kaiju/kaiju.out.genus.$SGE_TASK_ID.summary
#phylum
kaijuReport -t /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/nodes.dmp -n /blastdb/webdb/moderated/trapid_02/kaiju_files/ncbi_tax_2017_09/names.dmp -i $SGE_TASK_ID/kaiju/kaiju_merged.out -r phylum -o $SGE_TASK_ID/kaiju/kaiju.out.phylum.$SGE_TASK_ID.summary