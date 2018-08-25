import subprocess
import argparse
from time import gmtime, strftime

def get_param():
    '''
    Function that parses command line input of parameters needed to execute the plot_QC.py script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(description='enrichment analysis')

    # Arguments to pass to R script
    parser.add_argument('infile', type=str, help="input like _main.csv")
    parser.add_argument('project_script_location', type=str, help="project_script_location (Absolute path) "
                                                                                        "e.g. '/path/to/Project_trapid/Scripts/'")
    parser.add_argument('-GO', type=str, default="None", help='GO term to select NOGs')
    parser.add_argument('-min_occurence', '-mo', default=1, type=str, help='minimun occurence in experiments for NOG to be included. Default 1; include all.')
    parser.add_argument('-outdir', '-o', type=str, default="./", help="output directory")
    parser.add_argument('-counts',  action='store_true', help="switch on to use the transcript counts instead of just using GF presence (binary)")
    parser.add_argument('-normalize', "-n", action='store_true', help="switch on to normalize GF feature martix (recommended for counts)")


    args = parser.parse_args()
    out_dict = vars(args)
    print(out_dict)
    return out_dict

def NOG_vector_R(args):
    """Calls R script to generate NOG vectors"""

    command = 'Rscript'
    path2script = args['project_script_location'] + 'Compare/R/R_scripts/create_NOG_matrix.R'

    # Variable number of args in a list, make all strings
    # L = list(map(str, list(args.values()))) #UNORDERED

    infile = args['infile']
    dir_base = args['project_script_location']
    GO_term = ":".join(args['GO'].split('_'))
    min_occurence = str(args['min_occurence'])
    dir_out = args['outdir']
    COUNT = str(args['counts'])
    data_normalize = str(args['normalize'])

    L = [infile, dir_base, GO_term, min_occurence, dir_out, COUNT, data_normalize]
    # Build subprocess command
    cmd = [command, path2script] + L

    # check_output will run the command and store to result
    # print(cmd)
    try:
        x = subprocess.check_output(cmd, universal_newlines=True)
        # print(x)
    except subprocess.CalledProcessError as xc:
        print("error code", xc.returncode, xc.output)
    return x

def main(arguments):

    print("\n", strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\t[START] Creating NOG feature matrix\n")
    print("[INFO] Creating NOG vectors (this may take a wile) ...\n")
    # Run feature vector creator if no such file is passed
    dim = NOG_vector_R(arguments)
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\t[STOP] Creating NOG feature matrix:\t", strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\n")
    print("[INFO] NOG-feature matrix has shape:", dim.split()[-1])

if __name__ == '__main__':
    arguments = get_param()
    main(arguments)
