
# R script exploring cross sample comparison for MMETSP samples in TRAPID2.0
# Nick Dillen

# Dependencies
library('RMySQL')
library('rjson')
library('glue')
library('plyr')
library('dplyr')
library("ggplot2")
library('randomcoloR')
library('rCharts')
library('rbokeh')
library('taxize')


#### source for functions ####

source("compare_functions.R")

#### MAIN SCRIPT ####

# transcript configuration data to connect to DB
config <- fromJSON(file="../../../config_connect_trapid.json")

# get selection of experiments
usr_id = 65
All_experiments = select_exp(config = config, user_id = 65)
#### ZENODO versus Imic : annotated with picoPlAZA ####
# Comparison of basic statistics

# Selection of experiments
exps_zen = select_exp(config, usr_id, "zenodo", refDB_query = "pico")
exps_zen = rank_on_taxonomy(exps_zen)

exps_mic = select_exp(config, usr_id, "imicrobe", refDB_query = "pico")
exps_mic = rank_on_taxonomy(exps_mic)


# example based on taxonomy annotaion MMETSP
exps_chlorophyta = select_exp(config, usr_id, refDB_query = "eggnog", phylum = "chlorophyta")
exps_chlorophyta = rank_on_taxonomy(exps_chlorophyta)


# Count total transcripts for both selections
exps_zen = transcripts_count(config, exps_zen)
exps_mic = transcripts_count(config, exps_mic)
exps_chlorophyta = transcripts_count(config, exps_chlorophyta)

All_experiments= transcripts_count(config, All_experiments)

### TAXONOMY: get taxonomic composition and plot for all samples ####
data.location = "/home/nidil/Drives/biocomp/groups/group_cig/nidil/bigupload/experiment_data/"

# SPECIES ####
# txcmp_species.mic = tax_composition_kaijuReport(data.location, 'species', exps_mic)
# plot_tax_composition(txcmp_species.mic, cutoff = 0.05, title = "Taxonomic composition (species level) based on Kaiju of MMETSP samples iMICROBE" )
# 
# txcmp_species.zen = tax_composition_kaijuReport(data.location, 'species', exps_zen)
# plot_tax_composition(txcmp_species.zen, cutoff = 0.05, title = "Taxonomic composition (species level) based on Kaiju of MMETSP samples ZENODO" )


# GENUS ####
txcmp_genus.mic = tax_composition_kaijuReport(data.location, 'genus', exps_mic)
plot_tax_composition(txcmp_genus.mic, cutoff = 0.05, title = "Taxonomic composition (genus level) based on Kaiju of MMETSP samples iMICROBE" )

txcmp_genus.zen = tax_composition_kaijuReport(data.location, 'genus', exps_zen)
plot_tax_composition(txcmp_genus.zen, cutoff = 0.05, title = "Taxonomic composition (genus level) based on Kaiju of MMETSP samples ZENODO" )

# PHYLUM ####
txcmp_phylum.mic = tax_composition_kaijuReport(data.location, 'phylum', exps_mic)
plot_tax_composition(txcmp_phylum.mic, cutoff = 0.05, title = "Taxonomic composition (phylum level) based on Kaiju of MMETSP samples iMICROBE" )

txcmp_phylum.zen = tax_composition_kaijuReport(data.location, 'phylum', exps_zen)
plot_tax_composition(txcmp_phylum.zen, cutoff = 0.05, title = "Taxonomic composition (phylum level) based on Kaiju of MMETSP samples ZENODO" )

#for chlorophyta example

txcmp.ex = tax_composition_kaijuReport(data.location, 'genus', exps_chlorophyta)
plot_tax_composition(exps_chlorophyta, txcmp.ex, cutoff = 0.05, title = "example tax bin genus level")

# count number of trancripts with annotation on genus level
exps_zen = annotated_transcripts_count(exps_zen, txcmp_genus.zen)
exps_mic = annotated_transcripts_count(exps_mic, txcmp_genus.mic)
exps_chlorophyta = annotated_transcripts_count(exps_chlorophyta, txcmp.ex)

