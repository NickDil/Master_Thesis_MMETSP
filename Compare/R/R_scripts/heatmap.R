# Dependencies
library('RMySQL')
library('rjson')
library('glue')
library('plyr')
library('dplyr')
library("ggplot2")
library('randomcoloR')
library('rCharts')
library('taxize')

#### source for functions ####

source("compare_functions.R")

###
config <- fromJSON(file="../../../config_connect_trapid.json")
usr_id = get_user_ID(config, "nidil")

# exps_chlorophyta = select_exp(config, usr_id, refDB_query = "eggnog", phylum = "chlorophyta")
# exps_chlorophyta = rank_on_taxonomy(exps_chlorophyta)
# exps_chlorophyta = transcripts_count(config, exps_chlorophyta)
# 
# GF.data.original = GF_comparison_naive(config, exps_chlorophyta)
# print(nrow(GF.data.original))
# 
# colnames(GF.data.original) = exps_chlorophyta$title
# 
# GF.data.original.collapsed = GF_comparison_collapsed(config, exps_chlorophyta)


##alll
exps = select_exp(config, usr_id, refDB_query = "eggnog")
exps = get_coreGF_score(exps)


# Filter on GF_completeness
mask = exps$completeness_score >= 0.98

exps.plot = exps[mask,]
cat(paste0(nrow(exps.plot), " experiments remaining.\n"))

exps.plot = exps.plot[c(1:3),]

starttime = Sys.time()
GF.data.original.collapsed = GF_comparison_collapsed(config, exps.plot, COUNT = TRUE)
Sys.time() - starttime
# #Time difference of 8.27786 mins

# GO.term = 'GO:0015979' #photosynthesis
# GO.term = 'GO:0071941'#nitrogen cycle metabolic process
# GO.term = 'GO:0009607' #response to biotic stimulus
GO.term = "GO:0005215" #transporter
starttime = Sys.time() 
GF.trim_GO = GF_comparison_collapsed(config, exps.plot, GO.term = GO.term)
Sys.time() - starttime
#Time difference of=- 2mins

table(rowSums(GF.trim_GO[-1]))
#remove GFs that are not present in any sample or only in on sample
GF.data.plot = GF.trim_GO[rowSums(GF.trim_GO[-1]) > 10,]



#clustering
##cosine simil
X = t(GF.trim.photosynthesis[-1])
cos.sim <- function(ix) {
  A = X[ix[1],]
  B = X[ix[2],]
  return( 1 - sum(A*B)/sqrt(sum(A^2)*sum(B^2)) )
}

dist_cos.sim <- function(x){
  n <- nrow(X) 
  cmb <- expand.grid(i=1:n, j=1:n) 
  C <- as.dist(matrix(apply(cmb,1,cos.sim),n,n))
  attr(C, "Labels") = colnames(GF.trim.photosynthesis[-1])
  attr(C, "method") = "cos.sim"
  return(C)
  
}

heatmap(X, scale = 'none',distfun = dist_cos.sim, Colv =NA, RowSideColors = cc)

## 1-cor
dist_cor = function(x){
  return(as.dist(1-cor(x)))
}

heatmap(GF.data.plot[-1], scale = 'none',distfun = dist_cor, RowSideColors = cc, Colv = NA)

XXX = t(GF.data.original.collapsed[-1])
write(dim(X.m), file = 'FLAMEtest.csv')
write.table(X.m, sep = " ", file = 'FLAMEtest.csv', append = T, col.names = FALSE, row.names = FALSE)

f =read.csv("~/Drives/nidil/Documents/Project_TRAPID/Scripts/Compare/R/R_scripts/FLAMEtest.csv")


X.m = t(GF.trim_GO[-1])
### test ICA + FDR
# 1 ICA
#X.m = t(GF.data.original.collapsed[-1])
ICA.analysis = fastICA(X.m, 2)
S.m = ICA.analysis$S
#post-processing
pval.m = matrix(NA,nrow(S.m), ncol(S.m))
for (i in 1:nrow(S.m)){
  xfdr = fdrtool(S.m[i,], cutoff.method = 'fndr')
  pval.m[i,] = xfdr$pval

}



#### apcluster 
# is implicit for k but no overlap allowed
apclust.out = apcluster(corSimMat(r=1, signed=T), X.m, includeSim = T)
heatmap(apclust.out)

# port for FLAME
FLAME.location = "/home/nidil/flame-clustering/sample"
matrix.location = "/home/nidil/flame-clustering/FLAMEtest.csv"
distfunct = 2
knn = 50

command_FLAME = paste("python3 ~/Drives/nidil/Documents/Project_TRAPID/Scripts/Compare/python/python_scripts/FLAME_clustering.py", matrix.location,"-d", distfunct,"-knn", knn)
clusters = system(command_FLAME, intern = TRUE)

clusters


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


heatmap(data.matrix(t(GF.data.plot[-1]))
        , scale='none'
        , RowSideColors = cc
        , labCol = NA
        , main = paste("All samples /", GO.term)
        , distfun = dist_cos.sim
)

legend(0.85, 0.5, legend = c(coltax), fill = c(un), cex = 0.7, bty = 'n', yjust = 0.5)




clust1 = c(260,  153,  448,  450,  449,  152,   89,   90,   91,   95,
94,   93,   92,   58,   59,  148,  147,  441,   61,  360,
200,  201,   83,  442,  203,  149,  265,  135,  146,  143,
139,   68,  150,   80,   52,   78,   74,   76,   98,   99,
100,  355,   46,   47,  216,  217,  215,   48,  345,  111,
490)






# features selection, unique gene families throw away? not relevant if we want to cluster samples Based on *presence*, but as we also are interested in 
GF.data = GF.data.original[rowSums(GF.data.original[,-1]) > 1,]
print(nrow(GF.data))

GF.matrix = data.matrix(GF.data[,-1])
# exps_chlorophyta$experiment_id
# colnames(GF.matrix) =
# exps_chlorophyta$genus_MMETSP[exps_chlorophyta$transcripts_count_total <1000]

subdat = GF.matrix[1:100,]

library(heatmaply)
heatmap(subdat, scale = "none" )
# check other dist mb correlation
# switch testset to eggmog
heatmaply(subdat, Rowv = NA, labCol = exps_chlorophyta$genus_MMETSP, file = "/home/nidil/Documents/Project_TRAPID/Scripts/Compare/Results/testmap.html")
