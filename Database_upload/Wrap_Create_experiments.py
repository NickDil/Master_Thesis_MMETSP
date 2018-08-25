from annot_parse import parse_annot
import urllib.request
import re
import argparse



"""
Generates a list of shell commands involving the Create_experiment_cluster.py and annot_parse.py from a list of urls to dataset one wants to upload, 
and paste it in a big shell script to qsub to the cluster.

CAN ONLY BE USED WHEN USING CONFIGURATION FILES!

OUTPUT:

url_list_xxx.sh
"""


def get_param():
    '''
    Function that parses command line input of parameters needed to execute the xxxx_wrap.py scripts. Urllist

    :return:
    Dictionary with path to urllist
    '''
    parser = argparse.ArgumentParser(description='Create and upload multiple experiments from url list in the TRAPID database. \'config_connect_trapid.json\' and \'config_experiment.json\' should exist in helper scripts directory cf. gitlab repo NICK')

    parser.add_argument('urllist', type=str, help='LIST of urls to datasets to be downloaded')
    parser.add_argument('--upload_name', type=str, default="url_list_upload",
                        help='Name for the shell script that will be generated, defaults to: \'url_list_upload.sh\'')

    parser.add_argument('script_loc', type=str, help='path to the helper scripts directory (NICK), '
                                                               '\'config_connect_trapid.json\' and \'config_experiment.json\' should be in that '
                                                     'base directory too')

    args = parser.parse_args()

    out_dict = vars(args)

    return out_dict


def urllist_to_dict(fname):

    """
    Transforms text file to dictionary

    :param fname: (space separated list retrieved from running the iMicrobe_FTP_sample_url_scrape.py script
        here 'url_list_iMicrobe_final.txt') or othr file in same format
    :return: dict with different experiments, their assembled transcriptome and md5sum download link when available

    """
    url_d = dict()
    with open(fname) as f:
        for line in f:
            spl = line.split()
            experiment = spl[0]
            path = spl[1]
            if len(spl) > 2:
                if not (url_d.get(experiment)):
                    url_d[experiment] = [path, spl[2]]
                else:
                    url_d['{experiment}_X'.format(experiment=experiment)] = [path, spl[2]]
            else:
                if not (url_d.get(experiment)):
                    url_d[experiment] = [path, "NA"]
                else:
                    url_d['{experiment}_X'.format(experiment=experiment)] = [path, "NA"]
    return url_d


def main():

    param = get_param()

    # Create dictionary from url list
    url_d = urllist_to_dict(param['urllist'])

    # base script loc
    base_location = param['script_loc']

    # Load in annotation dict with function of annot_parse.py
    annot_d = parse_annot("{base_location}/Data/annot_retrieve.txt".format(base_location=base_location)) # from midas

    name = param['upload_name']
    shellout = open("{name}.sh".format(name=name), 'w')
    shellout.write("module load python/x86_64/3.5.1\n")

    for exp in url_d:
        url = url_d[exp][0]
        md51 = url_d[exp][1]
        if len(md51.split('/')) > 2: #if md5sum is specified by a url
            req = urllib.request.Request(md51)
            response = urllib.request.urlopen(req)
            the_page = response.read()
            p = the_page.split()[0]
            md5 = str(p).split("\'")[1]
        else:
            if md51 != 'NA':
                md5 = md51.split(':')[1]
            else:
                md5 = md51

        desc = "{annot} from {url} with md5sum: {md5}".format(annot=annot_d[exp], url=url, md5=md5)

        clean_id = 0
        if re.search("zenodo", url):
            clean_id = 1


        shell_cmd = "python3 {base_location}/Database_upload/Create_experiment_cluster.py" \
                    " -E {base_location}/config_experiment.json -D {base_location}/config_connect_trapid.json" \
                    " -t {exp} -du \"{url}\" -cid {clean_id} -d \"{exp} {desc}\"".format(base_location=base_location,exp=exp, url=url, desc=desc,
                                                 clean_id=clean_id)

        # subprocess.call(shell_cmd, shell=True)
        shellout.write(shell_cmd + "\n")

if __name__ == '__main__':

    main()