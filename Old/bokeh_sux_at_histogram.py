
from bokeh.io import show, output_file
from bokeh.plotting import figure
from Bio import SeqIO
import pandas as pd

tr_len = pd.Series()

for seq_record in SeqIO.parse("/home/nidil/Documents/Project_TRAPID/Data/MMETSP1399.nt.fa", "fasta"):
    tr_len = tr_len.append(pd.Series(len(seq_record)))

output_file("Length_distribution_sequences.html")

values = tr_len.value_counts()

p = figure(plot_height=250, title="Length_distribution_sequences",
           toolbar_location=None, tools="")

p.vbar(x=tr_len, top=values, width=10)

show(p)
