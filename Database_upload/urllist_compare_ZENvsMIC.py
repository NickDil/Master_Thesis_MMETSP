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

def parse_iMicrobe_FTP_scrape(fname):

    """

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


d_zen = parse_zenodo("Data/url_list_zenodo.txt")
d_mic = parse_iMicrobe_FTP_scrape("Data/url_list_iMicrobe_final.txt")

print("Zenodo: ", len(d_zen), "\n")
print("iMicrobe: ", len(d_mic), "\n")


intersect = d_zen.keys() & d_mic.keys()

print("Amount of urls to same samples (Intersection): ", len(intersect))


x = d_zen.keys() - intersect
print("the", abs(len(d_zen) - len(intersect)), "missing samples in Zenodo: \n", x)
y = d_mic.keys() - intersect
print("the", abs(len(d_mic) - len(intersect)), "missing samples in iMicrobe: \n", y)



