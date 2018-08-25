import subprocess
from annot_parse import parse_annot


def parse_iMicrobe_copylist(fname):

    """
    DON'T USE THIS

    :param fname: space separated list retrieved from copy pasting  ftp://ftp.imicrobe.us/projects/104/files
    :return: dict with different experiments, their assembled transcriptome and md5sum download link

    CAREFULL these links may not exist = use other url_list_imicrobe
    """

    url_d = dict()
    with open(fname) as f:
        for line in f:
            spl = line.split(".")
            experiment = spl[1].split('/')[-1]
            url_d[experiment] = ["ftp://ftp.imicrobe.us/projects/104{s}.nt.fa.gz".format(s=spl[1])]
    return url_d

def parse_iMicrobe_FTP_scrape(fname):

    """
    Transforms text file to dictionary

    :param fname: space separated list retrieved from running the iMicrobe_FTP_sample_url_scrape.py script
        here 'url_list_iMicrobe_final.txt'
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


    # Create dictionary of urls
    url_d = parse_iMicrobe_FTP_scrape("Data/url_list_iMicrobe_final.txt")

    # Load in annotation dict with function of annot_parse.py
    annot_d = parse_annot("Data/annot_retrieve.txt")


    # i = 0     #debugg
    for exp in url_d:

        url = url_d[exp][0]
        desc = annot_d[exp]
        shell_cmd = "python3 Create_experiment.py -E config_experiment.json -D config_connect_trapid.json -t {exp} -du \"{url}\" " \
                    "-d \"{exp} {desc} original assembly from iMicrobe - Pico_overlap\"".format(exp=exp, url=url, desc=desc)
        subprocess.call(shell_cmd, shell=True)
        #
        # if i > 1: #debugg
        #     break
        # i += 1


if __name__ == '__main__':

    main()