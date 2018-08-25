import argparse
import pandas as pd
import numpy as np
from bokeh.io import show
from bokeh.layouts import gridplot
from bokeh.models import LinearColorMapper, Title, HoverTool, LogColorMapper, BasicTicker, PrintfTickFormatter, ColorBar
from bokeh.plotting import figure, output_file
from bokeh.palettes import viridis #@Unresolvedreference
from bokeh.palettes import Category20 #@Unresolvedreference
from bokeh.palettes import Set3 #@Unresolvedreference



def get_param():
    '''
    Function that parses command line input of parameters needed to execute the FLAME_clustering.py script.

    :return:
    Dictionary with input parameters
    '''

    parser = argparse.ArgumentParser(description='Create heatmap, optionally clustered from flame output')

    # args
    parser.add_argument('NOG_matrix', type=str, help="path to NOG matrix you want to visualize with in a heatmap")
    parser.add_argument('-outdir', '-o', type=str, default="./", help="Specify output directory, defaults to working dir")
    parser.add_argument('-gene_set', "-g", type=str, help="gene set specifying the clusters")
    parser.add_argument('-data_main', "-d", type=str, help="Experiment data selection to use (_main.csv file)")

    args = parser.parse_args()
    out_dict = vars(args)
    return out_dict

def color_clusters(NOG_matrix, gene_set):

    NOGs = list(NOG_matrix.columns)
    titles = list(NOG_matrix.index)
    NOG_zeros = NOG_matrix[NOG_matrix == 0]
    NOG_matrix = NOG_matrix[NOG_matrix != 0]

    # reshape to 1D array or rates with a month and year for each row.
    df = pd.DataFrame(NOG_matrix.stack(), columns=["Y"]).reset_index()
    df.columns = ["title", "NOG", "counts"]

    # Add cluster information
    clusters = pd.DataFrame(gene_set[0])
    clusters['title'] = NOG_matrix.index
    clusters.columns = ['cluster', 'title']
    df = pd.merge(df, clusters, on='title')

    dfzeros = pd.DataFrame(NOG_zeros.stack(), columns=["Y"]).reset_index()
    dfzeros.columns = ["title", "NOG", "counts"]

    # Add cluster information
    dfzeros = pd.merge(dfzeros, clusters, on='title')

    # this is the colormap from the original NYTimes plot
    # colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    colors = list(np.array(viridis(20)))
    mapper = LogColorMapper(palette=colors, low=df.counts.min(), high=df.counts.max())

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