file.title = "exp1"
write.csv(exps_chlorophyta, file = paste0("../R_files/", file.title ,"_main.csv"))
write.csv(txcmp.ex, file = paste0("../R_files/", file.title ,"_txcmp.csv"))



#### base statistic plots ####

# #trs in smple
# length ORF/trs histo
# core GF completeness scores
# with annotation










#### COMPARE BETWEEN SAMPLES, MAKE IN ONE FUNCTION? par.mfrow? ####

# for each MMETSP sample: plot mic and zen value -> scatterlpot
# amount of transcripts

hoverdf1 = as.data.frame(cbind(exps_zen$title, exps_zen$transcripts_count_total, exps_mic$transcripts_count_total))
colnames(hoverdf1) = c('sample name', '#trs DIB-lab', '#trs NCGR')

#bobble size
# blob_size = (exps_zen$transcripts_count_total+exps_mic$transcripts_count_total)/(0.1*mean(c(exps_mic$transcripts_count_total, exps_zen$transcripts_count_total)))

samples.1 = exps_zen$title[exps_zen$transcripts_count_total / exps_mic$transcripts_count_total < 0.1]
samples.2 = exps_zen$title[exps_zen$transcripts_count_total < 6000]

tit = samples.2

transcripts_count_total_plot <- figure(width = 800, title = "Total amount of transcripts for different assemblies (original (NCGR) vs. DIB-lab)") %>%
  ly_points(exps_zen$transcripts_count_total, exps_mic$transcripts_count_total,
            hover = hoverdf1) %>%
  ly_points(exps_zen$transcripts_count_total[exps_zen$title %in% tit], exps_mic$transcripts_count_total[exps_mic$title %in% tit], col = 'red') %>%
  ly_abline(0, 1, legend = "Line with slope = 1") %>%
  x_axis(label = '# transcripts DIB-lab') %>%
  y_axis(label = "# transcripts NCGR")

transcripts_count_total_plot


# For agreement on species level
# Count number of transcripts annotated with MMETSP  annotation

# plot_agreement(txcmp_species.mic, txcmp_species.zen, 'species')

plot_agreement(txcmp_genus.zen,txcmp_genus.mic, 'genus', percent = FALSE, highlight = samples.2)

plot_agreement(txcmp_phylum.zen, txcmp_phylum.mic, 'phylum', percent = T, highlight = samples.2)


## amount of transcripts in GF####

# hoverdf2 = as.data.frame(cbind(exps_zen$title, exps_zen$transcripts_in_GF_count, exps_mic$transcripts_in_GF_count))
# colnames(hoverdf2) = c('sample name', '#trs in GF DIB-lab', '#trs in GF NCGR')
# 
# # blob_size = ((exps_mic$transcripts_in_GF_count + exps_zen$transcripts_in_GF_count)/(0.1*mean(c(exps_mic$transcripts_in_GF_count, exps_zen$transcripts_in_GF_count))))
# 
# transcripts_in_GF_count_plot <- figure(width = 800, title = "# Assembled transcripts in a GF for different assemblies (original (NCGR) vs. DIB-lab)") %>%
#   ly_points(exps_zen$transcripts_in_GF_count, exps_mic$transcripts_in_GF_count,
#             hover = hoverdf2 , color = 'red' ) %>%
#   ly_abline(0, 1, legend = "Line with slope = 1") %>%
#   x_axis(label = '# transcripts in GF Zen') %>%
#   y_axis(label = "# transcripts in GF iMic")
# 
# transcripts_in_GF_count_plot

## same for GF_inclusion ratio ####

# blob_size = (exps_zen$GF_inclusion_ratio + exps_mic$GF_inclusion_ratio)*10 


# hoverdf3 = as.data.frame(cbind(exps_zen$title, round(exps_zen$GF_inclusion_ratio, 3), round(exps_mic$GF_inclusion_ratio,3)))
# colnames(hoverdf3) = c('sample name', 'inclusion rate DIB-lab', 'inclusion rate NCGR')
# 
# GF_inclusion_plot <- figure(width = 800, title = "GF inclusion rate (trs in GF / all trs) for different assemblies (original (NCGR) vs. DIB-lab)") %>%
#   ly_points(exps_zen$GF_inclusion_ratio, exps_mic$GF_inclusion_ratio,
#             hover = hoverdf3, color = 'green' ) %>%
#   ly_abline(0, 1, legend = "Line with slope = 1") %>%
#   x_axis(label = 'GF inclusion rate DIB-lab') %>%
#   y_axis(label = "GF inclusion rate NCGR")
# 
# GF_inclusion_plot









