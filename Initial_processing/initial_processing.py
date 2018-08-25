import pymysql
import os
import subprocess
import argparse
import json
import sys
import configparser
from time import gmtime, strftime


"""
Script to do the initial processing of a transcript collection from the trapid DB
Inp

"""

def get_param():
    '''
    Function that parses command line input of parameters needed to execute the initial_processing.py script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(description='Perform initial processing of an experiment in the TRAPID database.')

    # PLAZA/Reference database parameters
    parser.add_argument('-reference_db_server', '-ps', type=str, help='Server name where reference DB is located')
    parser.add_argument('-reference_db_pswd', '-ppw', type=str, help='Password to connect to database')
    parser.add_argument('-reference_db_name', '-pn', type=str, help='Name of reference DB')
    parser.add_argument('-reference_db_user', '-pu', type=str, help='username to connect to reference DB')
    parser.add_argument('-reference_db_port', '-pp', type=int, help='Portname to reference DB server')

    # TRAPID database parameters
    parser.add_argument('-trapid_db_server', '-ts', type=str, help='Server name where TRAPID DB is located')
    parser.add_argument('-trapid_db_pswd', '-tpw', type=str, help='Password to connect to TRAPID database')
    parser.add_argument('-trapid_db_name', '-tn', type=str, help='Name of the TRAPID DB')
    parser.add_argument('-trapid_db_user', '-tu', type=str, help='username to connect to the TRAPID DB')
    parser.add_argument('-trapid_db_port', '-tp', type=int, help='Portname to TRAPID server')

    # storage parameter
    parser.add_argument('-temp_dir', '-td', type=str, help='Path to the experiments directory')

    # experiment settings
    parser.add_argument('-exp_ID', '-id', type=str, help='ID of experiment to be processed as in TRAPID DB')
    parser.add_argument('-blast_location', '-bl', type=str, help='Path to directory where databases are located')
    parser.add_argument('-blast_database', '-bd', type=str, help='blast_database, e.g. for a DIAMOND database the .dmnd file')
    parser.add_argument('-gf_type', '-gf', type=str, help='gf_type eg. HOM')
    parser.add_argument('-num_top_hits', '-nt', type=str, help='num_top_hits eg. 1')
    parser.add_argument('-evalue', '-ev', type=str, help='evalue eg. -5')
    parser.add_argument('-func_annot', '-fa', type=str, help='Functional annotation eg. gf')

    # location of executables
    parser.add_argument('-base_script_location', '-sl', type=str, help='base_script_location (path)')

    # Taxonomic scope (EggNOG)
    parser.add_argument('-tax_scope', '-txs', type=str, help="Taxonomic scope (should be 'None', unless we work with EggNOG data)")

    # Taxonomic binning
    parser.add_argument('-tax_binning', '-tx', type=str, help="Tax. binning user choice ('true' = perform it, 'false' = don't perform it)")
    parser.add_argument('-kaiju_parameters', '-kp', type=str, help='A string of Kaiju parameters (appended when calling `kaiju`)')
    parser.add_argument('-taxdmp_location', '-txd', type=str, help='Path to location of nodes.dmp and names.dmp of NCBI taxomomy database ')
    parser.add_argument('-splitted_db_location', '-kdb', type=str, help='Path to a directory containing kaiju (splitted) DB files')
    parser.add_argument('-kt_import_text_location', '-kt', type=str, help='Path to location `importText.pl` script from KronaTools')

    # ncRNA annotation (NOT USED AS OF NOW, but in development within TRAPID)
    parser.add_argument('-rfam_dir', '-rd', type=str, help='Path to TRAPID\'s RFAM directory. ')
    parser.add_argument('-rfam_clans', '-rc', type=str, help='A comma-separated list of RFAM clans to use with Infernal')


    parser.add_argument('--CONFIG', '-C',
                        help='Optional argument that reads in all parameters from a config_initial_processing.json file. '
                             '\nCAUTION: parameters specified in this file are overridden by parameters directely specified as arguments, should a conflict occur',
                        type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument("--verbose", '-v', help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    out_dict = vars(args)

    #### IF CONFIG.JSON FILES ARE GIVEN, read the parameters in the respective containers, if not specified by arguments already

    if args.CONFIG:

        with args.CONFIG as json_data_file:
            config_data = json.load(json_data_file)

        out_dict = merge_none(out_dict, config_data)

        args.CONFIG.close()

        if args.verbose:
            print('Database connection configuration file used:', args.CONFIG, '\n')


    ### verbose let know what value was assigned to every parameter
    if args.verbose:
        print('All parameters and their values; \n\n', out_dict, "\n")

    ### Raise error if None value in parameters

    for key in [key for key in out_dict if key != 'verbose']:
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


# NOTE: perhaps redundant with the json config / command-line arguments (although it is probably good to keep these
# scripts and TRAPID as independent as possible).
def create_initial_processing_ini(exp_id, parameters):
    """
    Function that creates configuration (`.ini` file) for the initial processing of experiment `exp_id`, using values
    provided in `parameters`.

    :return:
    Name of the configuration file, so it can be used as parameter for the initial processing script.
    """
    config = configparser.ConfigParser(interpolation=None)
    ini_file = os.path.join(parameters["temp_dir"], exp_id, 'initial_processing_%s.ini' % exp_id)
    # Add sections used in TRAPID's iniital processing configuration file
    conf_sections = ["trapid_db", "reference_db", "experiment", "initial_processing", "sim_search", "tax_binning", "infernal"]
    for section in conf_sections:
        config.add_section(section)

    # Add values for each section, from `parameters`
    # TRAPID database
    config["trapid_db"]["trapid_db_server"] = parameters["trapid_db_server"]
    config["trapid_db"]["trapid_db_name"] = parameters["trapid_db_name"]
    config["trapid_db"]["trapid_db_port"] = str(parameters["trapid_db_port"])
    config["trapid_db"]["trapid_db_username"] = parameters["trapid_db_user"]
    config["trapid_db"]["trapid_db_password"] = parameters["trapid_db_pswd"]
    # Reference database
    config["reference_db"]["reference_db_server"] = parameters["reference_db_server"]
    config["reference_db"]["reference_db_name"] = parameters["reference_db_name"]
    config["reference_db"]["reference_db_port"] = str(parameters["reference_db_port"])
    config["reference_db"]["reference_db_username"] = parameters["reference_db_user"]
    config["reference_db"]["reference_db_password"] = parameters["reference_db_pswd"]
    # Experiment
    config["experiment"]["exp_id"] = exp_id
    config["experiment"]["tmp_exp_dir"] = os.path.join(parameters["temp_dir"], exp_id, '')
    # Initial processing
    config["initial_processing"]["base_script_dir"] = parameters["base_script_location"]
    config["initial_processing"]["gf_type"] = parameters["gf_type"]
    config["initial_processing"]["num_top_hits"] = parameters["num_top_hits"]
    config["initial_processing"]["func_annot"] = parameters["func_annot"]
    config["initial_processing"]["tax_scope"] = parameters["tax_scope"]
    # Similarity search (DIAMOND)
    config["sim_search"]["blast_db_dir"] = parameters["blast_location"]
    config["sim_search"]["blast_db"] =  parameters["blast_database"].replace(".dmnd", "")  # Without `.dmnd` extension
    config["sim_search"]["e_value"] = parameters["evalue"]
    # Taxonomic binning
    config["tax_binning"]["perform_tax_binning"] = parameters["tax_binning"]
    config["tax_binning"]["kaiju_parameters"] = parameters["kaiju_parameters"]
    config["tax_binning"]["names_dmp_file"] = os.path.join(parameters["taxdmp_location"], "names.dmp")
    config["tax_binning"]["nodes_dmp_file"] = os.path.join(parameters["taxdmp_location"], "nodes.dmp")
    config["tax_binning"]["splitted_db_dir"] = parameters["splitted_db_location"]
    config["tax_binning"]["kt_import_text_path"] = parameters["kt_import_text_location"]
    # Rfam / Infernal
    # NOTE: Infernal is not used as in this project, but we still use the config values to stay consistent with the
    # latest TRAPID scripts
    config["infernal"]["rfam_dir"] = parameters["rfam_dir"]
    config["infernal"]["rfam_clans"] = parameters["rfam_clans"]

    # Write configration to `ini_file`
    with open(ini_file, "w") as conf_file:
        config.write(conf_file)

    # Print message to STDERR if verbose flag was provided.
    if "verbose" in parameters and parameters["verbose"]:
        sys.stderr.write("[Message] Created configuration file for experiment %s: '%s'. \n" % (exp_id, ini_file))

    return ini_file


def create_initial_processing_sh(exp_id, parameters, ini_file):
    """
    Function creates and runs a shell script in directory (initial_processing.sh) to upload the data from the url
    to the TRAPID DB.

    :return:
    path to shell script so it can be executed with subprocess.Popen()
    """

    # create  shell script for initial processing
    temp_dir = "{path}{exp}/".format(path=parameters['temp_dir'], exp=str(exp_id))

    shell_script_name = temp_dir + "initial_processing_{x}.sh".format(x=exp_id)

    header = """#!/usr/bin/env bash

date
#Loading necessary modules
module load perl
module load java
module load framedp
module load python/x86_64/2.7.2
module load gcc
module load kaiju
module load diamond

# Java parameters...
export _JAVA_OPTIONS="-Xmx8g"

#Launching perl script for initial processing, with necessary parameters

"""

    perl_cmd = "perl {base_script_location}perl/initial_processing.pl {ini_file}\ndate\n".format(
        base_script_location=parameters['base_script_location'],
        ini_file=ini_file
    )

    taxdmp_location = parameters["taxdmp_location"]

    kaiju_report_cmd = """
#species
kaijuReport -t {taxdmp_location}nodes.dmp -n {taxdmp_location}names.dmp -i {temp_dir}kaiju/kaiju_merged.out -r species -o {temp_dir}kaiju/kaiju.out.species.{exp_id}.summary
#genus
kaijuReport -t {taxdmp_location}nodes.dmp -n {taxdmp_location}names.dmp -i {temp_dir}kaiju/kaiju_merged.out -r genus -o {temp_dir}kaiju/kaiju.out.genus.{exp_id}.summary
#phylum
kaijuReport -t {taxdmp_location}nodes.dmp -n {taxdmp_location}names.dmp -i {temp_dir}kaiju/kaiju_merged.out -r phylum -o {temp_dir}kaiju/kaiju.out.phylum.{exp_id}.summary
""".format(taxdmp_location=taxdmp_location, temp_dir=temp_dir, exp_id=str(exp_id))

    # print(perl_cmd)  # Debug

    with open(shell_script_name, 'w') as out_file:
        out_file.write(header)

        out_file.write(perl_cmd)

        out_file.write(kaiju_report_cmd)

    out_file.close()
    os.chmod(shell_script_name, 0o777)

    print("{s} created on {time}\n".format(s=shell_script_name, time=strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    return shell_script_name

def connect_picoplaza(parameters):
    """
    Adapted version of code from Thomas Depuyt (/home/nidil/Documents/Project_TRAPID/Scripts/MySQL_test.py)
    just opens connection to TRAPID DB, does not create cursor,
    need connection to work with pandas pd.read_sql()

    configuration parameters from config_initial_processing.json
    """
    # read config_data
    username = parameters['reference_db_user']
    pswd = parameters['reference_db_pswd']
    db = parameters['reference_db_name']
    url = parameters['reference_db_server']
    portname = parameters['reference_db_port']

    # connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx

def connect_trapid(parameters):
    """
    Adapted version of code from Thomas Depuyt (/home/nidil/Documents/Project_TRAPID/Scripts/MySQL_test.py)
    just opens connection to TRAPID DB, does not create cursor,
    need connection to work with pandas pd.read_sql()

    configuration parameters from config_initial_processing.json
    """
    #read config_data
    username = parameters['trapid_db_user']
    pswd = parameters['trapid_db_pswd']
    db = parameters['trapid_db_name']
    url = parameters['trapid_db_server']
    portname = parameters['trapid_db_port']

    #connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx

def shortname_finder(DB_con_trapid, DB_con_pico, exp_id):

    """
    finds the shortname of the genus of the experiment as is implemented in TRAPID
    :param exp_id:
    :return: corresponding shortname if it exists
    """
    cursor = DB_con_trapid.cursor()

    # Get description from TRAPID DB
    sql = "SELECT description FROM experiments WHERE experiment_id = %s"
    cursor.execute(sql, (exp_id))
    desc = cursor.fetchall()[0][0]

    # Parse description to get genus and species variables
    sgfetch = desc.split()[1]
    sgl = sgfetch.split('_')[:2]
    sg = " ".join(sgl)
    g = sgl[0]


    # Select the common names from the pico plaza DB
    cursor2 = DB_con_pico.cursor()

    sql2 = "SELECT common_name FROM annot_sources"
    cursor2.execute(sql2)
    fetchl = cursor2.fetchall()

    gslist = []
    genuslist = []
    specieslist = []

    for e in fetchl:
        gslist += [e[0]]
        genuslist += [e[0].split()[0]]
        specieslist += [e[0].split()[1]]

    # initiate lists to do search

    if sg in gslist:
        refsp = sg
    elif g in genuslist:
        refspi = genuslist.index(g)
        refsp = gslist[refspi]
    else:
        refsp = "Eukaryotes"

    # print(refsp) # Debugg

    if refsp != "Eukaryotes":
        sql3 = "SELECT species FROM annot_sources WHERE common_name = %s"
        cursor2.execute(sql3, (refsp))
        out = cursor2.fetchall()[0][0]
    else:
        out = "Eukaryotes"

    DB_con_pico.close()
    DB_con_trapid.close()

    return out

def update_TRAPID_DB_IP(DB_con_trapid ,exp_id, blast_database):
    SQL_query = "UPDATE experiments SET used_blast_database = \'{blast_database}\' where experiment_id = {exp_id}".format(exp_id=exp_id, blast_database=blast_database)
    cursor = DB_con_trapid.cursor()
    cursor.execute(SQL_query)
    DB_con_trapid.commit()
    DB_con_trapid.close()


def main():


    # Get parameters for new experiment from command line input (argparse)

    parameters = get_param()

    # retrieve experiment ID
    exp_id = parameters['exp_ID']

    print("START:", strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    # connect to the two databases, needed to find shortname of species for rapsearch ref location
    # DB_con_trapid = connect_trapid('/home/nidil/Documents/Project_TRAPID/Scripts/config_initial_processing.json')
    # DB_con_pico = connect_picoplaza('/home/nidil/Documents/Project_TRAPID/Scripts/config_initial_processing.json')

    # find shortname of species in exp ID
    # name = shortname_finder(DB_con_trapid, DB_con_pico, exp_id)

    # IF you always want to search against all Eukryotes database
    # blast_directory = "Eukaryotes.dmd"


    # Better user specified reference database
    blast_database = parameters["blast_database"]

    # Create correct shell script in corresponding temporary folder that calls the initial_processing.pl script with
    # according parameters, ASSUMES DIR IS ALREADY MADE = DB_upload script

    ini_file_name = create_initial_processing_ini(exp_id, parameters)
    shell_script_name = create_initial_processing_sh(exp_id, parameters, ini_file_name)

    # print(shell_script_name)

    # Call the shell script (start upload to DB) and create output and error file
    # first correct names
    path, ipname = shell_script_name.rsplit('/', maxsplit=1)[:2]
    n = ipname.split(".")[0]

    # # Call shell script and write.out and .err files:
    with open("{p}/{n}.out".format(p=path, n=n), "w+") as outfile, open("{p}/{n}.err".format(p=path, n=n), "w+") as errfile:
        subprocess.call(shell_script_name, stdout=outfile, stderr=errfile)

    # Create taxonomic binning reports

    # update TRAPID DB experiments table with blast_database
    DB_con_trapid = connect_trapid(parameters)

    update_TRAPID_DB_IP(DB_con_trapid, exp_id, blast_database)

    print("END:", strftime("%Y-%m-%d %H:%M:%S", gmtime()))

if __name__ == '__main__':
    main()
