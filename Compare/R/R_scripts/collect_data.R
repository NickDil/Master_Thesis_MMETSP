
# R script exploring cross sample comparison for MMETSP samples in TRAPID2.0
# Nick Dillen

# Dependencies
suppressMessages(library('RMySQL'))
library('rjson')
library('glue')
suppressMessages(library('plyr'))
suppressMessages(library('dplyr'))
library("ggplot2")
# library('randomcoloR')
# library('rCharts')
# library('rbokeh')
#!!!!!!# library('taxize')

### get arguments ###
arguments = commandArgs(trailingOnly = TRUE)

# Convert "None" strings to NULL values
for (i in 1:length(arguments)){
  if (arguments[i] == "None"){
    arguments[i] = list(NULL)
  }
}
file.title = arguments[1]
dir.data = arguments[2]
dir.base = arguments[3]
dir.out = arguments[4]
taxres = arguments[5]
usr_id = arguments[6]
min.completeness = arguments[7]

# print(arguments)
#### source for functions ####
source(paste0(dir.base,"Compare/R/R_scripts/compare_functions.R"))


#### MAIN SCRIPT ####

#desc_query = NULL, tax_id = NULL, refDB_query = NULL, phylum = NULL, genus = NULL, species = NULL, minimal_nr_transcripts = 1, color = randomColor(1)

# transcript configuration data to connect to DB
config <- fromJSON(file=paste0(dir.base, "config_connect_trapid.json"))

# Selection of experiments
arguments.select = arguments
arguments.select[1:7] = NULL
parameters = c(list(config),usr_id, arguments.select)

exps = do.call(select_exp, parameters)
#exps = select_exp(config, usr_id, desc_query = "zenodo", refDB_query = "pico", phylum = "chlorophyta")

# Rank on transcript taxonomy
# exps = rank_on_taxonomy(exps)

# Count total transcripts for both selections
exps = transcripts_count(config, exps)

# Add core GF scores, default arguments
exps = get_coreGF_score(exps)

# Filter on core gf completeness score
exps = exps[exps$completeness_score >= min.completeness,]
print(paste('[FILTER]', nrow(exps), "experiments remaining after filtering on completeness score!"))

### TAXONOMY: get taxonomic composition and plot for all samples ####
data.location = dir.data
#"/home/nidil/Drives/biocomp/groups/group_cig/nidil/experiment_data/"
# print(exps$experiment_id)
# print(data.location)
# print(taxres)
# Taxonomic analysis (Kaiju output)
txcmp = tax_composition_kaijuReport(data.location, taxres, exps)

#plot_tax_composition(txcmp, cutoff = 0.05, title = "Taxonomic composition (genus level) based on Kaiju of MMETSP samples ZENODO" )

# count number of trancripts with annotation on genus level
exps = annotated_transcripts_count(exps, txcmp)

setwd(paste(dir.out))
folder.out = paste0(file.title)
dir.create(folder.out)
setwd(folder.out)
dir.create("Data")
setwd("Data")
write.csv(exps, file = paste0(file.title , "_main.csv"))
write.csv(txcmp, file = paste0(file.title ,"_txcmp.csv"))

print(paste0("[INFO] Files written to directory : ",dir.out, folder.out, '/Data/'))

# make sure all connections closed
# lapply(dbListConnections( dbDriver( drv = "MySQL")), dbDisconnect)
