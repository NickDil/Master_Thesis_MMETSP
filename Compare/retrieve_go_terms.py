"""
A (very) quick script to retrieve GO terms to use for Nicks's signature detection pipeline.
It makes use of temporary files in case one wants to examine how certain GO terms were retained.
Output: print a table of GO terms, the number of associated OGs given used criteria, and their description.
"""

# Usage example: python3 retrieve_go_terms.py -u <username> -f 0.5 -min 2 -max 1000 <og_list.txt> > <output.tsv>

import argparse
import getpass
import os
import pymysql
import requests
import sys
import time

TIMESTAMP = time.strftime('%Y_%m_%d_%H%M%S')

def parse_arguments():
    """Parse command-line arguments. """
    cmd_parser = argparse.ArgumentParser(description="""Retrieve GO terms """, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    cmd_parser.add_argument('-u', '--username', type=str, dest='username', help='Username to connect to the database server', default='frbuc')
    cmd_parser.add_argument('-s', '--mysql_server', type=str, dest='mysql_server', help='Host name (server)', default='psbsql01.psb.ugent.be')
    cmd_parser.add_argument('-db', '--db_name', type=str, dest='db_name', help='Name of database to retrieve data from', default='db_trapid_ref_eggnog_test')
    cmd_parser.add_argument('-m', '--min_occ', type=int, dest='min_occ', default=5, help='A GO term must be found in at least `min_occ` OGs from `og_list` to be reported. If zero, no `min_occ` threshold')
    cmd_parser.add_argument('-M', '--max_occ', type=int, dest='max_occ', default=1000, help='A GO term must be found in at most `max_occ` OGs from `og_list` to be reported. If zero, no `max_occ` threshold')
    cmd_parser.add_argument('-f', '--freq', type=float, dest='go_freq', default=0.5, help="Retrieved GO terms must be represented in at least `go_freq` of the members of OGs")
    cmd_parser.add_argument('--keep_tmp', dest='keep_tmp', default=False, action='store_true', help="If this flag is provided, temporary files will be kept")
    cmd_parser.add_argument('og_list',type=str, help='A file containing a list of OGs (suitable: all root OGs or all OGs found in the MMETSP samples)')
    cmd_args = cmd_parser.parse_args()
    return cmd_args


def db_connect(username, host, db_name):
    """
    Connect to database. If password not provided as environment variables (DB_PWD), get it from user input.
    Return a database connection.
    """
    if os.environ.get('DB_PWD') is not None:
        db_pwd = os.environ.get('DB_PWD')
    else:
        sys.stderr.write('['+time.strftime("%H:%M:%S")+'] Password not provided as environment variable (set $DB_PWD to avoid typing it each time). \n')
        # Prompt password and try to connect
        db_pwd = getpass.getpass(prompt='Password for user '+username+'@'+host+'?')
    try:
        db_conn = pymysql.connect(host=host,
            user=username,
            passwd=db_pwd,
            database=db_name)
    except:
        sys.stderr.write("[Error] Impossible to connect to the database. Check host/username/password (see error message below)\n")
        raise
    return db_conn


def get_gf_functional_data(og_list_file, go_freq, db_info):
    """
    Fetch GO data from `gf_functional_data` table for OGs included in `og_list_file`, with minimum frequency `go_freq`.
    Return name of file containing the data dump.
    """
    if go_freq < 0 or go_freq > 1:
        sys.stderr.write("[Error] Invalid GO frequency: must be between 0 and 1.\n")
        sys.exit(1)
    sys.stderr.write("[Message] Retrieve GO terms from `gf_functional_data` for selected OGs...\n")
    query_str = "SELECT * FROM `gf_functional_data` WHERE `gf_id` = '{og}' AND `type`='go' AND `freq` >= {go_freq};"
    og_list_name = os.path.splitext(os.path.basename(og_list_file))[0]
    # tmp_file = "gf_fd_dump.freq_" + str(go_freq) +  "." + og_list_name + "." + TIMESTAMP + ".txt"
    tmp_file = "gf_fd_dump."  + TIMESTAMP + ".txt"
    # Fetch data for each OG... Not the most efficient but should be OK with small lists
    db = db_connect(*db_info)
    cursor = db.cursor()
    with open(og_list_file, 'r') as in_file:
        for line in in_file:
            # print(query_str.format(og=line.strip(), go_freq=go_freq))  # Print query (debug)
            cursor.execute(query_str.format(og=line.strip(), go_freq=go_freq))
            results = cursor.fetchall()
            if results:
                to_write = "\n".join(["\t".join([str(a) for a in row][1:-1]) for row in results]) + "\n"
                with open(tmp_file, "a") as out_file:
                    out_file.write(to_write)
    db.close()
    return tmp_file


def count_and_filter_og_by_go(gf_func_data, min_occ=0, max_occ=0):
    """
    From `gf_func_data` (a `gf_functional_data` dump), count the number of OG associated to each GO term.
    Create a file with this information and return its name.
    """
    if min_occ < 0 or max_occ < 0 or max_occ < min_occ:
        sys.stderr.write("[Error] Invalid `min_occ` or `max_occ` values. Must be >=0, max_occ >= min_occ. \n")
        sys.exit(1)
    sys.stderr.write("[Message] Count OGs associated to each GO term...\n")
    tmp_file = "og_by_go." + TIMESTAMP + ".txt"
    go_og_dict = {}
    go_count_dict = {}
    to_filter = set()
    with open(gf_func_data, 'r') as in_file:
        for line in in_file:
            splitted = line.strip().split()
            if splitted[1] in go_og_dict:
                go_og_dict[splitted[1]].add(splitted[0])
            else:
                go_og_dict[splitted[1]] = set([splitted[0]])
    for go in go_og_dict:
        go_count_dict[go] = len(go_og_dict[go])
    # Filter GO terms
    sys.stderr.write("[Message] Filter GO terms based on min/max occurrence thresholds... \n")
    for go in go_count_dict:
        if min_occ != 0:
            if go_count_dict[go] < min_occ:
                to_filter.add(go)
        if max_occ != 0:
            if go_count_dict[go] > max_occ:
                    to_filter.add(go)
    [go_count_dict.pop(x, 'n/a') for x in to_filter]
    # Create output tmp file
    with open(tmp_file, "a") as out_file:
        # First off, write GOs that were filtered out
        out_file.write("# Removed GOs: " + ", ".join(list(sorted(to_filter))) + "\n")
        # Write count for all remaining GOs
        for go in sorted(go_count_dict):
            out_file.write("\t".join([go, str(go_count_dict[go])]) + "\n")
    return tmp_file


def create_final_output(og_by_go):
    """
    Create final output: GO identifer (formatted), OG count, description.
    """
    sys.stderr.write("[Message] Create final output...\n")
    quickgo_url = "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{go_terms}"
    go_data = {}
    # Retreive data from `og_by_go` tmp file
    with open(og_by_go, "r") as in_file:
        next(in_file)  # Skip line listing removed GOs
        for line in in_file:
            splitted = line.strip().split()
            go_data[splitted[0]] = {"formatted_id":splitted[0].replace(":", "_"), "desc": "None", "count": splitted[1]}
    # Get GO description from QuickGO's API, 100 by 100
    sys.stderr.write("[Message] Fetch GO descriptions from QuickGO... \n")
    all_go_terms = sorted(go_data)
    for i in range(0, len(all_go_terms), 100):
        go_str = ",".join(all_go_terms[i:i+100])
        r = requests.get(quickgo_url.format(go_terms=go_str), headers={"Accept" : "application/json"})
        if not r.ok:
            r.raise_for_status()
            sys.exit(1)
        response_body = r.json()
        # print(response_body["results"])  # Check retrieved data (debug)
        for go in response_body["results"]:
            if go["id"] in go_data:
                go_data[go["id"]]["desc"] = go["name"]
            else:
                sys.stderr.write("[Warning] '%s' not found in data: we probably have an obsolete GO term or a secondary ID! \n" % go["id"])
        time.sleep(1)
    # Create final output
    for go in sorted(go_data):
        print("\t".join([go_data[go]["formatted_id"], go_data[go]["count"], go_data[go]["desc"]]))


def del_files(files):
    """Delete the files given as parameters (a list of tmp files). """
    sys.stderr.write("Remove temporary files...")
    for file in files:
        os.remove(file)


if __name__ == '__main__':
    args = parse_arguments()
    db_info = [args.username, args.mysql_server, args.db_name]
    gf_func_data = get_gf_functional_data(og_list_file=args.og_list, go_freq=args.go_freq, db_info=db_info)
    og_by_go = count_and_filter_og_by_go(gf_func_data, args.min_occ, args.max_occ)
    create_final_output(og_by_go)
    if not args.keep_tmp:
        del_files([gf_func_data, og_by_go])