def plot_heatmap(NOG_matrix, gene_set, data_main, parameters):

    ### DATA FORMATTING ###

    NOGs = list(NOG_matrix.columns)
    titles = pd.DataFrame({"title" : list(NOG_matrix.index)})
    NOG_zeros = NOG_matrix[NOG_matrix == 0]
    NOG_matrix = NOG_matrix[NOG_matrix != 0]

    # reshape to 1D array of counts with a NOG and TITLE for each row.
    df = pd.DataFrame(NOG_matrix.stack(), columns=["Y"]).reset_index()
    df.columns = ["title", "NOG", "counts"]

    # ADD CLUSTER INFO
    clusters = pd.DataFrame(gene_set[0])
    clusters['title'] = NOG_matrix.index
    clusters.columns = ['cluster', 'title']
    df = pd.merge(df, clusters, on='title')

    dfzeros = pd.DataFrame(NOG_zeros.stack(), columns=["Y"]).reset_index()
    dfzeros.columns = ["title", "NOG", "counts"]
    dfzeros = pd.merge(dfzeros, clusters, on='title')

    # HOW to incorparate CLUSTER information in plot?
    unique_clusters = np.unique(df['cluster'])
    n_color_clusters = list(np.array(Set3[len(unique_clusters)]))
    df_cluster_color = pd.DataFrame({'cluster': unique_clusters, 'color_clust': n_color_clusters})
    df = df.merge(df_cluster_color, on='cluster')
    dfzeros = dfzeros.merge(df_cluster_color, on='cluster')

    df_cluster_bar = clusters.merge(df_cluster_color, on='cluster')
    # df["alpha"] = np.log(df["counts"])

    # ADD METADATA INFO
    phyla = data_main[['title', 'phylum_MMETSP']]
    phyla[pd.isnull(phyla)] = "Unknown"
    phyla = titles.merge(phyla, on='title') # order phyla
    df = df.merge(phyla, on='title')
    dfzeros = dfzeros.merge(phyla, on='title')

    # Create colors for bar
    unique_phyla = sorted(list(set((df['phylum_MMETSP'])))) #sort to remove randomness
    color_phyla = Category20[20] + Set3[12]
    n_color_phyla = list(np.array(color_phyla[:len(unique_phyla)]))
    df_phylum_color = pd.DataFrame({'phylum_MMETSP': unique_phyla, 'color_phylum_MMETSP': n_color_phyla})
    #ordered
    df = df.merge(df_phylum_color, on='phylum_MMETSP')
    dfzeros = dfzeros.merge(df_phylum_color, on='phylum_MMETSP')

    df_metadata_bar = phyla.merge(df_phylum_color, on='phylum_MMETSP')

    # Colors for heatmap
    colors = list(np.array(viridis(20)))
    mapper = LogColorMapper(palette=colors, low=df.counts.min(), high=df.counts.max())

    hover = HoverTool(tooltips=[
        ("title", "@title"),
        ("NOG", "@NOG"),
        ("counts", "@counts"),
        ("cluster", "@cluster"),
        ("phylum", "@phylum_MMETSP")
        #("cluster color", "$color[hex, swatch]:color"),
    ])

    tools_to_show = ['box_zoom, pan, wheel_zoom, reset', hover]


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

    ### HEATMAP ###
    p = figure(title="Heatmap of {} clustered by {}".format(parameters["NOG_matrix"].split("/")[-1], parameters["gene_set"].split("/")[-1]),
               title_location="above", x_range=NOGs,
               y_range=h.y_range,
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
    p.xaxis.major_label_orientation = np.pi/3
    p.yaxis.visible = False
    # p.title.visible = False

    p.rect(x="NOG", y="title", width=0.95, height=0.95,
           source=df,
           fill_color={'field': 'counts', 'transform': mapper},
           line_color=None,
           # hover_line_color="black", hover_color={'field': 'counts', 'transform': mapper}
           )
    # plot zero values
    p.rect(x="NOG", y="title", width=0.95, height=0.95,
           source=dfzeros,
           fill_color="grey",
           line_color=None,
           # hover_line_color="black", hover_color={'field': 'counts', 'transform': mapper}
           )

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d"),
                         label_standoff=6, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    grid = gridplot([[h, z, p]], tools=tools_to_show,
                    #merge_tools=True,
                    toolbar_location='below')
    return grid

def main():
    parameters = get_param()
    NOG_matrix = pd.read_table(parameters["NOG_matrix"], sep=" ")
    gene_set = pd.read_table(parameters["gene_set"], sep="\t", header=None)
    data_main = pd.read_table(parameters["data_main"], sep=",", encoding='latin-1')

    # Get titles from ordered experiment ids
    ordered_exp_id = pd.DataFrame(gene_set.iloc[:,1])
    ordered_exp_id.columns = ['experiment_id']
    ordered_titles = pd.DataFrame(pd.merge(ordered_exp_id, data_main, on='experiment_id').title)

    # Sort NOG matrix on title
    NOG_matrix["title"] = NOG_matrix.index
    ordered_NOG_matrix = pd.merge(ordered_titles, NOG_matrix, on='title')
    # remove title column
    ordered_NOG_matrix.index = ordered_NOG_matrix["title"]
    ordered_NOG_matrix = ordered_NOG_matrix.drop("title", axis=1)

    NOG_matrix = pd.read_table(parameters["NOG_matrix"], sep=" ")

    file = parameters["NOG_matrix"].rstrip(".txt")
    output_file(file + "_heatmap.html", title="Interactive heatmap")

    show(plot_heatmap(ordered_NOG_matrix, gene_set, data_main, parameters))
    # show(color_clusters(ordered_NOG_matrix, gene_set))



if __name__ == '__main__':
    main()


