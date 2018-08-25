from annot_parse import parse_annot
import pandas as pd
from Wrap_Create_experiments import urllist_to_dict

mic_d = urllist_to_dict("Data/url_list_iMicrobe_final.txt")
zen_d = urllist_to_dict("Data/url_list_zenodo_final.txt")
annot_d = parse_annot("Data/annot_retrieve.txt")

list = []
specieslist = []
with open("Data/pico_sp.txt") as fh:
    for line in fh:
        line = line.strip()
        lline = line.split()
        list.append(lline[0])
        specieslist.append("{g} {s}".format(g=lline[0], s=lline[1]))

out_sp = []
out_ge = []

for exp in annot_d:
    genus = annot_d[exp].split('_')[0]
    species = "{g} {s}".format(g=annot_d[exp].split('_')[0], s=annot_d[exp].split('_')[1])
    if genus in list:

        if exp in mic_d:
            out_mic[genus] = out_mic.get(genus, []) + [exp]
        if exp in zen_d:
            out_zen[genus] = out_zen.get(genus, []) + [exp]

    if species in specieslist:
        out_species[species] = out_species.get(species, []) + [exp]
        out_species_count[species] = out_species_count.get(species, 0) + 1

print("Dictionary of all genus that are also in pico-plaza: \n", out_MMETSP)

print('\nAll counts per genus:\n', pd.Series(out_count))

print("\nAll samples in both assemblies?\n",  (pd.Series(out_mic) == pd.Series(out_zen)))

print("\nAll sample counts per species:\n", pd.Series(out_species_count))