#### coreGF completness as QC metric ####

exps_zen = get_coreGF_score(exps_zen)
exps_mic = get_coreGF_score(exps_mic)
All_experiments= get_coreGF_score(All_experiments)


hoverdfcGF = as.data.frame(cbind(exps_zen$title, exps_zen$completeness_score, exps_mic$completeness_score))
colnames(hoverdfcGF) = c('sample name', 'score DIB-lab', 'score NCGR')

#bobble size
# blob_size = (exps_zen$completeness_score+exps_mic$completeness_score)/(0.1*mean(c(exps_mic$completeness_score, exps_zen$completeness_score)))

samples.1 = exps_zen$title[exps_zen$completeness_score / exps_mic$completeness_score < 0.1]
samples.2 = exps_zen$title[exps_zen$transcripts_count_total < 6000]
samples.3  = unique(c(exps_zen$title[exps_zen$completeness_score < 0.75], exps_mic$title[exps_mic$completeness_score  < 0.75]))

samples.3 == samples.2

titles.highlight = samples.3

completeness_score_plot <- figure(width = 800, title = "core GF completeness scores for different assemblies (original (NCGR) vs. DIB-lab)") %>%
  ly_points(exps_zen$completeness_score, exps_mic$completeness_score,
            hover = hoverdfcGF) %>%
  ly_points(exps_zen$completeness_score[exps_zen$title %in% titles.highlight], exps_mic$completeness_score[exps_mic$title %in% titles.highlight], col = 'red') %>%
  #ly_abline(0, 1, legend = "Line with slope = 1") %>%
  x_axis(label = 'scores DIB-lab') %>%
  y_axis(label = "scores NCGR")

completeness_score_plot

###############################

completeness_score_plot <- figure(width = 700, height = 600, title = "core GF completeness scores for different assemblies (original (NCGR) vs. DIB-lab)") %>%
  ly_boxplot(as.factor(c(exps_mic$desc_query, exps_zen$desc_query)), c(exps_mic$completeness_score, exps_zen$completeness_score), width = 0.4) %>%
  #ly_points(exps_zen$completeness_score[exps_zen$title %in% tit], exps_mic$completeness_score[exps_mic$title %in% tit], col = 'red') %>%
  #ly_abline(0, 1, legend = "Line with slope = 1") %>%
  x_axis(label = 'Assembly') %>%
  y_axis(label = "core GF completeness score")

completeness_score_plot

# histogram
exps_All = rbind(exps_mic, exps_zen)
vlines <- data.frame(xint =  c(mean(exps_mic$completeness_score), mean(exps_zen$completeness_score)),mean.score = unique(exps_All$desc_query))
ggplot(data = exps_All, aes(x=completeness_score, fill = desc_query)) + 
  geom_histogram(alpha = 0.3, binwidth = 0.05, position = 'identity') +
  geom_vline(data = vlines,aes(xintercept = xint,colour = mean.score), linetype = "dashed") 
  



ggplot(data = All_experiments, aes(x=completeness_score, fill = desc_query)) + 
  geom_histogram(alpha = 0.3, binwidth = 0.05, position = 'identity') 




###### TEST field #####

#### TEST CASE ####

# Bathycoccus versus Aureococcus

cols = distinctColorPalette(4)
exps_AB = rbind(select_exp(config, 10, desc_query = c('BATHY', 'imicrobe'), color = cols[1]),
                select_exp(config, 10, desc_query = c('AUREO', 'imicrobe'), color = cols[2]))
exps_AB = rank_on_taxonomy(exps_AB)

exps_AB = transcripts_count(config, exps_AB)

