# Helper scripts for command line based upload of multiple TRAPID2.0 experiments

Upload and initial processing of multiple transcriptomes using the command line.


## Considerations/preparations/ things I should make better:
- Made only for uploading MMETSP samples (for now)
- Three  .json configuration files should better exist, eg. for password safety (see templates):
    - config_connect_trapid.json			(info about user DB acces)
    - config_experiment.json		(info about experiments to be created)
    - config_initial_processing.json	(info for the initial processing)
- A temporary directory to store results in has to be created, if the server has no access to the final destination directory (eg. no acces to /www/bioapp/trapid_frbuc/experiment_data)
    - you will have to copy paste the content of this temporary directory to the final destination once done to get a fully working TRAPID experiment page.
(cp -R  {..} + chmod 777 {..})

### Requirements
- Python 2.7 (only for the `Data/mmetsp_metadata/reformat_mmetsp_metadata.py` script)
- Python 3
- Python 3 modules:
    - pymysql
    - argparse
    - json
    - urllib


## HOWTO

### Uploading experiments from URLs to TRAPID_DB:

#### 1 -  Create URL-list for the samples you want to upload.
- format of URL-list:

```shell
<SAMPLE NAME/TITLE>\t<URL>[\t<MD5SUM>]\n
<SAMPLE NAME/TITLE>\t<URL>[\t<MD5SUM>]\n
<SAMPLE NAME/TITLE>\t<URL>[\t<MD5SUM>]\n
…
```

(For examples of script scraping URLs from FTP site iMicrobe and create URL list from that cf. Old/iMicrobe_FTP_sample_url_scrape.py)


#### 2 – Use wrapper on the URL-list to get shell script
- Example:

```shell
python3 wrap_create_experiment.py <URL-list> <script_directory_NICK>
```
- output: `url_list_upload.sh`


#### 3 – qsub shell script

```shell
qsub url_list_upload.sh
```


#### (4 – optional but recommended QC step: Verification that connection to MySQL server was not lost)
- Encountered problems when uploading : ```Lost connection to MySQL server at 'reading authorization packet', system error: 0``` for some samples.
- check with `egrep -lir --include \upload.err "Lost connection"`
- For now: manually reupload selected experiments

--------------------------------------------------------------------------------


### Initial processing of uploaded transcriptome samples:


#### 1 – Know experiment IDs you want to get processed:
- eg: 888 – 999 = <minexp_ID-maxexp_ID>


#### 2 – Submit array job to cluster with initial_processing_array.sh
- Example:

```shell
qsub -l mem_free=10G,h_vmem=5G -q stt@snowstorm -t 888-999 -tc 10 -pe serial 2 initial_processing_array.sh
```
--------------------------------------------------------------------------------

### Copy everything to web accessible location:

This is needed in order to be able to use the TRAPID web application with your processed samples. Done in two steps:

```shell
# 1. Copy all your experiments to TRAPID's files location
cp -R {888..999} /path/to/trapid_experiment_data
# 2. Give proper permissons (needed by the web app)
chmod 777 -R {888..999}
```

--------------------------------------------------------------------------------
### Core Gene Family analysis

Process a range of experiment IDs with code by Francois Bucchini, see https://gitlab.psb.ugent.be/frbuc/core-gf-analysis for the source code

#### 1 - Make sure you are in a `experiments_data` folder, e.g. direct access to experiment_id folders.
```shell
cd /path/to/experiment_data
```
#### 2 - Do the core GF analysis
[TODO] PLAZA versus EggNOG still hardcoded !!! (eg for cluster use _EGGNOG.sh or _PLAZA.sh, local only PLAZA)

[TODO] path to /core-gf-analysis also hardcoded

##### (first export DB_PWD)
`export DB_PWD=[database password]`
- ##### A - Locally
Run and follow instructions:
```shell
/path/to/Scripts/Completeness/core_gf_analysis_local_PLAZA.sh
```

- ##### B - Cluster

Example:
```shell
qsub -v MY_CLADE=[clade_id],MY_SPEC=[conservation_treshold],DB_PWD -t 888-999 -tc 10 -l h_vmem=12G -o core_GF_anlysis.out -e core_GF_anlysis.err /path/to/Scripts/Completeness/core_gf_analysis_array_[EGGNOG/PLAZA].sh
```
--------------------------------------------------------------------------------

### Deleting multiple experiments
#### 1 – Know your experiment IDs to be removed
- eg. 888 to 999

#### 2 – Run delete experiments script
- Example:

```shell
python3 delete_experiments.py <888> <999> <temp_dir_location> <config_connect_trapid.json>
```

- Or modify shell script `del.sh` and submit to cluster.


## MMETSP metadata

In `Data/mmetsp_metadata`: raw MMETSP metadata & code used to create a MySQL database containing the MMETSP metadata.   


### How to generate

#### 1 - Reformat raw data

```shell
# Reformat MMETSP metadata
python reformat_mmetsp_metadata.py sample-attr.tab > mmetsp_sample_attr.tsv
# Convert line returns in SRA run info file
tr '\r' '\n' < SraRunInfo.csv > SraRunInfo.unix.csv
```

#### 2 - Create database

Simply use the code in `create_metadata_db.sql`

#### 3 - Import data

**Example:**
```shell
mysql -h psbsql01.psb.ugent.be -u trapid_website -p$DB_PWD db_trapid_mmetsp_metadata  --execute="LOAD DATA LOCAL INFILE 'SraRunInfo.unix.csv' INTO TABLE sra_run_info FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\n' IGNORE 1 LINES; SHOW WARNINGS"
mysql -h psbsql01.psb.ugent.be -u trapid_website -p$DB_PWD db_trapid_mmetsp_metadata  --execute="LOAD DATA LOCAL INFILE 'mmetsp_sample_attr.tsv' INTO TABLE mmetsp_sample_attr FIELDS TERMINATED BY '\\t' LINES TERMINATED BY '\\n' IGNORE 1 LINES; SHOW WARNINGS"           
```


## Troubleshooting

Quick dump of issues we've encountered and how we solved them.

**What should be put in the `blast_location` and `blast_database` of the initial processing configuration file?**

These two variables are the reflect of how parameters are handled by the initial processing Java code. They correspond respectively the directory where DIAMOND databases (`.dmnd` files) are located, for a given TRAPID reference database, and the actual DIAMOND database you want to use in that directory (the `.dmnd` file itself).


**Impossible to create directories and file needed for processing...**

Make sure that you are trying to read/write from locations that are accessible from the machine you use to launch the scripts.
