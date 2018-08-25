import argparse
import pandas as pd
import pymysql
import json
import numpy as np
from bokeh.io import show, save
from bokeh.layouts import gridplot
from bokeh.models import LinearColorMapper, Title, HoverTool, LogColorMapper, BasicTicker, PrintfTickFormatter, ColorBar
from bokeh.plotting import figure, output_file
from bokeh.palettes import viridis, grey, inferno, cividis, Category20, Set3 #@Unresolvedreference


""" For bokeh V0.13.0"""


def get_param():
    '''
    Function that parses command line input of parameters needed to execute the FLAME_clustering.py script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(description='Create heatmap, optionally clustered from flame output')

    # args
    parser.add_argument('NOG_matrix', type=str, help="Path to NOG matrix you want to visualize in a heatmap.")
    parser.add_argument('-outdir', '-o', type=str, default="./", help="Specify output directory, defaults to working dir.")
    parser.add_argument('-row_order', "-r", type=str, help="(FLAME)clustering output file specifying the sample clusters.")
    parser.add_argument('-col_order', "-c", type=str, help="(FLAME)clustering output file specifying the NOG clusters.")
    parser.add_argument('-data_main', "-d", type=str, help="Experiment data selection to use (_main.csv file).")
    parser.add_argument('-greyscale', "-bw", action='store_true', help="Toggle to plot in black and white (greyscale).")
    parser.add_argument('-show', "-s", action='store_true', help="Toggle to open HTML file immediately in browser")

    parser.add_argument('--DBCONFIG', '-D',
                        help='Argument that reads in all parameters'
                             ' for DB connection from config_connect_trapid.json file. ',
                        type=argparse.FileType('r', encoding='UTF-8'))

    args = parser.parse_args()
    out_dict = vars(args)

    if args.DBCONFIG:

        with args.DBCONFIG as json_data_file:
            config_data = json.load(json_data_file)
        args.DBCONFIG.close()

        for p in config_data.keys():
            out_dict[p] = config_data[p]

    return out_dict

def unique_order(sequence):
    """
    code from: http://www.martinbroadhurst.com/removing-duplicates-from-a-list-while-preserving-order-in-python.html

    :param sequence:
    :return: unique elements in the sequence in the order you encounter them, i.e. original order
    """
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def connect_eggnog(parameters):
    """
    Adapted version of code from Thomas Depuyt (/home/nidil/Documents/Project_TRAPID/Scripts/MySQL_test.py)
    just opens connection to TRAPID DB, does not create cursor,
    need connection to work with pandas pd.read_sql()

    configuration parameters from config_connect_trapid.json
    """
    #read config_data
    username = parameters['trapid_db_user']
    pswd = parameters['trapid_db_pswd']
    db = 'db_trapid_ref_eggnog_test'
    url = parameters['trapid_db_server']
    portname = parameters['trapid_db_port']

    #connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx

def plot_heatmap_image(NOG_matrix, row_clusters, data_main, parameters):


    # init COLOR functions

    colfunct_clusters = inferno
    colfunct_image = viridis
    color_phyla = Category20[20] + Set3[12]

    if parameters["greyscale"]:
        colfunct_clusters = grey
        colfunct_image = grey
        color_phyla = grey(32)


    ### DATA FORMATTING ###

    # NOGs = list(NOG_matrix.columns)
    titles = pd.DataFrame({"title" : list(NOG_matrix.index)})
    # NOG_zeros = NOG_matrix[NOG_matrix == 0]
    # NOG_nzeros = NOG_matrix[NOG_matrix != 0]


    # # reshape to 1D array of counts with a NOG and TITLE for each row.
    # df = pd.DataFrame(NOG_matrix.stack(), columns=["Y"]).reset_index()
    # df.columns = ["title", "NOG", "counts"]

    # ADD CLUSTER INFO
    clusters = pd.DataFrame(row_clusters[0])
    clusters['title'] = NOG_matrix.index
    clusters.columns = ['cluster', 'title']
    # df = pd.merge(df, clusters, on='title')

    # dfzeros = pd.DataFrame(NOG_zeros.stack(), columns=["Y"]).reset_index()
    # dfzeros.columns = ["title", "NOG", "counts"]
    # dfzeros = pd.merge(dfzeros, clusters, on='title')

    # HOW to incorparate CLUSTER information in plot?

    unique_clusters = unique_order(clusters['cluster'])
    n_color_clusters = list(np.array(colfunct_clusters(len(unique_clusters))))
    # permutate
    n_color_clusters[::2] = n_color_clusters[::2][::-1]
    # n_color_clusters[::2] = n_color_clusters[::2][1:]+[n_color_clusters[::2][0]]
    # n_color_clusters=np.random.choice(n_color_clusters, len(n_color_clusters), replace=False)

    df_cluster_color = pd.DataFrame({'cluster': unique_clusters, 'color_clust': n_color_clusters})
    # df = df.merge(df_cluster_color, on='cluster')
    # dfzeros = dfzeros.merge(df_cluster_color, on='cluster')

    df_cluster_bar = clusters.merge(df_cluster_color, on='cluster')
    # df["alpha"] = np.log(df["counts"])

    # ADD METADATA INFO
    phyla = data_main[['title', 'phylum_MMETSP']]
    phyla[pd.isnull(phyla)] = "Unknown"
    phyla = titles.merge(phyla, on='title') # order phyla back
    # df = df.merge(phyla, on='title')
    # dfzeros = dfzeros.merge(phyla, on='title')


    #remove annotation mistake
    phyla["phylum_MMETSP"][phyla["phylum_MMETSP"]=='Forminafera'] = "Foraminifera"


    # Create colors for bar
    unique_phyla = sorted(list(set(phyla["phylum_MMETSP"]))) #sort to remove randomness

    # color_phyla = Category20[20] + Set3[12]
    n_color_phyla = list(np.array(color_phyla[:len(unique_phyla)]))
    df_phylum_color = pd.DataFrame({'phylum_MMETSP': unique_phyla, 'color_phylum_MMETSP': n_color_phyla})
    df_phylum_color["color_phylum_MMETSP"][df_phylum_color["phylum_MMETSP"] == "Unknown"] = 'black'
    #ordered
    # df = df.merge(df_phylum_color, on='phylum_MMETSP')
    # dfzeros = dfzeros.merge(df_phylum_color, on='phylum_MMETSP')

    df_metadata_bar = phyla.merge(df_phylum_color, on='phylum_MMETSP')

    #### PLOTTING ####

    ### Phylum color bar figure ###
    h = figure(y_range=list(reversed(titles["title"])),
               plot_width=120,
               tools='hover', tooltips=[('Phylum', '@phylum_MMETSP')])
    h.rect(x=0, y="title", width=1, height=1,
           source=df_metadata_bar,
           fill_color="color_phylum_MMETSP",
           line_color=None,
           # hover_line_color="black", hover_color={'field': 'counts', 'transform': mapper}
           )

    h.plot_height = 1024
    h.grid.grid_line_color = None
    h.axis.axis_line_color = None
    h.axis.major_tick_line_color = None
    h.axis.major_label_text_font_size = "7pt"
    h.axis.major_label_standoff = 0
    h.xaxis.visible = False
    h.add_layout(Title(text="Metadata", align="center", text_font_size="9px"), "above")


    ### Cluster color bar figure ###
    z = figure(y_range=h.y_range,
               plot_width=50, #title="{} clusters".format(len(n_color_clusters)),
               tools='hover', tooltips=[('Cluster', '@cluster')])

    z.rect(x=0, y="title", width=1, height=1,
           source=df_cluster_bar,
           fill_color="color_clust",
           line_color=None,
           # hover_line_color="black", hover_color={'field': 'counts', 'transform': mapper}
           )

    z.plot_height = 1024
    z.grid.grid_line_color = None
    z.axis.axis_line_color = None
    z.axis.major_tick_line_color = None
    z.axis.major_label_text_font_size = "10px"
    z.axis.major_label_standoff = 0
    z.xaxis.visible = False
    z.yaxis.visible = False
    z.add_layout(Title(text="Cluster", align="center", text_font_size="9px"), 'above')


    #### HEATMAP IMAGE #####

    list_title = []
    for each in NOG_matrix.index:
        row = [each]*len(NOG_matrix.columns)
        list_title.append(row)

    list_title = np.array(list_title[::-1])

    list_NOG = [NOG_matrix.columns]*len(NOG_matrix.index)

    #read NOG descriptions
    db_con = connect_eggnog(parameters)

    #create cursor
    cursor = db_con.cursor()

    # Create new database entry for experiment
    gf_ids = NOG_matrix.columns

    sql = "SELECT functional_categories.description, gene_families.gf_id " \
          "FROM gene_families LEFT JOIN functional_categories " \
          "ON gene_families.func_cats  = functional_categories.func_cat_id " \
          "WHERE gf_id IN ('%s')"%("', '".join(gf_ids))

    cursor.execute(sql)
    desc = cursor.fetchall()
    desc = pd.DataFrame([x[0] for x in desc])
    desc.index = sorted(gf_ids)
    desc = desc.loc[gf_ids]

    list_desc = list(desc[0])*len(NOG_matrix.index)

    # image_nz = np.array(NOG_nzeros.iloc[range(len(NOG_nzeros.index)-1,-1,-1),])
    # image_z = np.array(NOG_zeros.iloc[range(len(NOG_zeros.index)-1,-1,-1),])
    imageNOG = np.array(NOG_matrix.iloc[range(len(NOG_matrix.index)-1,-1,-1),])

    data = dict(image=[imageNOG],
                title=[list_title],
                NOG_id=[list_NOG],
                desc=[list_desc]
                )
    hovertooltips = [
        ("title", "@title"),
        ("NOG_id", "@NOG_id"),
        ("description", '@desc'),
        ("value", "@image")
    ]

    # Colors for heatmap
    colors = list(np.array(colfunct_image(20)))
    maximum = max([max(x) for x in imageNOG])
    mapper = LogColorMapper(palette=colors, low=0, high=maximum)

    tools_to_show = ['box_zoom, pan, wheel_zoom, reset, hover']

    p = figure(x_range=(np.array(NOG_matrix.columns)),
               title="Heatmap of {} clustered".format(parameters["NOG_matrix"].split("/")[-1]),
               y_range=h.y_range,
               tools=tools_to_show, tooltips=hovertooltips, x_axis_location="above")

    # must give a vector of image data for image parameter
    p.image(source=data, image='image', x=0, y=0, dw=len(NOG_matrix.columns), dh=len(NOG_matrix.index), color_mapper=mapper)

    p.plot_width = 1600
    p.plot_height = 1024
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "10pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = np.pi/3
    p.yaxis.visible = False

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d"),
                         label_standoff=6, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')


    grid = gridplot([[h, z, p]], tools=tools_to_show,
                    #merge_tools=True,
                    toolbar_location='below')
    return grid

def order_NOG_matrix(NOG_matrix, order_file, ax):
    if ax == 1:
        # get ordered NOGs
        ordered_colnames = order_file.iloc[:, 1]
        # Sort NOG matrix on NOG-id
        ordered_NOG_matrix = NOG_matrix[ordered_colnames]

    else:
        # Get ordered titles
        ordered_rownames = list(order_file.iloc[:,1])
        ordered_NOG_matrix = NOG_matrix.loc[ordered_rownames]

    return ordered_NOG_matrix

def main():
    parameters = get_param()
    NOG_matrix = pd.read_table(parameters["NOG_matrix"], sep=" ")
    data_main = pd.read_table(parameters["data_main"], sep=",", encoding='latin-1')

    file = parameters["NOG_matrix"].rstrip(".txt")
    output_file(file + "_heatmap_image.html", title="Interactive heatmap")

    ordered_NOG_matrix = NOG_matrix
    if parameters["row_order"]:
        row_clusters = pd.read_table(parameters["row_order"], sep="\t", header=None)
        ordered_NOG_matrix = order_NOG_matrix(NOG_matrix, row_clusters, ax=0)
        if parameters["col_order"]:
            col_clusters = pd.read_table(parameters["col_order"], sep="\t", header=None)
            ordered_NOG_matrix = order_NOG_matrix(ordered_NOG_matrix, col_clusters, ax=1)

    p = plot_heatmap_image(ordered_NOG_matrix, row_clusters, data_main, parameters)
    if parameters["show"]:
        show(p)
    else:
        save(p)

if __name__ == '__main__':
    main()
