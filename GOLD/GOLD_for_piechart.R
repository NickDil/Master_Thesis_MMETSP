library('RMySQL')
library('randomcoloR')
library('taxize')
# GOLD DB (GOLD Release v.6 , File last generated: 04 Jul, 2018) downloaded on jul 5 2018 21:00
path2Gold = "goldData.xls"

#na.strings=c(""," ","NA")
gold.data = read.table(path2Gold, header = T, sep = "\t", fill = T)

# Move colnames one col to make them match
colnames(gold.data) = c(colnames(gold.data)[-1], "")


# Convert coluns of interest to uppercase -> more robust
gold.data$PROJECT.TYPE = as.character(toupper(gold.data$PROJECT.TYPE))
gold.data$DOMAIN = as.character(toupper(gold.data$DOMAIN))
gold.data$PROJECT.STATUS = as.character(toupper(gold.data$PROJECT.STATUS))
gold.data$PHYLUM = as.character(gold.data$PHYLUM)
gold.data$NCBI.TAXON.ID = as.character(gold.data$NCBI.TAXON.ID)




####################################### copy MMETSP paper GOLD data  #######################################
MMETSP.orig = c("Glaucophytes", "Rhodoophytes", "Viridiplantae", "Unknown", "Katablepharids", "Biliphytes", "Telonemids", "Stramenopiles", "Rhizaria", "Dinoflagellates",
                "Apicomplexans" ,"Ciliates", "Haptophytes", "Cryptophytes", "Excavates", "Opisthokonts", "Amoebozoa")

excavata = c("33682", "85705", "136088")
names(excavata) =c("Euglenozoa", "Ancyromonadidae","Malawimonas")
excavata.string = "33682, 85705, 136088"
taxa = data.frame(tax = c("Glaucophytes", "Rhodoophytes", "Viridiplantae", "Unknown", "Stramenopiles", "Rhizaria", "Dinoflagellates",
                          "Apicomplexans" ,"Ciliates", "Haptophytes", "Cryptophytes", "Excavates", "Excavates","Excavates",
                          "Opisthokonts", "Amoebozoa", "Katablepharids"),tax_id = c("38254", "2763", "33090","no_txid", "33634", "543769", "2864", "5794",
                                                                  "5878", "2830", "3027", "33682", "85705", "136088", "33154", "554915", "339960"), stringsAsFactors= FALSE)
# QQQ = gold.data$PROJECT.TYPE == "WHOLE GENOME SEQUENCING" & (gold.data$PROJECT.STATUS == "COMPLETE AND PUBLISHED" | gold.data$PROJECT.STATUS == "COMPLETE") & gold.data$DOMAIN == "EUKARYAL"
QQQ = gold.data$PROJECT.TYPE == "WHOLE GENOME SEQUENCING" & gold.data$SEQUENCING.STATUS == "Complete" & gold.data$DOMAIN == "EUKARYAL"
work.data = gold.data[QQQ,]
work.data["MMETSP_tax"] = NA
tax_ids = work.data$NCBI.TAXON.ID

i = 1
for (project_tax in tax_ids){
  print(project_tax)
  print(i)
  CC = classification(project_tax, db='ncbi')
  lineage = CC[[1]]$id
  for (lin in lineage){
    if(lin %in% taxa$tax_id){
      work.data[i,"MMETSP_tax"] = taxa[taxa$tax_id == lin, 1]
    }
  }
i = i+1}

# replace nan with unknown
work.data$MMETSP_tax[is.na(work.data$MMETSP_tax)] = "Unknown"

ppdata = table(work.data$MMETSP_tax)

# col = c("#81C8D5", "#86E562" ,  "salmon1" , "#D472DB")
# col = c(distinctColorPalette(length(ppdata)))
MMETSP.orig = c("Glaucophytes", "Rhodoophytes", "Viridiplantae", "Unknown", "Katablepharids", "Biliphytes", "Telonemids", "Stramenopiles", "Rhizaria", "Dinoflagellates",
                "Apicomplexans" ,"Ciliates", "Haptophytes", "Cryptophytes", "Excavates", "Opisthokonts", "Amoebozoa")

