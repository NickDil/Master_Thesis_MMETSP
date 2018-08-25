import pandas as pd
import numpy as np
import glob
import json
import subprocess
import os
import argparse
from FLAME_clustering import *
import argparse
import pandas as pd
import pymysql
import json


def get_param():
    '''
    Function that parses command line input of parameters needed to execute the plot_QC.py script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(description='enrichment analysis')

    # Arguments to pass to R script
    # parser.add_argument('cluster_set', type=str, help="input clustering")
    # parser.add_argument('enricher_location', type=str, help="Path to dreec_enricher")
    parser.add_argument('-data_main', "-d", type=str, help="Experiment data selection to use (_main.csv file).")
    parser.add_argument('-enricher_loc', "-e", type=str, help="Path to dreec enricher")

    # parser.add_argument('meta_data_type', type=str, help='Should be column of mmetsp_sample_attr table in db_trapid_mmetsp_metadata')

    args = parser.parse_args()
    out_dict = vars(args)
    return out_dict

def enrichment_analysis():
    """Execute dries enricher"""

    ""

def write_metadata_file(parameters):

    data_main = pd.read_table(parameters["data_main"], sep=",", encoding='latin-1')

    pd.options.mode.chained_assignment = None #supress warnings

    #Generate feature set to pass to enricher
    FLAMEdir = parameters["outdir"] + "/FLAME_output_d{}_knn{}_axis{}".format(parameters['d'], parameters['knn'], "".join(parameters['axis']))
    ftr_file = "{}/{}_metadata.txt".format(FLAMEdir, parameters['metadata_type'])

    f = open(ftr_file, "w+")
    for i, title in enumerate(data_main["title"]):
        metadata = data_main[parameters['metadata_type']].iloc[i]
        f.write("{metadata}\t{S}\n".format(metadata=metadata, S=title))
    f.close()
    print("[INFO] metadata file written to {}".format(FLAMEdir))

def main():
    # read parameters
    parameters = get_param()

    write_metadata_file(parameters)






if __name__ == '__main__':
    main()