tax_comp_AB = tax_composition_kaijuReport(data.location, df = exps_AB, tax_level = 'genus')
plot_tax_composition(tax_comp_AB, cutoff = 0.05)


# PCA
xx = GF_comparison_naive(config, exps_AB)
xx = xx[,-1]
xxt =t(xx)
pcs = prcomp(xxt)
summ = summary(pcs)
summ

### rBokeh plot
pca_plot <- figure(width = 800, legend_location = 'bottom_right') %>%
  ly_points(pcs$x[,1], pcs$x[,2],
            color = exps_AB$desc_query, glyph = exps_AB$desc_query,
            hover = exps_AB["unique_title"], size = 15) %>%
  x_axis(label = glue('PC1 (explaining {x}% of variation)', x = summ$importance[2,1]*100)) %>%
  y_axis(label = glue('PC2 (explaining {x}% of variation)', x = summ$importance[2,2]*100))

pca_plot


###for zenodo
#exps_zen_toptax =  add_toptax(exps_zen, tax_comp_zen)

# PCA
xxz = GF_comparison_naive(config, exps_zen)
xxz = xxz[,-1]
xxzt =t(xxz)
pcs = prcomp(xxzt)
pcasum = summary(pcs)
pcasum

### rBokeh plot
hoverdfPCA = as.data.frame(cbind(exps_zen$title, exps_zen$species_MMETSP))
colnames(hoverdfPCA) = c('sample name', 'species')


pca_plot1 <- figure(width = 800, height = 800, xlim =c(-45,80), title = "PCA on GF presence vectors of 90 MMETSP samples (DIB-lab assembly) Hover over samples to get annotation") %>%
  ly_points(pcs$x[,1], pcs$x[,2],
            color = exps_zen$phylum_MMETSP, glyph = exps_zen$genus_MMETSP,
            hover = hoverdfPCA, size = 15) %>%
  x_axis(label = glue('PC1 (explaining {x}% of variation)', x = pcasum$importance[2,1]*100)) %>%
  y_axis(label = glue('PC2 (explaining {x}% of variation)', x = pcasum$importance[2,2]*100))

pca_plot1

### now for all samples


NOG.matrix = GF_comparison_collapsed(config, All_experiments) 



exps_All = rbind(exps_mic, exps_zen)



tax_comp_All = tax_composition_kaijuReport(data.location, 'genus', exps_All)
plot_tax_composition(tax_comp_All)


# PCA
xx = GF_comparison_naive(config, exps_All) #patience required: 180 samples = 1m
xx = xx[,-1]
xxt =t(xx)
pcs = prcomp(xxt)
#pcs = prcomp(xxt)
sumt = summary(pcs)
sumt

# ### rBokeh plot
# pca_plot_all <- figure() %>%
#   ly_points(pcs$x[,1], pcs$x[,2],
#             color = exps_All$desc_query, glyph = exps_All$desc_query,
#             hover = exps_All["unique_title"], size = 15) %>%
#   x_axis(label = glue('PC1 (explaining {x}% of variation)', x = sumt$importance[2,1]*100)) %>%
#   y_axis(label = glue('PC2 (explaining {x}% of variation)', x = sumt$importance[2,2]*100))
# 
# 
# pca_plot_all


blob_size.tot_trs = 5+ (exps_All$transcripts_count_total/1000)
blob_size.trs_annot =  30*exps_All$transcripts_percent_annot



hoverdf.all = as.data.frame(cbind(exps_All$title,exps_All$desc_query, exps_All$phylum_MMETSP, exps_All$species_MMETSP))
colnames(hoverdf.all) = c('sample name','assembly', 'phylum',' species')

ids.1 = exps_All$experiment_id[exps_All$completeness_score < 0.75]


pca_plot_all <- figure(width = 800, height = 800, xlim =c(-60,80), title = "PCA on GF presence vectors of all samples, glyph size ~ # transcripts, red = core_GF_score < 0.75 ") %>%
  ly_points(pcs$x[,1], pcs$x[,2],
            glyph = exps_All$genus_MMETSP, color = exps_All$desc_query,
            hover = hoverdf.all, size = blob_size.tot_trs) %>%
  ly_points(pcs$x[,1][exps_All$experiment_id %in% ids.1], pcs$x[,2][exps_All$experiment_id %in% ids.1], col = 'red') %>%
  x_axis(label = glue('PC1 (explaining {x}% of variation)', x = sumt$importance[2,1]*100)) %>%
  y_axis(label = glue('PC2 (explaining {x}% of variation)', x = sumt$importance[2,2]*100))

