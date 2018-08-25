# Create data in appropriate format
import numpy as np

from bokeh.plotting import figure, show, output_file
import pandas as pd

NOG_matrix = pd.read_table("/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/Compare/Results/EggNOG_all_userID_10_results/bliepbloep", sep=" ")

NOG_matrix = NOG_matrix.iloc[0:100,0:100]

y = list(NOG_matrix.index)
x = list(NOG_matrix.columns)
counts = np.array(NOG_matrix)


colormap = ["lightgrey","red"]
xname = []
yname = []
color = []
for i, node1 in enumerate(x):
    for j, node2 in enumerate(y):
        xname.append(node1)
        yname.append(node2)
        if counts[j,i] ==1:
            color.append(colormap[1])
        else:
            color.append(colormap[0])

data=dict(
    xname=xname,
    yname=yname,
    colors=color,
    count=np.transpose(counts).flatten(),
)

p = figure(title="Heatmap",
           x_axis_location="above", tools="hover,box_zoom,save,reset,wheel_zoom",
           x_range=x, y_range=y[::-1],
           tooltips=[('Title', '@yname'),('NOG', '@xname'), ('count', '@count')])


p.plot_width = 800
p.plot_height = 1500
p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "6pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = np.pi/3

p.rect('xname', 'yname', 0.9, 0.9, source=data,
       color='colors', line_color=None,
       hover_line_color='black', hover_color='colors')

# color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
#                      ticker=BasicTicker(desired_num_ticks=len(colors)),
#                      formatter=PrintfTickFormatter(format="%d%%"),
#                      label_standoff=6, border_line_color=None, location=(0, 0))
# p.add_layout(color_bar, 'right')

output_file("Heatmap.html", title="Heatmap")

show(p)