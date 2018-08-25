import os
import re
import pandas as pd
import argparse
import copy
from scipy import stats

def get_param():
    '''
    Function that parses command line input of parameters needed to execute this script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(description='Create heatmap, optionally clustered from flame output')

    # args
    parser.add_argument('scan_dir', type=str, help="Path to dir that has to be scanned.")
    parser.add_argument('-outdir', '-o', type=str, default="./", help="Specify output directory, defaults to working dir.")
    parser.add_argument('-collect_signal', "-s", action='store_true', help="Toggle to extract 'signal' that defined the 'good cluster'. This takes more time")

    parser.add_argument('-set_consistence', "-sc", type=float, default=0.8, help="Cutoff value for set consistence (= n_hits/set_size). Default 0.8")
    parser.add_argument('-ftr_consistence', "-fc", type=float, default=0.0, help="Cutoff value for ftr consistence (= n_hits/ftr_size). Default 0 (include all")
    parser.add_argument('-min_clusters', "-m", type=int, default=1, help="Minimum amount of 'good clusters' in an enrichment output to for the selection to be included in the results. Default 0 (include all)")

    # Collect signal specific
    parser.add_argument('-pval_filter', "-pf", type=float, default=0.05, help="signal = neutral/none if p-value higher than '-pval_filter'. Default = 0.05 (set to 1 if you do not want the t test)")
    parser.add_argument('-FC_modifier', "-Fm", type=float, default=1, help="signal = positive/negative if fold change (FC) is higher/lower than 'FC_modifier'/ (1/'FC_modifier'). Default = 1")

    args = parser.parse_args()
    out_dict = vars(args)

    return out_dict


def collect_data(parameters):
    out = pd.DataFrame()
    #walk through input dir
    for root, dirs, files in os.walk(parameters['scan_dir']):
        for x in files:
            if x.startswith("enricher_output"):

                path = os.path.join(root, x)
                m = re.search('GO_(\d*)',x)
                GO_term = m.group()

                enrichment_table = pd.read_table(path, skiprows=6)

                enrichment_table["ftr_consistence"] = enrichment_table["n_hits"] / enrichment_table["ftr_size"]
                enrichment_table["set_consistence"] = enrichment_table["n_hits"] / enrichment_table["set_size"]
                enrichment_table["GO_TERM"] = ":".join(GO_term.split("_"))

                # Filter(s)

                enrichment_table = enrichment_table[enrichment_table["set_consistence"] >= parameters["set_consistence"]]
                enrichment_table = enrichment_table[enrichment_table["ftr_consistence"] >= parameters["ftr_consistence"]]


                if len(enrichment_table) >= parameters["min_clusters"]:
                    if parameters["collect_signal"]:
                        enrichment_table = collect_signal(enrichment_table, parameters, root)

                    out = out.append(enrichment_table, ignore_index=True)

    return out

def collect_signal(enrichment_table, parameters, root):

    # Get density w.r.t. rest of the NOG matrix per cluster
    Flame_out = pd.read_table(os.path.join(root, "FLAME_output_d4_knn15_axis0.txt"), sep="\t", header=None)
    NOGdir_path = "/".join(root.split("/")[:-1])
    NOG_path = os.path.join(NOGdir_path, os.listdir(NOGdir_path)[0])
    NOG_matrix = pd.read_table(NOG_path, sep=" ")

    out = []
    for cluster in set(enrichment_table["#set_id"]):

        cluster_titles = Flame_out[Flame_out.iloc[:, 0] == cluster][1]
        non_cluster_titles = Flame_out[Flame_out.iloc[:, 0] != cluster][1]

        NOG_matrix_cluster = NOG_matrix.loc[cluster_titles]
        NOG_matrix_non_cluster = NOG_matrix.loc[non_cluster_titles]
        # Calculate density

        # 1. Select NOGs to look at (we want positive signals)

        # A. with two sample  T test; watch out for small sized clusters.... maybe set ftr_consistence assez haut
        s, p = stats.ttest_ind(NOG_matrix_non_cluster, NOG_matrix_cluster, equal_var=False)
        summ = pd.DataFrame({"p.value": p})
        cluster_FC = NOG_matrix_cluster.mean(axis=0) / NOG_matrix_non_cluster.mean(axis=0)
        summ.index = NOG_matrix.columns
        summ["FC"] = cluster_FC

        # B. Filter only pvalues smaller than 0.05
        summ = summ[summ['p.value'] <= parameters['pval_filter']]

        cluster_positive = sum(summ['FC'] > parameters['FC_modifier'])
        cluster_negative = sum(summ['FC'] < (1 / parameters['FC_modifier']))
        cluster_neutral = len(NOG_matrix_cluster.columns) - (cluster_negative + cluster_positive)

        # C. only keep if fold change is large/small enough
        # print(summ, cluster_positive, cluster_negative, cluster_neutral)
        addout = {'#set_id': cluster, "pos_sig": cluster_positive, 'neg_sig': cluster_negative, "no_sig": cluster_neutral}
        out.append(addout)

    out = pd.DataFrame(out)
    return pd.merge(enrichment_table, out, on='#set_id')


def main():
    parameters = get_param()

    #Verbosity
    paramprint = copy.deepcopy(parameters)
    paramprint.pop("scan_dir")
    paramprint.pop("outdir")
    print("[INFO] Parameters used to filter:")
    [print("#", x, ">=", paramprint[x]) for x in paramprint]
    print("\n")

    out = collect_data(parameters)



    #write or do something ....

    if len(out) == 0:
        print("NO enrichments found!")
    else:
        print(out)
        print("GO-terms that generated enriched clusters and met your criteria:", set(out["GO_TERM"]))

if __name__ == '__main__':
    main()
