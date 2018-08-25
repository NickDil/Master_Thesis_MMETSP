
# functions for the compare.R scripts

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

########## FUNCTIONS ##########

get_user_ID <- function(config, name){
  
  mydb = dbConnect(MySQL(), user=config$trapid_db_user, password=config$trapid_db_pswd, dbname=config$trapid_db_name, host=config$trapid_db_server)
  SQLquery = glue("SELECT user_id from authentication where email LIKE '{name}%'")
  rs = dbGetQuery(mydb, SQLquery)
  #print(usrid)
  dbDisconnect(mydb)
  return(rs)
}

merge_exp <- function(dfA, dfB, by = 'experiment_id'){
  df_out = inner_join(dfA, dfB, by = by)
  return(df_out)
}

select_exp <- function(trapid_db_server, trapid_db_name, trapid_db_port, trapid_db_user, trapid_db_pswd, user_id, desc_query = NULL, tax_id = NULL, refDB_query = NULL, phylum = NULL, genus = NULL, species = NULL, minimal_nr_transcripts = 1, color = randomColor(1)){
  mydb = dbConnect(MySQL(), user=trapid_db_user, password=trapid_db_pswd, dbname=trapid_db_name, host=trapid_db_server)
  select_query = "SELECT experiments.experiment_id, experiments.title"
  from_query = " from experiments"
  where_query = glue(" WHERE experiments.user_id = {user_id}")
  grp_query = ""
  
  if (!is.null(desc_query)){
    for (qq in desc_query){
      where_query = paste0(where_query, glue(" AND experiments.description LIKE '%{qq}%'"))
    }
  }
  
  if (!is.null(refDB_query)){
    for (qq in refDB_query){
      where_query = paste0(where_query, glue(" AND experiments.used_plaza_database LIKE '%{qq}%'"))
    }
  }
  
  if (!is.null(tax_id)){
    if (is.character(tax_id)){
      mini_query = glue_sql("SELECT txid FROM full_taxonomy WHERE scname IN ({tax_id*})", .con = mydb)
      tax_id = dbGetQuery(mydb, mini_query)
      tax_id = tax_id$txid
    }
    
    from_query = " FROM transcripts_tax LEFT JOIN experiments ON transcripts_tax.experiment_id = experiments.experiment_id"
    where_query = paste0(where_query, glue_sql(" AND transcripts_tax.txid IN ({tax_id*})", .con = mydb))
    grp_query = paste0(grp_query, glue(" GROUP BY experiment_id HAVING COUNT(transcripts_tax.txid)  >= {minimal_nr_transcripts}"))
  }
  
  if (!is.null(c(phylum, genus, species))){
    if (is.null(phylum)) {phylum = "" }
    if (is.null(genus)) {genus = "" }
    if (is.null(species)) {species = "" }
    
    samples.all = select_sample_tax(config, phylum, genus, species)
    samples.title = samples.all$title
    
    where_query = paste0(where_query, glue_sql(" AND experiments.title IN ({samples.title*})", .con = mydb))
  }
  
  
  # SQLquery = glue("SELECT experiment_id, title from experiments where user_id = {user_id} AND description LIKE '%{desc_query}%'")
  SQLquery = paste0(select_query, from_query, where_query, grp_query)
  # print(SQLquery)
  rs = dbGetQuery(mydb, SQLquery)
  
  dbDisconnect(mydb)
  
  out = rs[order(rs$title),]
  out["color_label"] = color
  out["desc_query"] = paste(desc_query, collapse=', ' )
  out["tax_query"] = paste(tax_id, collapse=', ' )
  out["refDB_query"] = paste(refDB_query, collapse=', ' )
  out["unique_title"] = paste(out$title, out$desc_query, out$refDB_query, out$tax_id)
  
  out = add_MMETSP_annotation(config, out)
  
  print(paste("You have selected",length(rs$title), "experiments! With color label =", color))
  
  return(out)
}

