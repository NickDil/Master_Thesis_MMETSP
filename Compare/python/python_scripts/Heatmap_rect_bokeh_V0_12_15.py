


import argparse
import pandas as pd
import numpy as np
import json
import pymysql
from bokeh.io import show, save
from bokeh.layouts import gridplot
from bokeh.models import LinearColorMapper, Title, HoverTool, LogColorMapper, BasicTicker, PrintfTickFormatter, ColorBar
from bokeh.plotting import figure, output_file
from bokeh.palettes import viridis, grey, inferno, Category20, Set3 #@Unresolvedreference




def get_param():
    '''
    Function that parses command line input of parameters needed to execute the FLAME_clustering.py script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(description='Create heatmap, optionally clustered from flame output')

    # args
    parser.add_argument('input_table', type=str, help="Path to NOG matrix you want to visualize in a heatmap.")
    parser.add_argument('-outdir', '-o', type=str, default="./", help="Specify output directory, defaults to working dir.")
    parser.add_argument('-row_order', "-r", type=str, help="(FLAME)clustering output file specifying the sample clusters.")
    parser.add_argument('-col_order', "-c", type=str, help="(FLAME)clustering output file specifying the NOG clusters.")
    parser.add_argument('-data_main', "-d", type=str, help="Experiment data selection to use (_main.csv file).")
    parser.add_argument('-greyscale', "-bw", action='store_true', help="Toggle to plot in black and white (greyscale).")
    parser.add_argument('-show', "-s", action='store_true', help="Toggle to open HTML file immediately in browser")

    parser.add_argument('--DBCONFIG', '-D',
                        help='Argument that reads in all parameters'
                             ' for DB connection from config_connect_trapid.json file. ',
                        type=str)

    args = parser.parse_args()
    out_dict = vars(args)

    return out_dict

def color_clusters(NOG_matrix, row_order):

    NOGs = list(NOG_matrix.columns)
    titles = list(NOG_matrix.index)
    NOG_zeros = NOG_matrix[NOG_matrix == 0]
    NOG_matrix = NOG_matrix[NOG_matrix != 0]

    # reshape to 1D array or rates with a month and year for each row.
    df = pd.DataFrame(NOG_matrix.stack(), columns=["Y"]).reset_index()
    df.columns = ["title", "NOG", "counts"]

    # Add cluster information
    clusters = pd.DataFrame(row_order[0])
    clusters['title'] = NOG_matrix.index
    clusters.columns = ['cluster', 'title']
    df = pd.merge(df, clusters, on='title')

    dfzeros = pd.DataFrame(NOG_zeros.stack(), columns=["Y"]).reset_index()
    dfzeros.columns = ["title", "NOG", "counts"]

    # Add cluster information
    dfzeros = pd.merge(dfzeros, clusters, on='title')

    # this is the colormap from the original NYTimes plot
    # colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    colors = list(np.array(colfunct_image(20)))
    mapper = LogColorMapper(palette=colors, low=df.counts.min(), high=df.counts.max())

    print(mapper)
    # HOW to incorparate cluster information in plot?
    clustcol = np.unique(df['cluster'])
    ncolor = list(np.array(Set3[len(clustcol)]))
    dfcolor = pd.DataFrame({'cluster': clustcol, 'color': ncolor})
    df = df.merge(dfcolor, on='cluster')
    dfzeros = dfzeros.merge(dfcolor, on='cluster')

    df["alpha"] = np.log(df["counts"])

    TOOLS = "box_zoom,save,reset,wheel_zoom"

    hover = HoverTool(tooltips=[
        ("title", "@title"),
        ("NOG", "@NOG"),
        ("(normalized) counts", "@counts"),
        ("cluster", "@cluster"),
        ("cluster color", "$color[hex, swatch]:color"),
        ("core_gf_score", "@completeness_score"),
        ("index", "$index"),
        ("quantile", "@quantile%")
    ])

    tools_to_show = [hover, TOOLS]

    p = figure(title="Heatmap",
               x_range=NOGs, y_range=list(reversed(titles)),
               x_axis_location="above",
               tools=tools_to_show, toolbar_location='below',
               )

    p.plot_width = 1024
    p.plot_height = 1024
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "10pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = np.pi / 3

    p.rect(x="NOG", y="title", width=0.95, height=0.95,
           source=df,
           #fill_color={'field': 'counts', 'transform': mapper},
           fill_color='color',
           alpha='alpha',
           line_color=None,
           # hover_line_color="black", hover_color={'field': 'counts', 'transform': mapper}
           )
    # plot zero values
    p.rect(x="NOG", y="title", width=0.95, height=0.95,
           source=dfzeros,
           fill_color="white",
           alpha = 0.9,
           line_color=None,
           # hover_line_color="black", hover_color={'field': 'counts', 'transform': mapper}
           )

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d"),
                         label_standoff=6, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    return p

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
    fh = open(parameters["DBCONFIG"], 'r')
    config_data = json.load(fh)
    fh.close()

    username = config_data['trapid_db_user']
    pswd = config_data['trapid_db_pswd']
    db = 'db_trapid_ref_eggnog_test'
    url = config_data['trapid_db_server']
    portname = config_data['trapid_db_port']

    #connect to db
    cnx = pymysql.connect(user=username, passwd=pswd, host=url, db=db, port=portname)
    return cnx

def plot_heatmap(NOG_matrix, row_clusters, data_main, parameters):

    # init COLOR functions

    colfunct_clusters = inferno
    colfunct_image = viridis
    color_METADATA = Category20[20] + Set3[12]

    if parameters["greyscale"]:
        colfunct_clusters = grey
        colfunct_image = grey
        color_METADATA = grey(32)

    ## Adding desriptions
    #read NOG descriptions
    db_con = connect_eggnog(parameters)

    #create cursor
    cursor = db_con.cursor()

    # Create new database entry for experiment
    gf_ids = NOG_matrix.columns

    print("[INFO] selecting metadata")

    sql = "SELECT functional_categories.description, gene_families.gf_id " \
          "FROM gene_families LEFT JOIN functional_categories " \
          "ON gene_families.func_cats  = functional_categories.func_cat_id " \
          "WHERE gf_id IN ('%s')"%("', '".join(gf_ids))

    cursor.execute(sql)
    desc = cursor.fetchall()
    desc = pd.DataFrame({"NOG": [x[1] for x in desc], "desc": [x[0] for x in desc]})
    db_con.close()
    ### DATA FORMATTING ###

    print("[INFO] Adding metadata info")
    NOGs = list(NOG_matrix.columns)
    titles = pd.DataFrame({"title" : list(NOG_matrix.index)})
    NOG_zeros = NOG_matrix[NOG_matrix == 0]
    NOG_matrix = NOG_matrix[NOG_matrix != 0]


    # reshape to 1D array of counts with a NOG and TITLE for each row.
    df = pd.DataFrame(NOG_matrix.stack(), columns=["Y"]).reset_index()
    df.columns = ["title", "NOG", "counts"]

    # ADD CLUSTER and desc INFO
    clusters = pd.DataFrame(row_clusters[0])
    clusters['title'] = NOG_matrix.index
    clusters.columns = ['cluster', 'title']
    df = pd.merge(df, clusters, on='title')
    df = pd.merge(df, desc, on='NOG')

    dfzeros = pd.DataFrame(NOG_zeros.stack(), columns=["Y"]).reset_index()
    dfzeros.columns = ["title", "NOG", "counts"]
    dfzeros = pd.merge(dfzeros, clusters, on='title')
    dfzeros = pd.merge(dfzeros, desc, on='NOG')



    # HOW to incorparate CLUSTER information in plot?
    unique_clusters = unique_order(df['cluster'])
    n_color_clusters = list(np.array(colfunct_clusters(len(unique_clusters))))
    # permutate
    n_color_clusters[::2] = n_color_clusters[::2][::-1]
    df_cluster_color = pd.DataFrame({'cluster': unique_clusters, 'color_clust': n_color_clusters})
    df = df.merge(df_cluster_color, on='cluster')
    dfzeros = dfzeros.merge(df_cluster_color, on='cluster')

    df_cluster_bar = clusters.merge(df_cluster_color, on='cluster')
    # df["alpha"] = np.log(df["counts"])



    #Add metadata info
    tax = data_main[['title', "species_MMETSP"]]
    tax[pd.isnull(tax)] = "Unknown"
    tax = titles.merge(tax, on='title') # order phyla
    df = df.merge(tax, on='title')
    dfzeros = dfzeros.merge(tax, on='title')

    METADATA = data_main.iloc[:,1:3]
    metadata_annotation = METADATA.columns[1]

    METADATA = titles.merge(METADATA, on='title') # order phyla
    df = df.merge(METADATA, on='title')
    dfzeros = dfzeros.merge(METADATA, on='title')

    # Create colors for bar
    unique_METADATA = sorted(list(set((df[metadata_annotation])))) #sort to remove randomness
    n_color_METADATA = list(np.array(color_METADATA[:len(unique_METADATA)]))

    df_METADATA_color = pd.DataFrame({metadata_annotation: unique_METADATA, 'color_metadata': n_color_METADATA})
    #ordered
    df = df.merge(df_METADATA_color, on=metadata_annotation)
    dfzeros = dfzeros.merge(df_METADATA_color, on=metadata_annotation)

    df_metadata_bar = METADATA.merge(df_METADATA_color, on=metadata_annotation)

    # Colors for heatmap
    colors = list(np.array(colfunct_image(20)))
    mapper = LogColorMapper(palette=colors, low=df.counts.min(), high=df.counts.max())

    tools_to_show = ['box_zoom, pan, wheel_zoom, reset, hover']


    #### PLOTTING ####
    print("[INFO] construct heatmap")


    ### Metadata color bar figure ###
    h = figure(y_range=list(reversed(titles["title"])),
               plot_width=120,
               tools='hover')

    h.rect(x=0, y="title", width=1, height=1,
           source=df_metadata_bar,
           fill_color="color_metadata",
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
    h.add_layout(Title(text=metadata_annotation, align="center", text_font_size="9px"), "above")

    h.select_one(HoverTool).tooltips = [(metadata_annotation, '@{}'.format(metadata_annotation))]

    ### Cluster color bar figure ###
    z = figure(y_range=h.y_range,
               plot_width=50, #title="{} clusters".format(len(n_color_clusters)),
               tools='hover')

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

    z.select_one(HoverTool).tooltips = [('Cluster', '@cluster')]


    ### HEATMAP ###
    p = figure(title="Heatmap of {} clustered by {}".format(parameters["input_table"].split("/")[-1], parameters["row_order"].split("/")[-1]),
               title_location="above", x_range=NOGs,
               y_range=h.y_range,
               x_axis_location="above",
               tools=tools_to_show, toolbar_location='below',
               )

    p.plot_width = 1600
    p.plot_height = 1024
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "10pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = np.pi/3
    p.yaxis.visible = False
    # p.title.visible = False

    p.rect(x="NOG", y="title", width=1, height=1,
           source=df,
           fill_color={'field': 'counts', 'transform': mapper},
           line_color=None,
           # hover_line_color="black", hover_color={'field': 'counts', 'transform': mapper}
           )
    # plot zero values
    p.rect(x="NOG", y="title", width=1, height=1,
           source=dfzeros,
           fill_color="grey",
           line_color=None,
           # hover_line_color="black", hover_color={'field': 'counts', 'transform': mapper}
           )


    # Anti Bug of 0.12.15 color bar does not work with 0-1 data ?
    if not sum(df["counts"] != 1) == 0:
        color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                             ticker=BasicTicker(desired_num_ticks=len(colors)),
                             formatter=PrintfTickFormatter(format="%d"),
                             label_standoff=6, border_line_color=None, location=(0, 0))
        p.add_layout(color_bar, 'right')


    p.select_one(HoverTool).tooltips = [
        ("sample", "@title"),
        ("NOG", "@NOG : @desc"),
        ("counts", "@counts"),
        ("cluster", "@cluster"),
        (metadata_annotation, "@{}".format(metadata_annotation)),
        ("species", "@species_MMETSP")
        #("cluster color", "$color[hex, swatch]:color"),
    ]

    grid = gridplot([[ h, z, p]], tools=tools_to_show,
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

def read_json(DBCONFIG):
    with DBCONFIG as json_data_file:
        config_data = json.load(json_data_file)
    DBCONFIG.close()

    return config_data

def main(parameters):

    NOG_matrix = pd.read_table(parameters["input_table"], sep=" ")
    data_main = pd.read_table(parameters["data_main"], sep=",", encoding='latin-1')


    file = parameters["input_table"].rstrip(".txt")
    output_file(file + "_heatmap_image.html", title="Interactive heatmap")

    ordered_NOG_matrix = NOG_matrix
    if parameters["row_order"]:
        print("ORDERING ROWS")
        row_clusters = pd.read_table(parameters["row_order"], sep="\t", header=None)
        ordered_NOG_matrix = order_NOG_matrix(NOG_matrix, row_clusters, ax=0)
        if parameters["col_order"]:
            print("ORDERING Columns")

            col_clusters = pd.read_table(parameters["col_order"], sep="\t", header=None)
            ordered_NOG_matrix = order_NOG_matrix(ordered_NOG_matrix, col_clusters, ax=1)
    print('PLOTTING')
    p = plot_heatmap(ordered_NOG_matrix, row_clusters, data_main, parameters)
    if parameters["show"]:
        print("BCDSBVBSFKVBJ")
        show(p)
    else:
        save(p)

if __name__ == '__main__':
    parameters = get_param()
    print(parameters)
    main(parameters)