col.orig = c("#6fccde", "#9f423f", "#8dc741", "#666767", "#f7ec13", "#ce7c38", 
        "#c2b69c", "#ed2127", "#ee2b7b", "#8165a3", "#804099", "#b99bc9",
        "#f15b2b", "#ba529f", "#bdbfc1", "#3853a4", "#4e82c0")
names(col.orig) = MMETSP.orig
#col["Unknown"] = "dimgrey"
# pie like MMETSP

ppdata.col = col.orig[which(MMETSP.orig %in% names(ppdata))] #get correct colors
ppdata.col = ppdata.col[order(names(ppdata.col))] #order alphabetically

pie(ppdata, col = ppdata.col, #labels = paste0(round(ppdata/sum(ppdata)*100, 2), "%"), 
    labels = "",
    main = "Distribution of sequenced genomes from eukaryotes", init.angle = 60)
legend(1,1, names(col.orig), fill = col.orig, cex = 0.8, title = "Taxon")


####################################### Summarize MMETSP data taxonomy #######################################
mmetsp.taxa = data.frame(tax_id= read.table("mmetsp_taxon_id", col.names = "MMETSP_tax_id"), MMETSP_tax=NA)
tax_ids_mmetsp = mmetsp.taxa$MMETSP_tax_id

i = 1
while (i <= length(tax_ids_mmetsp)){
  project_tax = as.character(tax_ids_mmetsp[i])
  print(project_tax)
  print(i)
  if (project_tax == "NULL"){
    i=i+1
    next
  }
  CC = classification(project_tax, db='ncbi')
  lineage = try(CC[[1]]$id)
  if (class(lineage) == "try-error"){
    i=i+1
    next
  }
  for (lin in lineage){
    if(lin %in% taxa$tax_id){
      mmetsp.taxa[i,"MMETSP_tax"] = taxa[taxa$tax_id == lin, 1]
    }
  }
  i = i+1}

# replace nan with unknown
mmetsp.taxa$MMETSP_tax[is.na(mmetsp.taxa$MMETSP_tax)] = "Unknown"

ppdata.mmetsp = table(mmetsp.taxa$MMETSP_tax)
ppdata.mmetsp.col = col.orig[which(MMETSP.orig %in% names(ppdata.mmetsp))] #get correct colors
ppdata.mmetsp.col = ppdata.mmetsp.col[order(names(ppdata.mmetsp.col))] #order alphabetically

# pie like MMETSP
pie(ppdata.mmetsp, col = ppdata.mmetsp.col, #labels = paste0(round(ppdata/sum(ppdata)*100, 2), "%"), 
    labels = "",
    main = "MMETSP transcriptomes", init.angle = 70)
legend(1,1, MMETSP.orig, fill = col.orig, cex = 0.8, title = "Taxon")


#####################################################################################################################




query1 = gold.data$PROJECT.TYPE == "WHOLE GENOME SEQUENCING" & gold.data$PROJECT.STATUS == "COMPLETE AND PUBLISHED" 
#query = gold.data$PROJECT.TYPE == "WHOLE GENOME SEQUENCING" & gold.data$DOMAIN == "EUKARYAL" 
# For all organisms check domain spread of completed WGS projects
gold.DOM = gold.data[query1,]
gold.DOM = as.data.frame(apply(gold.DOM, 2, as.character))
#rm(gold.data, query)


#gold.DOM = gold.DOM[gold.DOM$DOMAIN != "VIRU

gold.DOM[gold.DOM$DOMAIN == "","DOMAIN"] = "VIRUS"
n = nrow(gold.DOM)

gold.phyla = as.character(gold.DOM$PHYLUM)
gold.phyla[gold.phyla == " "] = "Phylum unknown"
table(gold.phyla)
gold.kingdom = as.character(gold.DOM$KINGDOM)
gold.kingdom[gold.kingdom == " "] = "kingdom unknown"

