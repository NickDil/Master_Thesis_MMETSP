from annot_parse import parse_annot
import pandas as pd
from Wrap_Create_experiments import urllist_to_dict
import pymysql
import json

def connect_picoplaza(confile):
    """
    Adapted version of code from Thomas Depuyt (/home/nidil/Documents/Project_TRAPID/Scripts/MySQL_test.py)
    just opens connection to TRAPID DB, does not create cursor,
    need connection to work with pandas pd.read_sql()

    configuration parameters from config_connect_trapid.json
    """
    with open(confile) as json_data_file:
        config_data = json.load(json_data_file)

    #read config_data
    username = config_data['username']
    pswd = config_data['pswd']
    db = "db_trapid_ref_plaza_pico_02_test"
    url = config_data['urlDB']
    portname = config_data['portname']


    json_data_file.close()

    #connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx

mic_d = urllist_to_dict("/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/Data/url_list_iMicrobe_final.txt")
zen_d = urllist_to_dict("/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/Data/url_list_zenodo_final.txt")
annot_d = parse_annot("/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/Data/annot_retrieve.txt")



DB_con_pico = connect_picoplaza("/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/config_connect_trapid.json")
cursor2 = DB_con_pico.cursor()

sql2 = "SELECT common_name FROM annot_sources"
cursor2.execute(sql2)
fetchl = cursor2.fetchall()

genuslist = []
specieslist = []

gslist = []

for e in fetchl:
    gslist += [e[0]]
    genuslist += [e[0].split()[0]]
    specieslist += [e[0].split()[1]]


out_MMETSP = {}
out_count = {}
out_mic = {}
out_zen = {}

out_species = {}
out_species_count = {}

out_sp_mic = []
out_ge_mic = []

out_sp_zen = []
out_ge_zen = []

for exp in annot_d:
    genus = annot_d[exp].split('_')[0]
    species = "{g} {s}".format(g=annot_d[exp].split('_')[0], s=annot_d[exp].split('_')[1])
    if genus in genuslist:
        out_count[genus] = out_count.get(genus, 0) + 1
        out_MMETSP[genus] = out_MMETSP.get(genus, []) + [exp]
        if exp in mic_d:
            out_mic[genus] = out_mic.get(genus, []) + [exp]
            out_ge_mic += [exp]
        if exp in zen_d:
            out_zen[genus] = out_zen.get(genus, []) + [exp]
            out_ge_zen += [exp]
    if species in specieslist:
        out_species[species] = out_species.get(species, []) + [exp]
        out_species_count[species] = out_species_count.get(species, 0) + 1
        if exp in mic_d:
            out_sp_mic += [exp]
        if exp in zen_d:
            out_sp_zen += [exp]


print("Genus in pico plaza:", genuslist, "\n")

print("List of all genus that are also in pico-plaza: \n", out_MMETSP.keys(), "\n")

print("Dictionary of all genus that are also in pico-plaza: \n", out_MMETSP, "\n")


print("Amount of samples:", len(out_ge_zen))

print('\nAll counts per genus:\n', pd.Series(out_count))

print("\nAll samples in both assemblies?\n",  (pd.Series(out_mic) == pd.Series(out_zen)))

print("\nAll sample counts per species:\n", pd.Series(out_species_count))

### WRITE URLLISTS

fileGM = "Data/url_list_pico_genus_mic.txt"
fileSM = "Data/url_list_pico_species_mic.txt"
fileGZ = "Data/url_list_pico_genus_zen.txt"
fileSZ = "Data/url_list_pico_species_zen.txt"

# with open(fileGZ, 'w') as fd:
#     for exp in out_ge_zen:
#         tit = exp
#         url = zen_d[exp][0]
#         md5 = zen_d[exp][1]
#         fd.write("{tit}\t{url}\t{md5}\n".format(tit=tit, url=url, md5=md5))
#     fd.close()
#
# with open(fileSZ, 'w') as fd:
#     for exp in out_sp_zen:
#         tit = exp
#         url = zen_d[exp][0]
#         md5 = zen_d[exp][1]
#         fd.write("{tit}\t{url}\t{md5}\n".format(tit=tit, url=url, md5=md5))
#     fd.close()
#
#
# with open(fileSM, 'w') as fd:
#     for exp in out_sp_mic:
#         tit = exp
#         url = mic_d[exp][0]
#         md5 = mic_d[exp][1]
#         fd.write("{tit}\t{url}\t{md5}\n".format(tit=tit, url=url, md5=md5))
#     fd.close()
#
# with open(fileGM, 'w') as fd:
#     for exp in out_ge_mic:
#         tit = exp
#         url = mic_d[exp][0]
#         md5 = mic_d[exp][1]
#         fd.write("{tit}\t{url}\t{md5}\n".format(tit=tit, url=url, md5=md5))
#     fd.close()
