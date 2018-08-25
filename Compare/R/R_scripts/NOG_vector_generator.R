# Dependencies
suppressMessages(library('RMySQL'))
suppressMessages(library('rjson'))
suppressMessages(library('glue'))
suppressMessages(library('plyr'))
suppressMessages(library('dplyr'))
# library("ggplot2")
# library('randomcoloR')
# library('rCharts')
# library('taxize')

### get arguments ###
# arguments = commandArgs(trailingOnly = TRUE)
# 
# # Convert "None" strings to NULL values
# for (i in 1:length(arguments)){
#   if (arguments[i] == "None"){
#     arguments[i] = list(NULL)
#   }
# }
# infile = arguments[1]
# min_completeness = arguments[2]
# dir.data = arguments[3]
# dir.out = arguments[4]
# taxres = arguments[5]

arguments = commandArgs(trailingOnly = TRUE)


print(arguments)
 
# arguments_use = c('infile', 1, 0.8, FALSE, '/home/nidil/Documents/Project_TRAPID/Scripts/', FALSE, 'None', getwd())
# names(arguments_use) = c('infile', 'min_occurence', 'min_completeness', 'data.normalize', 'dir.base', 'COUNT', 'GO.term', 'dir.out')


arguments_use = c('infile', '/home/nidil/Documents/Project_TRAPID/Scripts/', "None", 0.8, 1, getwd(), FALSE, FALSE)
names(arguments_use) = c("infile", "dir.base", "GO.term" ,"min_completeness", "min_occurence", "dir.out", "COUNT", "data.normalize")

# Convert "None" strings to NULL values
infile = arguments[1]
if(!is.na(arguments[2])){arguments_use["dir.base"] = arguments[2]}
if(!is.na(arguments[3])){arguments_use["GO.term"] = arguments[3]}
if(!is.na(arguments[4])){arguments_use["min_completeness"] = arguments[4]}
if(!is.na(arguments[5])){arguments_use["min_occurence"] = arguments[5]}
if(!is.na(arguments[6])){arguments_use["dir.out"] = arguments[6]}
arguments_use["COUNT"] = arguments[7]
if(!is.na(arguments[8])){arguments_use["data.normalize"] = arguments[8]}else{
  arguments_use["data.normalize"] = arguments_use["COUNT"]}
print(infile)
print(arguments_use)
#### source for functions ####
source(paste0(arguments_use["dir.base"],"Compare/R/R_scripts/compare_functions.R"))

# configuration data to connect to DB
config <- fromJSON(file=paste0(arguments_use["dir.base"], "config_connect_trapid.json"))

exps = read.csv(infile)
exps.plot = exps

# GENERATE THE FETURE VECTORS
# GO.term = 'GO:0015979' #photosynthesis
# GO.term = 'GO:0071941'#nitrogen cycle metabolic process
# GO.term = 'GO:0009607' #response to biotic stimulus
# GO.term = "GO:0005215" #transporter
starttime = Sys.time() 
if (arguments_use["GO.term"] == 'None'){
  GF.trim_GO = GF_comparison_collapsed(config, exps.plot, COUNT = as.logical(arguments_use["COUNT"]))
}else{
  GF.trim_GO = GF_comparison_collapsed(config, exps.plot, GO.term = arguments_use["GO.term"], COUNT = as.logical(arguments_use["COUNT"]))
  }
Sys.time() - starttime
#Time difference of=- 2mins

# table(rowSums(GF.trim_GO[-1]))

#remove GFs that are not present in only in `min_occurence` number of samples
GF.data.plot = GF.trim_GO[rowSums(GF.trim_GO != 0) >= as.numeric(arguments_use["min_occurence"]),]
cat(paste(nrow(GF.trim_GO), "NOGs before occurence filter,", nrow(GF.data.plot), "NOGs remaining after"))

if (arguments_use["data.normalize"]){
  print("Normalizing")
  # Normalize by dividing each column with the total amount of transcripts in that experiment, multiply by mean of all experiments included to get countlike value
  df.normalized = as.matrix(GF.data.plot) %*% diag(1/exps.plot$transcripts_count_total) * mean(exps.plot$transcripts_count_total)
  colnames(df.normalized) = colnames(GF.data.plot)
  GF.data.plot = df.normalized
}

#Write to outdir, needs to to be rows = exps, cols = GFs
X = t(GF.data.plot)
setwd(paste(arguments_use["dir.out"]))
dir.out1 = paste0("NOG_vectors_mincomp",arguments_use["min_completeness"],"_minocc", arguments_use["min_occurence"],"_", paste(unlist(strsplit(arguments_use["GO.term"], ":")), collapse = "_"))
if (as.logical(arguments_use["COUNT"])){dir.out1 = paste0(dir.out1, "_counts")}
dir.create(dir.out1, showWarnings = FALSE)
setwd(dir.out1)
file.out = paste0(dir.out1, ".txt")
print(file.out)

# #oldstyle
# write(dim(X), file = file.out)
# write.table(X, sep = " ", file = file.out, append = T, col.names = FALSE, row.names = FALSE)

write.table(X, sep = " ", file = file.out)

## How to add meta info?
# write.table(rownames(X), file = "experiments.txt", col.names=FALSE, row.names = FALSE)
# write.table(colnames(X), file = "NOGs.txt", col.names=FALSE, row.names = FALSE)
# 
# write.table(X, sep = " ", file = paste0(dir.out1, "INFO.txt"))



write.csv(exps.plot, file = paste0("filtered_mincomp", arguments_use["min_completeness"],"_data_main.csv"))

cat("\n", paste0(getwd(), "/", file.out))
cat("\n", paste0(dim(X)[1],"x", dim(X)[2]))
