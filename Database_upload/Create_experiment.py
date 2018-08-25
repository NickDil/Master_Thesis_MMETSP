import pymysql
import time
import os
import subprocess
import argparse
import json
from time import gmtime, strftime

"""
This script creates, for one experiment, as specified by input parameters, entries in the TRAPID DB and uploads files
from a given url to the database. 
"""

def connect_mysql2(parameters):
    """
    Adapted version of code from Thomas Depuyt (/home/nidil/Documents/Project_TRAPID/Scripts/MySQL_test.py)
    just opens connection to TRAPID DB, does not create cursor,
    need connection to work with pandas pd.read_sql()

    configuration parameters from config_connect_trapid.json
    """
    #read config_data
    username = parameters['username']
    pswd = parameters['pswd']
    db = parameters['db']
    url = parameters['urlDB']
    portname = parameters['portname']
    #connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx

def create_exp_db(DB_con, parameters):

    """
    Function creates new database entry for an experiment with parameters as specified in a config file amd returns the
    experiment ID.
    Includes: new row in experiments table and new row in data_uploads table

    :return:
    exp_id
    """

    # Read TRAPID and experiment related config data
    user_id = parameters["userID"]
    ref_db = parameters["refdb"]
    title = parameters["title"]
    description = parameters["description"]
    url = parameters["urldata"]


    #create cursor

    cursor = DB_con.cursor()

    # Create new database entry for experiment

    sql = "INSERT INTO experiments (user_id, title, description, creation_date, last_edit_date, used_plaza_database ) VALUES (%s, %s, %s, %s, %s, %s)"

    print('write to experiments')
    cursor.execute(sql, (user_id, title, description, time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'), ref_db))
    exp_id = cursor.lastrowid
    DB_con.commit()
    print("wrote in experiments, new experiment with ID =", exp_id)

    # Create new database entry for data_uploads

    sql = "INSERT INTO data_uploads (user_id, experiment_id, type, name) VALUES (%s, %s, %s, %s)"

    print('write to data_uploads')
    cursor.execute(sql, (user_id, exp_id, "url", url))
    DB_con.commit()
    print("wrote in data-uploads")

    return exp_id

def create_DB_upload(exp_id):

    """
    Function creates a directory and shell script in that directory (database_upload.sh) to upload the data from the url
    to the TRAPID DB.

    :return:
    path to shell script so it can be executed with subprocess.Popen()
    """

    # make directory to upload data in for experiment ... + chmod
    path = "/www/bioapp/trapid_frbuc/experiment_data/"
    if not os.path.exists(path+str(exp_id)):
        os.makedirs(path+str(exp_id))
        os.chmod(path+str(exp_id), 0o777)
        os.makedirs(os.path.join(path+str(exp_id), "upload_files"))
        os.chmod(os.path.join(path + str(exp_id), "upload_files"), 0o777)

    print("Directory created:", path + str(exp_id))

    # create  shell script for database upload
    shell_script_name = "/www/bioapp/trapid_frbuc/experiment_data/" + str(exp_id) + '/' + 'database_upload.sh'
    header = "#!/usr/bin/env bash\n#Loading necessary modules\n"
    perl_cmd = "perl /home/nidil/Documents/trapid_develop/app/scripts/perl/database_upload.pl psbsql01 db_trapid_02 3306 trapid_website @Z%28ZwABf5pZ3jMUz /www/bioapp/trapid_frbuc/experiment_data/{exp_id}/upload_files/ {exp_id} /www/group/biocomp/extra/bioinformatics_prod/testix/trapid_frbuc/app/scripts/\ndate\n".format(exp_id=str(exp_id))
    # print(perl_cmd)  # Debug
    with open(shell_script_name, 'w') as out_file:
        out_file.write(header)
        out_file.write("module load perl\nhostname\ndate\n#Launching perl script for database upload, with necessary parameters\n")
        out_file.write(perl_cmd)

    os.chmod(shell_script_name, 0o777)
    return shell_script_name


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

def merge_none(a, b):

    for k in b:
        if not a[k]:
            a[k] = b[k]
    return a


def main():

    # Get parameters for new experiment from command line input (argparse)

    parameters = get_param()

    print("START:", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    # Connect to DB

    db_con = connect_mysql2(parameters)

    # Create entries in the DB for this new experiment

    experiment = create_exp_db(db_con, parameters)

    # Create a directory and shell script in that directory (database_upload.sh) to upload the data from the url
    # to the TRAPID DB. Recover the path to the shell script.

    shell_script_name = create_DB_upload(experiment)

    # Call the shell script (start upload to DB) and create output and error file
    path = shell_script_name.rsplit('/', maxsplit= 1)[0]
    with open(path + "/upload.out", "w+") as outfile, open(path + "/upload.err", "w+") as errfile:
        subprocess.call(shell_script_name, stdout=outfile, stderr=errfile)
    print("END:", strftime("%Y-%m-%d %H:%M:%S", gmtime()))

if __name__ == "__main__":

    main()