select_sample_tax <- function(config, phylum = "", genus = "", species = "") {
  
  mydb.meta = dbConnect(MySQL(), user=config$trapid_db_user, password=config$trapid_db_pswd, dbname= 'db_trapid_mmetsp_metadata', host=config$trapid_db_server)
  
  SQL_query = glue_sql("Select sample_name, phylum, genus, species, taxon_id FROM mmetsp_sample_attr where phylum IN ({phylum*}) OR genus in ({genus*}) OR species in ({species*})", .con = mydb.meta)
  rs = dbGetQuery(mydb.meta, SQL_query)
  dbDisconnect(mydb.meta)
  
  colnames(rs) = c('title', 'phylum_MMETSP', 'genus_MMETSP', 'species_only_MMETSP', 'txid_MMETSP')
  rs["species_MMETSP"] = paste(rs$genus, rs$species_only_MMETSP)
  return(rs)
}

add_MMETSP_annotation <- function(config, df){
  
  titles = df$title
  
  mydb.meta = dbConnect(MySQL(), user=config$trapid_db_user, password=config$trapid_db_pswd, dbname= 'db_trapid_mmetsp_metadata', host=config$trapid_db_server)
  SQL_query = glue_sql("Select sample_name, phylum, genus, species, taxon_id FROM mmetsp_sample_attr where sample_name IN ({titles*})", .con = mydb.meta)
  rs = dbGetQuery(mydb.meta, SQL_query)
  dbDisconnect(mydb.meta)
  
  colnames(rs) = c('title', 'phylum_MMETSP', 'genus_MMETSP', 'species_only_MMETSP', 'txid_MMETSP')
  rs["species_MMETSP"] = paste(rs$genus, rs$species_only_MMETSP)
  df = merge_exp(df, rs, by = "title")
  
  return(df)
}

rank_on_taxonomy <- function(df) {
  # Function returns the dataframe ordered by hierarchical clustering of samples of different tax ID annotation
  
  print(paste("START rearanging dataframe based on NCBI taxonomy", format(Sys.time(), "%X")))
  
  #1 Get taxonomic clustering for taxa involved
  # get tax ids for samples
  txids = unique(df$txid_MMETSP)
  
  #Generate classification and make tree (distance matrix we need)
  txids.class = classification(txids, db = 'ncbi')
  txids.tree = class2tree(txids.class)
  dist.mat = txids.tree$distmat
  
  # Cluster again on distance matrix, we want the $order element from the hclust return to get permutation of txids
  clust.obj = hclust(dist.mat)
  perm = clust.obj$order
  txids.perm = txids[perm]
  
  #2 premutate dataframe
  df["reorder_tax"] = match(df$txid_MMETSP, txids.perm)
  df = arrange(df, reorder_tax)
  
  print(paste("STOP:", format(Sys.time(), "%X")))
  return(df)
}

transcripts_count <- function(config, df){
  print(paste("START counting transcripts:", format(Sys.time(), "%X")))
  exp_ids = df$experiment_id
  mydb = dbConnect(MySQL(), user=config$trapid_db_user, password=config$trapid_db_pswd, dbname=config$trapid_db_name, host=config$trapid_db_server)
  SQLquery = glue_sql("SELECT experiment_id, COUNT(experiment_id) FROM transcripts WHERE experiment_id IN ({exp_ids*}) GROUP BY experiment_id", .con = mydb)
  rs = dbGetQuery(mydb, SQLquery)
  dbDisconnect(mydb)
  
  colnames(rs) = c("experiment_id", "transcripts_count_total")
  out = merge_exp(df, rs)
  print(paste("STOP counting transcripts:", format(Sys.time(), "%X")))
  return(out)
}

transcripts_in_GF_count <- function(config, df){
  print(paste("START counting transcripts in GF:", format(Sys.time(), "%X")))
  exp_ids = df$experiment_id
  mydb = dbConnect(MySQL(), user=config$trapid_db_user, password=config$trapid_db_pswd, dbname=config$trapid_db_name, host=config$trapid_db_server)
  SQLquery = glue_sql("SELECT experiment_id, COUNT(gf_id) from transcripts WHERE experiment_id IN ({exp_ids*}) GROUP BY experiment_id", .con = mydb)
  rs = dbGetQuery(mydb, SQLquery)
  dbDisconnect(mydb)
  
  colnames(rs) = c("experiment_id", "total_transcripts_in_GF_count")
  out = merge_exp(df, rs)
  print(paste("STOP counting transcripts in GF:", format(Sys.time(), "%X")))  
  return(out)
}