pca_plot_all

#################### with QC

#remove samples with low core gf comp score
exps_All_QC = exps_All[exps_All$completeness_score > 0.8,]

xx = GF_comparison_naive(config, exps_All_QC)
xx = xx[,-1]
xxt =t(xx)
pcs_QC = prcomp(xxt)
#pcs = prcomp(xxt)
sumt_QC = summary(pcs_QC)
sumt_QC

hoverdf.all = as.data.frame(cbind(exps_All_QC$title,exps_All_QC$desc_query, exps_All_QC$phylum_MMETSP, exps_All_QC$species_MMETSP))
colnames(hoverdf.all) = c('sample name','assembly', 'phylum',' species')

blob_size.tot_trs_QC = 5+ (exps_All_QC$transcripts_count_total/1000)
blob_size.trs_annot_QC =  50*exps_All_QC$transcripts_percent_annot

pca_plot_all <- figure(width = 800, height = 800, xlim =c(-60,80), title = "PCA on GF presence vectors of all samples, glyph size ~ # transcripts, red = < 6000 transcripts ") %>%
  ly_points(pcs_QC$x[,1], pcs_QC$x[,2],
            glyph = exps_All_QC$genus_MMETSP, color = exps_All_QC$desc_query,
            hover = hoverdf.all, size =blob_size.trs_annot_QC) %>%
  ly_points(pcs$x[,1][exps_All_QC$experiment_id %in% ids.1], pcs$x[,2][exps_All_QC$experiment_id %in% ids.1], col = 'red') %>%
  x_axis(label = glue('PC1 (explaining {x}% of variation)', x = sumt_QC$importance[2,1]*100)) %>%
  y_axis(label = glue('PC2 (explaining {x}% of variation)', x = sumt_QC$importance[2,2]*100))

pca_plot_all

## heatmap

config <- fromJSON(file="../../../config_connect_trapid.json")
usr_id = get_user_ID(config, "nidil")
exps_chlorophyta = select_exp(config, usr_id, refDB_query = "eggnog", phylum = "chlorophyta")
exps_chlorophyta = rank_on_taxonomy(exps_chlorophyta)
exps_chlorophyta = transcripts_count(config, exps_chlorophyta)

GF.data.original = GF_comparison_naive(config, exps_chlorophyta)
print(nrow(GF.data.original))

colnames(GF.data.original) = exps_chlorophyta$species_MMETSP

#heatmap of orignal dat only clustered on samples
un = c(distinctColorPalette(length(unique(exps_chlorophyta$genus_MMETSP))))
cc = c()
for (genus in exps_chlorophyta$genus_MMETSP){
  i = match(genus, unique(exps_chlorophyta$genus_MMETSP))
  print(paste(i, genus, un[i]))
  cc = c(cc, un[i])
}

heatmap(data.matrix(t(GF.data.original[,-1])), 
        Colv = NA, scale='none', 
        RowSideColors = cc
        )


# features selection, unique gene families throw away? not relevant if we want to cluster samples Based on *presence*, but as we also are interested in 
GF.data = GF.data.original[rowSums(GF.data.original[,-1]) > 1,]
print(nrow(GF.data))

GF.matrix = data.matrix(GF.data[,-1])
exps_chlorophyta$experiment_id
#colnames(GF.matrix) =
exps_chlorophyta$genus_MMETSP[exps_chlorophyta$transcripts_count_total <1000]



subdat = GF.matrix[1:100,]


library(heatmaply)
heatmap(subdat, scale = "none" )
# check other dist mb correlation
# switch testset to eggmog
heatmaply(subdat, Rowv = NA, labCol = exps_chlorophyta$genus_MMETSP, file = "/home/nidil/Documents/Project_TRAPID/Scripts/Compare/Results/")