gold.domain = as.character(gold.DOM$DOMAIN)
gold.domain[gold.domain == ""] = "Unknown"
table(gold.domain)
piedata = table(gold.domain)

# col = c("#81C8D5", "#86E562" ,  "salmon1" , "#D472DB")
col = c(distinctColorPalette(4))

# WITH VIRUSES
pie(piedata, col = col, labels = paste0(round(c(piedata[1], piedata[2], piedata[3], piedata[4])/n*100, 2), "%"), main = "Domain distribution of available complete genome sequences")
legend(1,1, names(piedata), fill = col, cex = 0.8, title = "DOMAIN")

# WITHOUT VIRUSES

pie(piedata[1:3], col = col, labels = paste0(round(c(piedata[1], piedata[2], piedata[3])/(n-piedata[4])*100, 2), "%"), main = "Domain distribution of available complete genome sequences")
legend(1,1, names(piedata[1:3]), fill = col, cex = 0.8, title = "DOMAIN")


# Total effort?
table(gold.data$DOMAIN, gold.data$PROJECT.STATUS)
effortdata = table(gold.data$DOMAIN)[c("ARCHAEAL", "BACTERIAL" , "EUKARYAL", "VIRUS")]
col = c(distinctColorPalette(length(effortdata)))
pie(effortdata, col = col, labels = paste0(round(effortdata/sum(effortdata)*100, 2), "%"), main = "Sequencing effort towards the 4 domains of life")
legend(1,1, names(effortdata), fill = col, cex = 0.8, title = "DOMAIN")



# for phyla
query2 = gold.data$PROJECT.TYPE == "WHOLE GENOME SEQUENCING" & gold.data$DOMAIN == "EUKARYAL" 

gold.PHY = gold.data[query2,]
gold.PHY = as.data.frame(apply(gold.PHY, 2, as.character))
gold.PHY$PHYLUM = as.character(gold.PHY$PHYLUM)
gold.PHY[gold.PHY$PHYLUM == " ", "PHYLUM"] = "Unknown"
table(gold.PHY$PHYLUM)
piephy1 = table(gold.PHY$PHYLUM)

X = 1

othersc = sum(piephy1[piephy1/sum(piephy1)*100 <= X])
names(othersc) = "Other"
piephy = c(piephy1[piephy1/sum(piephy1)*100 > X], othersc)
col.phyla = distinctColorPalette(length(piephy))

pie(piephy, col = col.phyla, labels = paste0(round(piephy/sum(piephy)*100, 2), "%"), main = "Distribution of sequencing effort in the eukaryote domain", init.angle = 50)
legend(1.1,1, names(piephy), fill = col.phyla, cex = 0.8, title = "PHYLUM")








table.P = table.Phyla

#Or trimmed
table.P = table.Phyla[table.Phyla/n*100 >= 1]
table.P["Other"] = sum(table.Phyla[table.Phyla/n*100 < 1])

# names.kingdom = names(table.K)
# col.kingdom = c(distinctColorPalette(length(unique(gold.kingdom))))
# names(col.kingdom) = names.kingdom
# col.kingdom["kingdom unknown"] = "grey15"
# pie(table.K, col = col.kingdom, labels = '',  main = "Distribution of sequenced genomes from eukaryotes")
# legend(-1.6, 1, names.kingdom, fill = col.kingdom, cex = 0.8, title = "Kingdom")

names.phyla = names(table.P)
col.phyla = distinctColorPalette(length(unique(names.phyla)))
names(col.phyla) = names.phyla
col.phyla["Phylum unknown"] = "grey15"
col.phyla["Other"] = "grey35"
pie(table.P, col = col.phyla, labels = paste0(round(table.P/n*100, 2), "%"), main = "Distribution of sequenced genomes from eukaryotes", init.angle = 50)
legend(1.1,1, names.phyla, fill = col.phyla, cex = 0.8, title = "PHYLUM")

col.phyla[8] = "pink2"



col.phyla = col.good 