annotated_transcripts_count <- function(df, txcmp.df) {
  
  rest.df = aggregate( cbind(transcripts_count, transcripts_percent) ~ experiment_id, data = txcmp.df[txcmp.df$tax_annot != 'unclassified',], FUN = sum)
  
  colnames(rest.df) = c("experiment_id", 'transcripts_count_annot', 'transcripts_percent_annot')
  out = merge_exp(df, rest.df)
  return(out)
  
}

tax_composition_species <- function(config, df1){
  ### OUTDATED => USE 'tax_composition_kaijuReport()'
  # Homemade (Nick) subroutine to get the taxonomic composition of a set of experiments. 
  # Probably not very well optimalized when compared to the scripts from Kaiju git repo
  
  print(paste("START summarizing taxonomic binning results:", format(Sys.time(), "%X")))  
  exp_ids = df1$experiment_id
  
  SQL_compo = glue_sql("select experiment_id, full_taxonomy.scname, full_taxonomy.tax, transcripts_tax.txid, count(transcripts_tax.txid) 
                       from transcripts_tax left join full_taxonomy on transcripts_tax.txid = full_taxonomy.txid 
                       where transcripts_tax.experiment_id IN ({exp_ids*}) 
                       GROUP BY transcripts_tax.txid, experiment_id")
  
  mydb = dbConnect(MySQL(), user=config$trapid_db_user, password=config$trapid_db_pswd, dbname=config$trapid_db_name, host=config$trapid_db_server)
  rs = dbGetQuery(mydb, SQL_compo)
  dbDisconnect(mydb)
  
  # rs[is.na(rs)] <-"Unclassified"
  colnames(rs) = c("experiment_id", "tax_annot", "full_taxonomy", "txid", "transcripts_count")
  out = merge_exp(df1, rs)
  out['transcripts_percent'] = out["transcripts_count"]/out['transcripts_count_total']
  print(paste("STOP summarizing taxonomic binning results:", format(Sys.time(), "%X")))  
  
  return(out)
}

tax_composition_kaijuReport <- function(data.location, tax_level, df) {
  # kaiju summary files should be present in the directories of your experiment_data!!
  # Run the kaijuPhylumReport.sh shell script to get these summaries
  expids = df$experiment_id
  
  # First one
  expid.file = paste0(data.location, expids[1], "/kaiju/kaiju.out.", tax_level, ".", expids[1], ".summary")
  expid.report = read.table(expid.file, sep = '\t', header = TRUE, comment.char = "-")
  expid.report["experiment_id"] = expids[1]
  out = expid.report
  
  # Now for the rest
  for (expid in df$experiment_id[-1]){
    expid.file = paste0(data.location, expid,"/kaiju/kaiju.out.", tax_level, ".", expid, ".summary")
    expid.report = read.table(expid.file, sep = '\t', header = TRUE, comment.char = "-")
    expid.report["experiment_id"] = expid
    out = rbind(out, expid.report)
  }
  
  colnames(out) = c('transcripts_percent', 'transcripts_count', 'tax_annot', "experiment_id")
  out$transcripts_percent = out$transcripts_percent/100
  out$tax_annot = as.character(out$tax_annot)
  out = merge_exp(df, out)
  return(out)
}

plot_tax_composition <- function(df, cutoff = 0.10, title = "Taxonomic composition"){
  
  # dataframe should have following columns:  transcripts_count_total, transcripts_count, transcripts_percent and tax_annot 
  
  # FILTER ~ cutoff
  if (cutoff < 1){
    x_plt = df[df$transcripts_percent >= cutoff,]
    switchP = TRUE
  } else {
    x_plt = df[df$transcripts_count >= cutoff,]
    switchP = FALSE
  }
  
  # Create "OTHER" category
  tot_select = aggregate(cbind(transcripts_count, transcripts_percent) ~ experiment_id, data=x_plt, FUN=sum)
  tot = aggregate(. ~ experiment_id, data=x_plt, FUN=unique)
  rest_transcripts_count = as.numeric(levels(tot$transcripts_count_total))[tot$transcripts_count_total] - tot_select$transcripts_count
  rest_transcripts_percent = 1 - tot_select$transcripts_percent
  other_df = as.data.frame(tot)
  other_df["tax_annot"] = "other"
  other_df["transcripts_count"] = rest_transcripts_count
  other_df["transcripts_percent"] = rest_transcripts_percent
  
  
  x_plt_out = merge(x_plt, other_df, all = TRUE)
  x_plt_out$tax_annot[x_plt_out$tax_annot == 'unclassified'] = NA
  
  # reorder dataframe
  x_plt_out["reorder_tax"] = as.numeric(x_plt_out$reorder_tax)
  x_plt_out = arrange(x_plt_out, reorder_tax)
  
  x_plt_out$unique_title = as.character(x_plt_out$unique_title)
  x_plt_out$unique_title <- factor(x_plt_out$unique_title, levels=unique(x_plt_out$unique_title))
  
  # PLOTTING
  
  if (switchP){
    
    plt = ggplot(x_plt_out, aes(x = unique_title, y = transcripts_percent, fill = tax_annot)) +
      geom_bar(position = position_stack(), stat = "identity") +
      scale_y_continuous(labels = scales::percent) +
      geom_text(aes(label = paste0(round(transcripts_percent, 3)*100,"%")), position = position_stack(vjust = 0.5), size = 3) +
      labs(x="", y="percentage") +
      ggtitle(paste0(title, ", cutoff=", cutoff*100, "% of transcripts"))
    
  }else{
    
    plt = ggplot(x_plt_out, aes(x = unique_title, y = transcripts_count, fill = tax_annot)) +
      geom_bar(position = position_stack(), stat = "identity") +
      #geom_text(aes(label = paste(transcripts_count)), position = position_stack(vjust = 0.5), size = 3) +
      labs(x="", y="transcript count") +
      ggtitle(paste0(title, ", cutoff=", cutoff, " transcripts"))
  }
  plt = plt + theme(legend.title = element_blank(),legend.position="bottom", legend.direction="horizontal") + coord_flip()
  
  
  return(plt)
  ly_b
}

plot_agreement <- function(dfx, dfy, level = "genus", highlight = "", percent = TRUE) {
  
  label.x = paste(dfx$desc_query[1], dfx$tax_query[1], dfx$refDB_query[1])
  label.y = paste(dfy$desc_query[1], dfy$tax_query[1], dfy$refDB_query[1])
  
  tax_agreement_dfx = dfx[dfx[paste0(level, "_MMETSP")] == dfx['tax_annot'],]
  tax_agreement_dfy = dfy[dfy[paste0(level, "_MMETSP")] == dfy['tax_annot'],]
  
  tax_agreement = full_join(tax_agreement_dfx, tax_agreement_dfy, by = 'title')
  tax_agreement[is.na(tax_agreement)] = 0
  
  
  
  if (percent){
    #Get the to be highlighted points
    highlight.x = tax_agreement$transcripts_percent.x[tax_agreement$title %in% highlight]*100
    highlight.y = tax_agreement$transcripts_percent.y[tax_agreement$title %in% highlight]*100
    
    hoverdf = as.data.frame(cbind(tax_agreement$title, tax_agreement[paste0(level, "_MMETSP.x")], tax_agreement$transcripts_percent.x*100, tax_agreement$transcripts_percent.y*100))
    colnames(hoverdf) = c('sample name', "MMETSP annotation",glue('% transcripts for {label.x}'), glue('% of transcripts for {label.y}'))
    
    agreement_plot <- figure(width = 800, title = glue("Percent transcripts with same {level} as MMETSP annotation")) %>%
      ly_points(tax_agreement$transcripts_percent.x*100, tax_agreement$transcripts_percent.y*100,
                hover = hoverdf) %>%
      ly_points(highlight.x, highlight.y, col = 'red') %>%
      ly_abline(0, 1, legend = "Line with slope = 1") %>%
      x_axis(label = paste(colnames(hoverdf)[3])) %>%
      y_axis(label = paste(colnames(hoverdf)[4]))
    
  } else {
    #Get the to be highlighted points
    highlight.x = tax_agreement$transcripts_count.x[tax_agreement$title %in% highlight]
    highlight.y = tax_agreement$transcripts_count.y[tax_agreement$title %in% highlight]
    
    hoverdf = as.data.frame(cbind(tax_agreement$title, tax_agreement[paste0(level, "_MMETSP.x")], tax_agreement$transcripts_count.x, tax_agreement$transcripts_count.y))
    colnames(hoverdf) = c('sample name', "MMETSP annotation", glue('# transcripts for {label.x}'), glue('# of transcripts for {label.y}'))
    
    agreement_plot <- figure(width = 800, title = glue("Number of transcripts with same {level} as MMETSP annotation")) %>%
      ly_points(tax_agreement$transcripts_count.x, tax_agreement$transcripts_count.y,
                hover = hoverdf) %>%
      ly_points(highlight.x, highlight.y, col = 'red') %>%
      ly_abline(0, 1, legend = "Line with slope = 1") %>%
      x_axis(label = paste(colnames(hoverdf)[3])) %>%
      y_axis(label = paste(colnames(hoverdf)[4]))
    
  }
  
  
  return(agreement_plot)
  
}

GF_comparison_naive <- function(config, df){
  print(paste("START creating GF vectors:", format(Sys.time(), "%X")))
  
  mydb = dbConnect(MySQL(), user=config$trapid_db_user, password=config$trapid_db_pswd, dbname=config$trapid_db_name, host=config$trapid_db_server)
  
  # for first one 
  exp_id = df$experiment_id[1]
  out = dbGetQuery(mydb, glue_sql("SELECT plaza_gf_id FROM gene_families WHERE experiment_id = {exp_id}", .con = mydb))
  out[paste(exp_id)] = 1
  
  for (i in seq(2, nrow(df))){
    exp_id = df$experiment_id[i]
    rs = dbGetQuery(mydb, glue_sql("SELECT plaza_gf_id FROM gene_families WHERE experiment_id = {exp_id}", .con = mydb))
    rs[paste(exp_id)] = 1
    out = merge(out, rs, all = TRUE)
  }
  
  dbDisconnect(mydb)
  out[is.na(out)] = 0
  
  print(paste("STOP creating GF vectors:", format(Sys.time(), "%X")))
  
  return(data.frame(out))
  
}

do_all_after_select <- function(config, df, user_id){
  # copy df
  out = df
  
  # rank on NCBI taxonomy
  out = rank_on_taxonomy(out)
  
  # Count transcripts 
  out = transcripts_count(config, out)
  
  # Count transcripts in GF
  out = transcripts_in_GF_count(config, out)
  
  # normalized GF counts
  out["GF_inclusion_ratio"] = out$transcripts_in_GF_count/out$transcripts_count_total
  
  return(out)
  
}

add_toptax <- function(df, tax_df){
  tax_attrib = tax_df %>% group_by(title) %>% filter(!is.na(tax_annot)) %>% filter(transcripts_percent == max(transcripts_percent))
  df['toptax'] = tax_attrib$tax_annot
  df['toptax_transcripts_count'] = tax_attrib$transcripts_count
  df['toptax_transcripts_percent'] = tax_attrib$transcripts_percent
  
  return(df)
}

get_coreGF_score <- function(df, txid = 2759, sp=0.9, ts="ncbi", th=5) {
  # The core GF analysis should have been run beforehand and should have been uploaded to the TRAPID database you are trying to get it from
  # Run a completeness_...sh script form Project_TRAPID/Scripts/completeness/ with correct arguments/parameters
  
  exp_ids = df$experiment_id
  used_method = paste(glue("sp={sp};ts={ts};th={th}"))
  mydb = dbConnect(MySQL(), user=config$trapid_db_user, password=config$trapid_db_pswd, dbname=config$trapid_db_name, host=config$trapid_db_server)
  SQLquery = glue_sql("SELECT experiment_id, completeness_score from completeness_results 
                      WHERE experiment_id IN ({exp_ids*}) 
                      AND clade_txid = {txid} 
                      AND used_method = {used_method}
                      AND id = MAX(id);", .con = mydb)
  
  SQLquery = glue_sql("SELECT a.experiment_id, a.completeness_score, a.used_method
                      FROM completeness_results a 
                      INNER JOIN(
                      SELECT used_method, MAX(id) id from completeness_results 
                      WHERE experiment_id IN ({exp_ids*}) AND clade_txid = {txid} 
                      AND used_method = {used_method} GROUP BY experiment_id
                      ) b ON a.id = b.id AND a.used_method = b.used_method;", .con = mydb)
  
  
  rs = dbGetQuery(mydb, SQLquery)
  dbDisconnect(mydb)
  out = merge_exp(df, rs)
  return(out)
}



