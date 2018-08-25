"""
Reformat `sample-attr.tab` file to create TSV file that can be imported in the metadata DB using `mysqlimport`
"""

# Usage: python2.7 reformat_mmetsp_metadata.py sample-attr.tab > mmetsp_sample_attr.tsv

import sys


def min_checks():
    """Check `sys.argv` length. """
    if len(sys.argv) < 2:
        sys.stderr.write("[Error] Invalid arguments. Usage: `python reformat_mmetsp_metadata.py sample-attr.tab > output_file.tsv`\n")
        sys.exit(1)


def get_attributes(sample_tab_file):
    """Get all the possible attributes to look for and return them as set. """
    possible_attributes = set()
    with open(sample_tab_file, 'r') as in_file:
        next(in_file)
        for line in in_file:
            possible_attributes.add(line.strip().split('\t')[2])
    return possible_attributes


def parse_metadata(sample_tab_file):
    """Parse `sample-attr.tab` file and print correctly formatted table, ready to be imported. """
    attributes = get_attributes(sample_tab_file)
    attributes.add("sample_name")
    attributes = list(attributes)
    sample_dict = dict()
    with open(sample_tab_file, 'r') as in_file:
        next(in_file)
        for line in in_file:
            splitted = line.strip().split('\t')
            if splitted[0] not in sample_dict:
                sample_dict[splitted[0]] = {k:"\N" for k in attributes}
                sample_dict[splitted[0]]["sample_name"] = splitted[1]
            if splitted[2] != "country":
                sample_dict[splitted[0]][splitted[2]] = splitted[3]
            # Keep only country code (for some samples, both the country code & full name are indicated)
            else:
                if sample_dict[splitted[0]]["country"] == "\\N":
                    sample_dict[splitted[0]][splitted[2]] = splitted[3]
                else:
                    if len(splitted[3]) < len(sample_dict[splitted[0]][splitted[2]]):
                        sample_dict[splitted[0]][splitted[2]] = splitted[3]
    # Now print the table we want
    print "sample_id\t" + '\t'.join(sorted(attributes))
    sample_line = "{sample_id}\t{all_attributes}"
    for sample in sorted(sample_dict.keys()):
        attr_str = '\t'.join([sample_dict[sample][att] for att in sorted(sample_dict[sample])])
        print sample_line.format(sample_id=sample, all_attributes=attr_str)


if __name__ == "__main__":
    min_checks()
    parse_metadata(sys.argv[1])
