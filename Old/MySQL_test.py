import pymysql
import pandas as pd
import json
with open('/home/nidil/Drives/nidil/doc/Documents/Project_TRAPID/config_connect_trapid.json') as json_data_file:
    config_data = json.load(json_data_file)
def connect_mysql2():
    """
    qdqpted code from ThomasDP>Klaas Vdpoele

    Create cursor connected to Trapid DB

    """
    #read INI-file
    username = config_data['username']
    pswd = config_data['pswd']
    db = config_data['db']
    url = config_data['url']
    portname = config_data['portname']
    #connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    cur = cnx.cursor()
    return cur


cursor = connect_mysql2()

# Get all table names in db

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(tables)

#NOW
cursor.execute("SELECT NOW(); SELECT USER();")
now = cursor.fetchone()
usr = cursor.fetchone()
print(now)
print(usr)

#Get ID's of people who created last 10 experiments
query = ("SELECT user_id FROM experiments ORDER BY creation_date DESC LIMIT 10 ")
cursor.execute(query)
ids = cursor.fetchall()
idss = pd.Series(ids).unique()

for x in idss:
    query = ("SELECT email from authentication where user_id = %s")
    cursor.execute(query, x)
    print(x, cursor.fetchall())
