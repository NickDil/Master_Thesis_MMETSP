import re

def parse_annot(fname):
    """

    :param fname: file with structure as such:

            Genus_species(SRA)_strain_SRR_MMETSP_alt_Genus_species(imicrobe).Trinity.fasta

    :return: annotation dictionary
    """


    annot_d = dict()
    with open(fname) as f:
        for line in f:
            spl = line.split("_SRR")
            descr = spl[0]
            tit = re.findall(r'MMETSP....', line)[0]
            annot_d[tit] = descr
    f.close()
    return annot_d

def output(annot_d, fname):
    '''
    Writes to output file
    :param annot_d:
    :param fname:
    :return:
    '''
    with open(fname, 'w') as f:
        for tit in annot_d:
            f.write("{tit}\t{desc}\n".format(tit=tit,desc=annot_d[tit]))
    f.close()

def main():
    inname = "Data/annot_retrieve.txt"
    outname = "Data/annot_out.txt"
    annot_d = parse_annot(inname)
    output(annot_d, outname)

if __name__ == "__main__":

    main()