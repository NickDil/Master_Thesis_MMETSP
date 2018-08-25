require('RMySQL')
require('rjson')
config <- fromJSON(file="/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/config.json")

mydb = dbConnect(MySQL(), user=config$username, password=config$pswd, dbname=config$db, host=config$urlDB)
dbListTables(mydb)

dbListFields(mydb, 'experiments')

rs = dbSendQuery(mydb, "select * from experiments where user_id = 10")
my_experiments = fetch(rs)
View(my_experiments)


phylum = c("chlorophyta", "bld")
genus = c("Thalassiosira")
species = NULL

data1 = exps_mic[1,]
data1['url'] = url
data2 = exps_zen[1,]
url = "http://bioinformatics.psb.ugent.be/testix/trapid_frbuc/trapid/experiment/9851"
p <- figure(width = 800, title = "Reads with species annotation for different assemblies (original (NCGR) vs. DIB-lab)") %>%
  ly_points(data1$reads_count_total, data2$reads_count_total, url = as.vector(url)) %>%
  ly_abline(0, 1, legend = "Line with slope = 1") %>%
  x_axis(label = '# transcripts DIB-lab') %>%
  y_axis(label = "# transcripts NCGR")

p


expids = exps_zen$experiment_id

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

colnames(out) = c('reads_percent', 'reads_count', 'tax_annot', "experiment_id")
out$reads_percent = out$reads_percent/100
out$tax_annot = as.character(out$tax_annot)
out = merge_exp(df, out)
return(out)



