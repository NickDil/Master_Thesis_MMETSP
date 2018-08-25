
from Bio import SeqIO
import matplotlib.pyplot as plt
import seaborn


import pandas as pd

tr_len = pd.Series()

for seq_record in SeqIO.parse("/home/nidil/Documents/Project_TRAPID/Data/MMETSP1399.nt.fa", "fasta"):
    tr_len = tr_len.append(pd.Series(len(seq_record)))

print('Amount of transcripts:', tr_len.size)

plt.style.use('seaborn-white')
tr_len.hist(bins=50)
plt.xlabel('NT')
plt.ylabel('#transcripts')
plt.title('Length distribution sequences')
plt.show()





