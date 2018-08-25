# Dependencies
library('RMySQL')
library('rjson')
library('glue')
library('plyr')
library('dplyr')
library("ggplot2")
library('RColorBrewer')

### cmdline args

arguments = commandArgs(trailingOnly = TRUE)

arguments_use = c('heatmap_MMETSP_all_default', 'euclidian', 1, 1, 0.8 , '/home/nidil/Documents/Project_TRAPID/Scripts/', TRUE, "None" )
names(arguments_use) = c("name","distfun", "min_occurence", "min_trs", "min_completeness", "dir.base", "COUNT", "GO.term")

if(!is.na(arguments[1])){arguments_use["name"] = arguments[1]}
if(!is.na(arguments[2])){arguments_use["distfun"] = arguments[2]}
if(!is.na(arguments[3])){arguments_use["min_occurence"] = arguments[3]}
if(!is.na(arguments[4])){arguments_use["min_trs"] = arguments[4]}
if(!is.na(arguments[5])){arguments_use["min_completeness"] = arguments[5]}
if(!is.na(arguments[6])){arguments_use["dir.base"] = arguments[6]}
if(!is.na(arguments[7])){arguments_use["COUNT"] = arguments[7]}
if(!is.na(arguments[8])){arguments_use["GO.term"] = arguments[8]}


print(arguments_use)

#### source for functions ####

source(paste0(arguments_use["dir.base"],"Compare/R/R_scripts/compare_functions.R"))

###
config <- fromJSON(file=paste0(arguments_use["dir.base"],"config_connect_trapid.json"))
usr_id = 65

##all experiments
# add min_trs to also flter on #trs ( not nescessary when using core_GF filter)
exps.all = select_exp(config, usr_id, refDB_query = "eggnog")
exps.all = get_coreGF_score(exps.all)
cat(paste0("[EXPERIMENT SELECTION} Selected ", nrow(exps.all), " experiments.\n"))

# # Filter on GF_completeness
# mask = exps.all$completeness_score >= arguments_use['min_completeness']
# cat(paste0('[FILTER] Filtering out ', 
#              nrow(exps.all) - sum(mask), 
#              " experiments with core_gf_completeness_score lower than ",
#              arguments_use["min_completeness"], ".\n"))
# 
# exps.all = exps.all[mask,]
# cat(paste0(nrow(exps.all), " experiments remaining.\n"))
# 
# exps.plot = exps.all
# GF.data.original.collapsed = GF_comparison_collapsed(config, exps.plot, COUNT = TRUE)
# 
# df.normalized = as.matrix(GF.data.plot) %*% diag(1/exps.plot$transcripts_count_total) * mean(exps.plot$transcripts_count_total)
# colnames(df.normalized) = colnames(GF.data.plot)
# GF.data.plot = df.normalized
# 
# cat(paste0("[GENE FAMILY SELECTION} Created GF presence vectors of length ", nrow(GF.data.original.collapsed), ".\n"))
# 
# mask.GF = rowSums(GF.data.original.collapsed[,-1]) > arguments_use['min_occurence']
# cat(paste0('[FILTER] Filtering out ', 
#            nrow(GF.data.original.collapsed) - sum(mask.GF), 
#            " gene families (NOGs) that are present in only ",
#            arguments_use["min_occurence"], " sample(s).\n"))
# GF.data.original.collapsed = GF.data.original.collapsed[mask,]
# cat(paste0("[HEATMAP] Creating a heatmap based on data matrix with ", ncol(GF.data.original.collapsed), " samples and ", nrow(GF.data.original.collapsed), " gene families (NOGs)!\n"))

# Filter on GF_completeness
exps.plot = exps.all
rm(exps.all)
mask = exps.plot$completeness_score >= as.numeric(arguments_use["min_completeness"])

exps.plot = exps.plot[mask,]
cat(paste0(nrow(exps.plot), " experiments remaining.\n"))

exps.plot = transcripts_count(config, exps.plot)

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
GF.data.plot = GF.trim_GO[rowSums(GF.trim_GO != 0) > as.numeric(arguments_use["min_occurence"]),]
cat(paste(nrow(GF.trim_GO), "NOGs before occurence filter,", nrow(GF.data.plot), "NOGs remaining after"))

if (as.logical(arguments_use["COUNT"])){
  # Normalize by dividing each column with the total amount of transcripts in that experiment, multiply by mean of all experiments included to get countlike value
  df.normalized = as.matrix(GF.data.plot) %*% diag(1/exps.plot$transcripts_count_total) * mean(exps.plot$transcripts_count_total)
  colnames(df.normalized) = colnames(GF.data.plot)
  GF.data.plot = df.normalized
}


png(file=paste0(getwd(),"/", arguments_use["name"], ".png"), width = 5000, height = 2500)

# GF.plot determination
# GF.plot = GF.data.original.collapsed[,-1]
GF.plot = GF.data.plot

# heatmap of orignal data, only clustered on samples
taxcol = "phylum_MMETSP"
coltax = unlist(unique(exps.plot[taxcol]))

n <- length(coltax)
colmap = c("#e57373", "#00ffaa", "darkcyan", "brown4", "#f2c6b6", "green", "#ff6600", "#bff2ff", "#bf6600", "black", "#e5b073",
           "#40bfff", "#ffbf40", "#3069bf", "#eeff00", "#a173e6", "#aab32d", "#6d00cc", "#fbffbf", "#b499cc", "#73e6cf", "#cc00be",
           "#ffffff", "#ff80d5", "#f2f2f2", "#e5397e", "grey", "#d9a3b1", "#59b371", "#cc001b")
un = colmap[1:n]
cc = c()
for (taxc in exps.plot[taxcol]){
  i = match(taxc, coltax)
  cc = c(cc, un[i])
}

starttime = Sys.time()
heatmap(data.matrix(t(GF.plot))
        , RowSideColors = cc
        , labCol = NA
        , main = paste("Heatmap", arguments_use["GO.term"], arguments_use["min_completeness"], arguments_use["min_occurence"], arguments_use["distfun"] )
        , distfun = function(x) dist(x,method=arguments_use["distfun"])
)
Sys.time() - starttime

legend(0.85, 0.5, legend = c(coltax), fill = c(un), cex = 0.8, bty = 'n', yjust = 0.5)

dev.off()
