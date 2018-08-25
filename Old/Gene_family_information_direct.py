import pymysql
import pandas as pd
import json

#Open configuration data from JSON file
with open('Data/config_connect_trapid.json') as json_data_file:
    config_data = json.load(json_data_file)

def connect_mysql2():
    """
    Adapted version of code from Thomas Depuyt (/home/nidil/Documents/Project_TRAPID/Scripts/MySQL_test.py)
    just opens connection to TRAPID DB, does not create cursor,
    need connection to work with pandas pd.read_sql()

    configuration parameters from config_connect_trapid.json
    """
    #read INI-file
    username = config_data['username']
    pswd = config_data['pswd']
    db = config_data['db']
    url = config_data['url']
    portname = config_data['portname']
    #connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx


DB_con = connect_mysql2()

cursor = DB_con.cursor()


cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
#print(tables)


#Show columns of transcript table

cursor.execute("SHOW COLUMNS FROM transcripts")
#print(cursor.fetchall())


#find experiment name for email adress nick.dillen@ugent.be
    #First need user_id

cursor.execute("SELECT user_id from authentication where email LIKE 'nidil%' ")
usrid = cursor.fetchall()
#print(usrid)

cursor.execute("SELECT experiment_id, last_edit_date from experiments where user_id = %s", usrid)
expid = cursor.fetchall()
print("User_id =", usrid[0][0], ", Experiment_ids are:", [x[0] for x in expid], "and last_edit_date:", [x[1] for x in expid]) #experiment 77 belongs to user_id 10 (nick)




###SELECT transcripts from experiment with ID 77


#for exact timestamp
cursor.execute("SELECT DATE_FORMAT(NOW(), '%T %d %m %Y')")
now = cursor.fetchall()


now = expid[0][1]



#Get all transcript data for experiment 77 , it has gf_id column amd a transcript_id colunm which are used in Gene_family_information.py

query = "SELECT *  FROM transcripts where experiment_id=" + str(expid[0][0])
tr = pd.read_sql(query, con=DB_con)

#add timestamp
tr['last_edit_date'] = now

#show
#print("\n#########TR#######\n", tr.head())


#Get all transcripts_annotation info for experiment 77

#query = "SELECT *  FROM transcripts_annotation where experiment_id=" + str(expid[0][0])
#tr_annot = pd.read_sql(query, con=DB_con)
#print("\n########TRANNOT#######\n", tr_annot.head())




#Get all Gene family info for experiment 77, ..... what I actually DON'T need !

#query = "SELECT *  FROM gene_families where experiment_id=" + str(expid[0][0])
#GF_data = pd.read_sql(query, con=DB_con)
#print("\n#####GF_DATA#######\n", GF_data.head())



#make data_transcripts frame
data_transcripts = tr


#Extend with Gene_family_information.py


print('Total amount of transcripts:', data_transcripts['gf_id'].size)
z = data_transcripts['gf_id'].size  - data_transcripts['gf_id'].dropna().size

print("Time of DB retrieval:", now)

print('Amount of unattributable transcripts:', z, '\nPercentage of unattributable transcripts:', round(z/data_transcripts['gf_id'].size*100, ndigits=3), '%')

#Check column values
#print(data_transcripts.columns.values)

x = data_transcripts['gf_id'].nunique()
print('GF count:', x)

y = data_transcripts['gf_id'].dropna().unique()
print('GF count other way:', len(y))

#find single copy genes

d = data_transcripts['gf_id'].dropna()
sc = d.drop_duplicates(keep=False)
print('Amount of Single Copy GF\'s:', len(sc))

#transcripts in GF

print('transcripts in GF:', d.count())

#Highest transcript GF
counts = d.value_counts()
print('Top three GF\'s with highest transcript count:\n', counts.head(3))
