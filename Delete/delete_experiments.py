import pymysql
import os
import argparse
import json
from time import gmtime, strftime
import sys


def get_param():
    '''
    Function that parses command line input of parameters needed to execute the delete_experiments.py script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(
        description='Deletes experiments from the TRAPID database and a directory (tmpdir).')

    parser.add_argument('first_expID', type=int, help='Experiment id of the first experiment to delete')
    parser.add_argument('last_expID', type=int, help='Experiment id of the first experiment to delete')
    parser.add_argument('tmpdir', type=str, help='temp dir to be cleaned location (path)')
    parser.add_argument('config', type=str, help='path to config file to read for acces TRAPID DB')

    args = parser.parse_args()
    out_dict = vars(args)

    # return the dict
    return out_dict


def clear_db_content(exp_id1, exp_id2, db_connection):
    """Cleanup exepriment's taxonomic binning results, stored in the `transcript_tax` table. """
    msg = "[Message] Cleanup `transcripts_tax` for" \
          " experiments '{exp_id1}\' to \'{exp_id2}\'; \n".format(exp_id1=str(exp_id1), exp_id2=str(exp_id2))
    sys.stderr.write(msg)
    cursor = db_connection.cursor()
    delete_query_tax = "DELETE FROM transcripts_tax WHERE experiment_id BETWEEN \'{exp_id1}\' and \'{exp_id2}\';"
    cursor.execute(delete_query_tax.format(exp_id1=str(exp_id1), exp_id2=str(exp_id2)))

    msg = "[Message] Cleanup `experiments` for" \
          " experiments '{exp_id1}\' to \'{exp_id2}\'; \n".format(exp_id1=str(exp_id1), exp_id2=str(exp_id2))
    sys.stderr.write(msg)
    delete_query_exp = "DELETE FROM `db_trapid_02`.`experiments` WHERE `experiments`.`experiment_id` BETWEEN \'{exp_id1}\' and \'{exp_id2}\';"
    cursor.execute(delete_query_exp.format(exp_id1=str(exp_id1), exp_id2=str(exp_id2)))

    msg = "[Message] Cleanup rest (similarities, completeness_results for" \
          " experiments '{exp_id1}\' to \'{exp_id2}\'; \n".format(exp_id1=str(exp_id1), exp_id2=str(exp_id2))
    sys.stderr.write(msg)
    delete_query_exp = "DELETE FROM similarities WHERE experiment_id BETWEEN \'{exp_id1}\' and \'{exp_id2}\';" \
                       " DELETE FROM completeness_results WHERE experiment_id BETWEEN \'{exp_id1}\' and \'{exp_id2}\' "
    cursor.execute(delete_query_exp.format(exp_id1=str(exp_id1), exp_id2=str(exp_id2)))

    db_connection.commit()
    cursor.close()


def connect_trapid(confile):
    """
    Adapted version of code from Thomas Depuyt (/home/nidil/Documents/Project_TRAPID/Scripts/MySQL_test.py)
    just opens connection to TRAPID DB, does not create cursor,
    need connection to work with pandas pd.read_sql()

    configuration parameters from config_connect_trapid.json
    """
    with open(confile) as json_data_file:
        config_data = json.load(json_data_file)

    # read config_data
    username = config_data['trapid_db_user']
    pswd = config_data['trapid_db_pswd']
    db = config_data['trapid_db_name']
    url = config_data['trapid_db_server']
    portname = config_data['trapid_db_port']

    json_data_file.close()

    # connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx


def main():

    parameters = get_param()
    print("START:", strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    # connect to the database
    DB_con_trapid = connect_trapid(parameters['config'])

    exp_id1 = parameters['first_expID']
    exp_id2 = parameters['last_expID']
    tmpdir = parameters['tmpdir']
    # clean up experiments
    print("Cleaning up database\n")
    clear_db_content(exp_id1, exp_id2, db_connection=DB_con_trapid)

    # clean /group/transreg/nidil/experiment_data/
    print("Cleaning {tmpdir}\n".format(tmpdir=tmpdir))
    x = "{exp_id1}..{exp_id2}".format(exp_id1=str(exp_id1), exp_id2=str(exp_id2))
    shell_cmd = "rm -rf {tmpdir}{{{x}}}".format(x=x, tmpdir=tmpdir)
    os.system(shell_cmd)


if __name__ == '__main__':
    main()