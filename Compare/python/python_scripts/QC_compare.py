import pymysql
import pandas as pd
import json
import numpy as np
from matplotlib import pyplot as plt
import argparse
"""
split Zenodo vs IMic 
- calculate basic statistics for every experiment
"""


def get_param():
    '''
    Function that parses command line input of parameters needed to execute the Create_experiment.py script.

    :return:
    Dictionary with input parameters
    '''
    parser = argparse.ArgumentParser(description='Create and upload an experiment in the TRAPID database.')
    parser.add_argument('-username', '-un', type=str, help='Username to connect to database')
    parser.add_argument('-pswd', '-pw', type=str, help='Password to connect to database')
    parser.add_argument('-urlDB', '-dbu', type=str, help='Url of server where database is located')
    parser.add_argument('-db', type=str, help='Name of database to connect to')
    parser.add_argument('-portname', '-p', type=int, help='Portname to server')
    parser.add_argument('-userID', '-ui', type=str, help='The user_id of an existing user of the TRAPID webtool')
    parser.add_argument('-refdb', '-rdb', type=str, help='Reference database used for processing of transcripts')
    parser.add_argument('-title', '-t', type=str, help='Title of experiment')
    parser.add_argument('-description', '-d', type=str, help='Description for the experiment ')
    parser.add_argument('-urldata', '-du', type=str, help='url to dataset to be downloaded')
    parser.add_argument('-clean_id', '-cid', type=int, default=0)
    parser.add_argument('-perform_tax_binning', '-tax', type=str, default="1")


    parser.add_argument('--DBCONFIG', '-D',
                        help='Optional argument that reads in all parameters for DB connection from config_connect_trapid.json file. '
                             '\nCAUTION: parameters specified in this file are overridden by parameters directely specified as arguments, should a conflict occur',
                        type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument('--EXPCONFIG', '-E',
                        help='Optional argument that reads in all parameters for experiment creation from config_connect_trapid.json file.'
                             '\nCAUTION: parameters specified in this file are overridden by parameters directely specified as arguments, should a conflict occur',
                        type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument("--verbose", '-v', help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    out_dict = vars(args)

    #### IF CONFIG.JSON FILES ARE GIVEN, read the parameters in the respective containers, if not specified by arguments already

    if args.DBCONFIG:

        with args.DBCONFIG as json_data_file:
            config_data = json.load(json_data_file)

        out_dict = merge_none(out_dict, config_data)

        args.DBCONFIG.close()

        if args.verbose:
            print('Database connection configuration file used:', args.DBCONFIG, '\n')

    if args.EXPCONFIG:

        with args.EXPCONFIG as json_data_file:
            config_data_TRAPID = json.load(json_data_file)

        out_dict = merge_none(out_dict, config_data_TRAPID)

        args.EXPCONFIG.close()

        if args.verbose:
            print('Experiment creation configuration file used:', args.EXPCONFIG, "\n")

    ### verbose let know what value was assigned to every parameter
    if args.verbose:
        print('All parameters and their values; \n\n', out_dict, "\n")

    ### Raise error if None value in parameters
    error_if = ["username", "urlDB", "pswd", "db", "portname", "userID", "refdb", "urldata", "title", 'description']

    for key in error_if:
        if not out_dict[key]:
            raise ValueError(
                '\nThe parameter {p} was assigned the value: {v} \nHINT: run in verbose mode (--verbose) to print parameters and their assigned values'.format(
                    p=key, v=out_dict[key]))

    # return the dict
    return out_dict

def connect_mysql2(config_data):
    """
    just opens connection to TRAPID DB, does not create cursor,
    need connection to work with pandas pd.read_sql()

    configuration parameters from config_connect_trapid.json
        "username":"",
        "urlDB":"",
        "pswd":"",
        "db":"",
        "portname":
    """

    #read config-file
    username = config_data['username']
    pswd = config_data['pswd']
    db = config_data['db']
    url = config_data['urlDB']
    portname = config_data['portname']

    #connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx

def getusrid(name):
    cursor.execute("SELECT user_id from authentication where email LIKE '{name}%'".format(name=name))
    usrid = cursor.fetchall()[0][0]
    #print(usrid)
    return(usrid)

def exp_id_dict(cursor, user_id, query):
    SQLstatement = "SELECT experiment_id, title from experiments where user_id = {user_id} " \
                "AND description LIKE '%{query}%'".format(user_id=user_id, query=query)
    cursor.execute(SQLstatement)
    out = cursor.fetchall()
    return dict(out)

def transcript_count(DB_con, df):
    counttr = "SELECT experiment_id, COUNT(experiment_id) FROM transcripts WHERE experiment_id IN {} GROUP BY experiment_id".format(tuple(df['exp_id']))
    dftr = pd.read_sql(counttr, con=DB_con)
    dftr.columns.values[1] = "#transcripts"
    dd = pd.concat([df, dftr.iloc[:,1]], axis=1)
    return dd

def difference_plot(x, y):
    color = ['red' if f > 0 else 'blue' for f in x - y]
    plt.scatter(range(len(x)), x-y, c=color)
    plt.title("difference in amount of transcripts for every sample")
    plt.xlabel("samples")
    plt.ylabel("#Zenodo - #iMicrobe")
    plt.plot([0,len(x)], [0,0])
    plt.show()

def main():
    # Open configuration data from JSON file
    with open('/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/config_connect_trapid.json') as json_data_file:
        config_data = json.load(json_data_file)

    DB_con = connect_mysql2(config_data)
    cursor = DB_con.cursor()
    user_id = getusrid(config_data['username'])
    expidict_zen = exp_id_dict(cursor, user_id, 'zenodo')
    expidict_mic = exp_id_dict(cursor, user_id, 'imicrobe')

    # Create dataframe for Zenodo and iMicrobe samples
    df_z = pd.DataFrame(list(expidict_zen.items()), columns=["exp_id", "title"])
    df_m = pd.DataFrame(list(expidict_mic.items()), columns=["exp_id", "title"])

    # add total amount of transcripts to them

    df_z = transcript_count(DB_con, df_z)
    df_m = transcript_count(DB_con, df_m)

    x = df_z.sort_values(by=['title'])
    y = df_m.sort_values(by=['title'])

# Test wether you are comparing the same samples
# print(list(x["title"]) == list(y["title"]))

diffs = df_z.iloc[:,2] - df_m.iloc[:,2]
color = ['red' if f > 0 else 'blue' for f in diffs]

print("More transcripts in Zenodo:", color.count("red"))
print("More transcripts in iMicrobe:", color.count("blue"))
#
# plt.scatter(df_z.iloc[:,2], df_m.iloc[:,2], c=color)
# plt.plot([max(df_z.iloc[:,2]), 0], [max(df_z.iloc[:,2]), 0])
# plt.show()

# Histogram of differences
#
# plt.hist(diffs, 20, histtype="step")
# plt.title("Differences distribution")
# plt.xlabel("Zenodo-iMicrobe")
# plt.show()

# # plot a difference plot
# difference_plot(x.iloc[:,2], y.iloc[:,2])
#
# # normal scatter plot
# color = ['red' if f > 0 else 'blue' for f in x.iloc[:,2]- y.iloc[:,2]]
#
# plt.scatter(x.iloc[:,2], y.iloc[:,2], c=color)
# plt.title(" Zenodo versus iMicrobe assembly amount of transcripts")
# plt.xlabel("#Transcripts Zenodo")
# plt.ylabel("#Transcripts iMicrobe")
# plt.show()






# print(expidict_zen)
# print(expidict_mic)
# print(len(expidict_zen))
# print(len(expidict_mic))

#
#
# cursor.execute("SELECT experiment_id from experiments where user_id = %s", user_id)
# expid = cursor.fetchall()
# expids_all = [x[0] for x in expid]
# print("User_id =", user_id, ", Experiment_ids are:", expids_all)
#
#
#
#
# ###SELECT transcripts from experiment with ID 77
#
#
# #for exact timestamp
# cursor.execute("SELECT DATE_FORMAT(NOW(), '%T %d %m %Y')")
# now = cursor.fetchall()
#
#
# now = expid[0][1]
#
#
#
# #Get all transcript data for experiment 77 , it has gf_id column amd a transcript_id colunm which are used in Gene_family_information.py
#
# query = "SELECT *  FROM transcripts where experiment_id=" + str(expid[0][0])
# tr = pd.read_sql(query, con=DB_con)
#
# #add timestamp
# tr['last_edit_date'] = now
#
# #show
# #print("\n#########TR#######\n", tr.head())
#
#
# #Get all transcripts_annotation info for experiment 77
#
# #query = "SELECT *  FROM transcripts_annotation where experiment_id=" + str(expid[0][0])
# #tr_annot = pd.read_sql(query, con=DB_con)
# #print("\n########TRANNOT#######\n", tr_annot.head())
#
#
#
#
# #Get all Gene family info for experiment 77, ..... what I actually DON'T need !
#
# #query = "SELECT *  FROM gene_families where experiment_id=" + str(expid[0][0])
# #GF_data = pd.read_sql(query, con=DB_con)
# #print("\n#####GF_DATA#######\n", GF_data.head())
#
#
#
# #make data_transcripts frame
# data_transcripts = tr
#
#
# #Extend with Gene_family_information.py
#
#
# print('Total amount of transcripts:', data_transcripts['gf_id'].size)
# z = data_transcripts['gf_id'].size  - data_transcripts['gf_id'].dropna().size
#
# print("Time of DB retrieval:", now)
#
# print('Amount of unattributable transcripts:', z, '\nPercentage of unattributable transcripts:', round(z/data_transcripts['gf_id'].size*100, ndigits=3), '%')
#
# #Check column values
# #print(data_transcripts.columns.values)
#
# x = data_transcripts['gf_id'].nunique()
# print('GF count:', x)
#
# y = data_transcripts['gf_id'].dropna().unique()
# print('GF count other way:', len(y))
#
# #find single copy genes
#
# d = data_transcripts['gf_id'].dropna()
# sc = d.drop_duplicates(keep=False)
# print('Amount of Single Copy GF\'s:', len(sc))
#
# #transcripts in GF
#
# print('transcripts in GF:', d.count())
#
# #Highest transcript GF
# counts = d.value_counts()
# print('Top three GF\'s with highest transcript count:\n', counts.head(3))
