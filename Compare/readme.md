# # Helper scripts for comparison of experiments

In this directory code is stored for comparison of multiple samples based on simple metrics, but also on clustering of NOG vectors.

### Prerequisites

Make sure the core GF completeness score is calculated for all experiments and is already done and stored in the trapid DB.

You can do this by running the [`Completeness/core_gf_analysis_array_EGGNOG.sh`](https://gitlab.psb.ugent.be/nidil/TRAPID-scripts-nidil/edit/master/Completeness/core_gf_analysis_array_EGGNOG.sh) or likewise script.

## Example pipeline

### 1) Select experiments and QC ([collect_data.R](https://gitlab.psb.ugent.be/nidil/TRAPID-scripts-nidil/blob/master/Compare/R/R_scripts/collect_data.R) wrapper)

Select experiments and plot based on core GF completeness score.

```shell
python3 experiments_QC.py /path/to/experiment_data/ /path/to/Scripts/ [-n name] [-i input_existing] [-o outdir] [-t tax_res] [<SQL DB query parameters...>]
```

Output:
- QC visualization (core GF completeness and # amount of transcripts per sample)
    - completeness_score.html  
- New analysis directory [name] containing a folder Data/ with:
    - data main.csv (selected experiment data)
    - data_txcmp.csv (kaiju taxcomp data)

### 2) Generate NOG feature matrix ([NOG_vector_generator](https://gitlab.psb.ugent.be/nidil/TRAPID-scripts-nidil/blob/master/Compare/R/R_scripts/NOG_vector_generator.R) wrapper)

Best to store the generated NOG_matrix in the analysis directory of the selected expeiments it is based on!

```shell
python3 NOG_matrix_wrapper.py data_main.csv /path/to/Scripts/ [-GO GO_term] [-mc min_completness] [-mo min_occurence] [-o outdir]
```
Creates NOG vectors (annotated with certain GO term) of your experiments and writes this matrix to a .txt file in a designated directory. PARAMETERS: GO-term, min_comp and min_occ

Output:
- New directory (name ~ parameters) containing:
    - NOG_vectors_mincomp[X]_minocc[Y]_[GO_term].txt (NOG feature matrix from given parameters)
    - filtered_mincomp[X]_data_main.csv (new selection of experiments based on completeness score filter applied)

### 3) [FLAME clustering](https://github.com/zjroth/flame-clustering) (wrapper around C++ code in link)

Best to store the output of the clustering in the directory of the used NOG_matrix.txt!

```shell
python3 FLAME_clustering.py NOG_matrix.txt /path/to/Scripts/flame-clustering/sample [-d distfunc] [-knn knn] [-write] [-o outdir] [-data_main data_main.csv]
```

Runs FLAME clustering algorithm (by wrapping around cpp code) on the NOG matrix,
transforms output to something recognized by the enricher and writes this to two files (gene_set and feature_set file) to designated folder.
PARAMETERS: d, knn, more to come.

The output is:
- New directory (name ~ parameters) containing:
    - phylum_clusters_FLAME_output_d[X]_knn[Y].txt, a file with taxonomic interpretation of the clusters
    - gene_set_FLAME_output_d[X]_knn[Y].txt, gene_set.txt to pass to Dries's enricher
    - feature_set_FLAME_output_d[X]_knn[Y].txt, ftr_set.txt to pass to Dries's enricher

### 4) Enrichment analysis of clusters

Perform enrichment analysis using dries’s enricher code

```shell
/group/.../Tools/../enricher [optional param] ftr_set.txt gene_set.txt
```

This prints the output directely in the terminal.


