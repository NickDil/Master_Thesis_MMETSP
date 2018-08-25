import subprocess
from annot_parse import parse_annot
import argparse
import json

def get_param():
    '''
    Function that parses command line input of parameters needed to execute the xxxx_wrap.py scripts. Urllist

    :return:
    Dictionary with path to urllist
    '''
    parser = argparse.ArgumentParser(description='Create and upload multiple experiments from url list in the TRAPID database.')

    parser.add_argument('urllist', type=str, help='LIST of urls to datasets to be downloaded')

    args = parser.parse_args()

    out_dict = vars(args)

    # return the dict
    return out_dict



def parse_zenodo(fname):

    """

    :param fname: space separated list retrieved from copy pasting https://zenodo.org/record/251828
    :return: dict with different experiments and their fabricated download link and md5sum
    """

    url_d = dict()
    with open(fname) as f:
        for line in f:
            spl = line.split()
            experiment = spl[0].split(".")[0]
            if not(url_d.get(experiment)):
                url_d[experiment] = ["https://zenodo.org/record/251828/files/{s}".format(s=spl[0]), spl[1]]
            else:
                url_d['{experiment}_X'.format(experiment=experiment)] = ["https://zenodo.org/record/251828/files/{s}".format(s=spl[0]), spl[1]]
    return url_d



def main():

    param = get_param()

    # Create dictionary from url list
    url_d = parse_zenodo(param['urllist'])

    # Load in annotation dict with function of annot_parse.py
    annot_d = parse_annot("Data/annot_retrieve.txt")

    print(url_d)
    # for exp in url_d:
    #
    #     url = url_d[exp][0]
    #     desc = annot_d[exp]
    #     shell_cmd = "python3 Create_experiment.py -E config_experiment.json -D config_connect_trapid.json -t {exp} -du \"{url}\" " \
    #                 "-d \"{exp} {desc} re-assembly from ZENODO - Pico_overlap\"".format(exp=exp, url=url, desc=desc)
    #     subprocess.call(shell_cmd, shell=True)
    #
    #     # break debugg


if __name__ == '__main__':

    main()