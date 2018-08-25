library('RMySQL')
library('rjson')
library('glue')


# Read configuration data to connect to DB
config <- fromJSON(file="/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/config.json")

# Create DB connection
mydb = dbConnect(MySQL(), user=config$username, password=config$pswd, dbname=config$db, host=config$urlDB)

# rs = dbSendQuery(mydb, "select * from experiments where user_id = 10")

########## FUNCTIONS ##########

get_user_ID <- function(mydb, name){
  SQLquery = glue("SELECT user_id from authentication where email LIKE '{name}%'")
  rs = dbGetQuery(mydb, SQLquery)
  #print(usrid)
  return(rs)
}

select_exp <- function(mydb, user_id, desc_query){
  SQLquery = glue("SELECT experiment_id, title from experiments where user_id = {user_id} AND description LIKE '%{desc_query}%'")
  rs = dbGetQuery(mydb, SQLquery)
  return(rs)
}

transcript_count <- function(mydb, exp_ids){
  SQLquery = glue_sql("SELECT experiment_id, COUNT(experiment_id) FROM transcripts WHERE experiment_id IN ({exp_ids*}) GROUP BY experiment_id", .con = mydb)
  rs = dbGetQuery(mydb, SQLquery)
  return(rs)
}
  
usr_id = get_user_ID(mydb, config$username)
exps_zen = select_exp(mydb, usr_id, "zenodo")
exps_mic = select_exp(mydb, usr_id, "imicrobe")

tr = transcript_count(mydb, as.vector(exps_zen$experiment_id))




