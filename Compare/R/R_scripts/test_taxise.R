library(taxize)

phylum = 'Bacillariophyta' 

phydi = lapply(unique(exps_mic$MMETSP_txid), tax_name, db = 'ncbi', '[', 7)
unlist(phydi[1])

txid  = unique(exps_mic$txid_MMETSP)[5]

classification(txid, db = 'ncbi', rows = 5)

xx =unique(exps_mic$MMETSP_txid)

jj = classification(xx, db = 'ncbi')

ncbi_downstream(phylum, downto = 'species')


species = paste(exps_mic$MMETSP_genus, exps_mic$MMETSP_species)
specis = unique(species)
tax_name(specis, get= 'phylum', db = 'ncbi')




ncbi_get_taxon_summary(c(1430660, 4751))


spnames = unique(exps_mic$txid_MMETSP)
taxout = classification(spnames, db = 'ncbi')

tr = class2tree(taxout)

dist.mat = tr$distmat
clust.obj = hclust(dist.mat)
perm = clust.obj$order
spnames[perm]


plt = ggplot(x_plt_out, aes(x = unique_title, y = reads_percent, fill = tax_annot)) +
  geom_bar(position = position_stack(), stat = "identity") +
  scale_y_continuous(labels = scales::percent) +
  geom_text(aes(label = paste0(round(reads_percent, 3)*100,"%")), position = position_stack(vjust = 0.5), size = 3) +
  labs(x="", y="percentage") +
  ggtitle(paste0(title, ", cutoff=", cutoff*100, "% of transcripts"))
plt = plt + theme(legend.title = element_blank(),legend.position="bottom", legend.direction="horizontal") + coord_flip()




options(warn = -1) 



for (col in exps_AB[,]){
  print(typeof(col))
  
}


