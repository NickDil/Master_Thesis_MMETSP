import pandas as pd
import subprocess
import os
import argparse
from time import gmtime, strftime


def get_param():
    '''
    Function that parses command line input of parameters needed to execute the FLAME_clustering.py script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(description='Run FLAME')

    # args
    parser.add_argument('input_table', type=str, help="Input file (space separated) of sample X feature matrix to be clustered, "
                                             "first line with dimensions should be present")
    parser.add_argument('flame_path', type=str, default=1, help="Path to flame algorithm")

    parser.add_argument('-axis', type=str, default='0', help="Which axis to use as instances, the other axis is used as features. Row:0 (default), col:1. To do both you can pass 01 or 10")

    parser.add_argument('-d', type=str, default="1", help="Distance funcion, check readme in 'flame-clustering/' dir. Defaults to euclidian (d=1)")

    parser.add_argument('-knn', type=str, default="15", help='K nearest neighbours, parameter for FLAME. Default knn=15')

    parser.add_argument('-write',  action='store_true', help="Write clustering results to a file (compatible with dreec enricher")

    parser.add_argument('-outdir', '-o', type=str, help="Specify output directory")

    parser.add_argument('-keep', action='store_true', help="toggle to keep parsed NOG matrix")

    args = parser.parse_args()
    out_dict = vars(args)

    #specific axis parameter handeling
    out_dict["axis"] = list(out_dict["axis"])
    print(out_dict)
    return out_dict

def parse_NOG_vector(parameters):
    # Communicate
    print("[INFO] Creating parsed NOG matrix to feed to the FLAME algorithm ...")

    # Read NOG_matrix
    NOG_matrix_read = pd.read_table(parameters["input_table"], sep=" ")

    tempfiles = []
    # Check axis
    for ax in parameters["axis"]:
        NOG_matrix = NOG_matrix_read
        if ax == '1': #columns
            NOG_matrix = NOG_matrix.T

        #create tempfile
        tempfile = parameters["input_table"]+"_{}.temp".format(ax)
        tempfiles += [tempfile]
        f_temp = open(tempfile, 'w')
        # Write dimesions (FLAME needs that)
        f_temp.write("{} {} {} {}\n".format(NOG_matrix.shape[0], NOG_matrix.shape[1], parameters['d'], parameters['knn']))
        f_temp.close()
        pd.DataFrame.to_csv(NOG_matrix, path_or_buf=tempfile, sep=" ", mode="a", header=False, index=False)
        #os.remove(tempfile)
        print('[INFO] NOG matrix parsed')

    return tempfiles

def update_arguments_line(parameters):
    #OUTDATED!!!!!!!!!!!!!!

    matrix_location = parameters["input_table"]

    # print(matrix_location)

    from_file = open(matrix_location)
    old_line = from_file.readline()
    from_file.close()
    # print(old_line)

    # make any changes to line
    line = " ".join(old_line.split()[0:2]) + " " + parameters['d'] + " " + parameters['knn']
    # print(old_line)

    subprocess.call(['sed', '-i', "1s/.*/{line}/".format(line=line), matrix_location])

    print("\n[INFO] argument line updated:", line, "\n")

def parse_FLAME_output(x):

    C_list = []
    inline = False
    newclust = [0]
    for rline in x.split("\n"):
        oline = rline.strip("\t ,\n").replace(',', '').split()

        if inline:
            oline = [int(x) for x in oline]
            newclust = newclust + oline
        if not oline:
            inline = False
        elif oline[0] == "Cluster":
            inline = True
            C_list.append(newclust)
            newclust = []
    C_list.pop(0)
    C_list.append(newclust)

    return C_list

def write_FLAME_output_old(cluster_list, arguments, ax):


    data_main = pd.read_table(arguments["data_main"], sep=",", encoding='latin-1')

    pd.options.mode.chained_assignment = None #supress warnings

    # Write data
    # make new directory
    FLAMEdir = arguments["outdir"] + "/FLAME_output_d{}_knn{}_axis{}".format(arguments['d'], arguments['knn'], "".join(arguments['axis']))
    os.makedirs(FLAMEdir, exist_ok=True)

    for i, cluster in enumerate(cluster_list):
        colname = "cluster_{}".format(i)
        data_main[colname] = 0
        data_main[colname].iloc[cluster] = 1

    # get metadata and write to file
    annotfile = "{}/annotated_clusters_FLAME_output_d{}_knn{}.txt".format(FLAMEdir, arguments['d'], arguments['knn'])

    f = open(annotfile, 'w+')
    cluster_annot_list = []
    for i in range(len(cluster_list)):
        colname = "cluster_{}".format(i)
        cluster_annot = list(data_main[data_main[colname] == 1][arguments["metadata"]])
        cluster_annot_list.append(cluster_annot)
        f.write("\n----------[CLUSTER {}]----------\n".format(i))
        f.write(str(cluster_annot))
    f.write("\n--------------------------------\n")
    # print(cluster_phyla_list)
    f.close()

    #Generate gene_set and feature set to pass to enricher
    gene_set_file = "{}/gene_set_FLAME_output_d{}_knn{}.txt".format(FLAMEdir, arguments['d'], arguments['knn'])
    ftr_file = "{}/feature_set_FLAME_output_d{}_knn{}.txt".format(FLAMEdir, arguments['d'], arguments['knn'])

    f = open(gene_set_file, "w+")
    for i in range(len(cluster_list)):
        for id in cluster_list[i]:
            exp_id = data_main["experiment_id"].iloc[id]
            f.write("Cluster_{i}\t{S}\n".format(i=i, S=exp_id))
    f.close()

    # print(sorted(list(itertools.chain(*cluster_list))))
    # print(data_main["experiment_id"][list(itertools.chain(*cluster_list))])
    f = open(ftr_file, "w+")
    for i, exp_id in enumerate(data_main["experiment_id"]):
        phylum = data_main[arguments["metadata_type"]].iloc[i]
        f.write("{phylum}\t{S}\n".format(phylum=phylum, S=exp_id))
    f.close()
    print("[INFO] Files written to {}:\n* Phylum clusters:\t{}\n"
          "* Gene_set:\t{}\n"
          "* Feature_set:\t{}".format(FLAMEdir, annotfile.split("/")[-1], gene_set_file.split("/")[-1], ftr_file.split("/")[-1]))

def write_FLAME_output(cluster_list, parameters, ax):

    pd.options.mode.chained_assignment = None  # supress warnings

    # Write data
    # make new directory
    FLAMEdir = parameters["outdir"] + "/FLAME_output_d{}_knn{}_axis{}".format(parameters['d'], parameters['knn'], "".join(parameters['axis']))
    os.makedirs(FLAMEdir, exist_ok=True)

    NOG_matrix_read = pd.read_table(parameters["input_table"], sep=" ")
    if ax == "1":
        instances = NOG_matrix_read.columns
    else:
        instances = NOG_matrix_read.index

    df = pd.DataFrame({"instances": instances})

    for i, cluster in enumerate(cluster_list):
        colname = "cluster_{}".format(i)
        df[colname] = 0
        df[colname].iloc[cluster] = 1

    # Generate gene_set and feature set to pass to enricher
    out_file = "{}/FLAME_output_d{}_knn{}_axis{}.txt".format(FLAMEdir, parameters['d'], parameters['knn'], ax)

    f = open(out_file, "w+")
    for i in range(len(cluster_list)):
        for id in cluster_list[i]:
            exp_id = df["instances"].iloc[id]
            f.write("Cluster_{i}\t{S}\n".format(i=i, S=exp_id))
    f.close()

    print("[INFO] FLAME output written to {}".format(FLAMEdir))

def FLAME(FLAME_location, matrix_location, verbose):
    # Communicate
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\t[START] FLAME clustering of {}".format(matrix_location))
    print("[INFO] Running FLAME ...")

    cmd = [FLAME_location, matrix_location]

    try:
        x = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as xc:
        if verbose:
            print("error code", xc.returncode, xc.output)

    FLAME_clusters = parse_FLAME_output(x)

    #check for outlier nodes (last element of output list)
    if not FLAME_clusters[-1] and verbose:
        print("Non-empty outlier group!")

    #remove zero clusters
    out = [x for x in FLAME_clusters if x]
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\t[STOP] FLAME clustering of {}".format(matrix_location))
    return out

def main(parameters):

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\t[START] FLAME clustering based on axis {} with parameters; distfunc = {}, knn = {}".format(' and '.join(parameters['axis']), parameters['d'], parameters["knn"]))
    FLAME_location = parameters["flame_path"]
    matrix_location = parameters["input_table"]


    # Create file that is readable by FLAME algorithm, ie remove column and rownames and store in temp file
    tempfiles = parse_NOG_vector(parameters)


    ## DONT NEED THIS ANYMORE< IS INCLUDED IN parse_NOG_vector()
    # Update the arguments passed to the FLAME algorithm, eg modify first line of input file
    # update_arguments_line(parameters)


    # Run FLAME
    for ax,tempfile in zip(parameters["axis"],tempfiles):
        out = FLAME(FLAME_location, tempfile, False)

        if parameters["write"]:
            if parameters["outdir"] is None: #create new folder in NOG_vector folder
                parameters["outdir"] = "."
            write_FLAME_output(out, parameters, ax)
            # print("[STOP] Files written to {}\n".format(parameters["write"]))
        else:
            print(out)

    #remove temporary file
    if not parameters["keep"]:
        for tempfile in tempfiles:
            os.remove(tempfile)
            print("[INFO] {} removed".format(tempfile))

if __name__ == '__main__':
    parameters = get_param()
    main(parameters)