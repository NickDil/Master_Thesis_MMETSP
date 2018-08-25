import pandas as pd

data_transcripts = pd.read_table("/home/nidil/Documents/Project_TRAPID/Data/transcripts_gf_exp77.txt")

print(data_transcripts.head())

##Gene family information

#how many transcripts that have NA gene family
print('Total amount of transcripts:', data_transcripts['gf_id'].size)
z = data_transcripts['gf_id'].size  - data_transcripts['gf_id'].dropna().size

print('Amount of unattributable transcripts:', z, '\nPercentage of unattributable transcripts:', round(z/data_transcripts['gf_id'].size*100, ndigits=3), '%')

#print(data_transcripts.columns.values)

x = data_transcripts['gf_id'].nunique()
print('GF count:', x)

y = data_transcripts['gf_id'].dropna().unique()
print('GF count other way:', len(y))

#find single copy genes

d = data_transcripts['gf_id'].dropna()
sc = d.drop_duplicates(keep=False)
print('Amount of Single Copy GF\'s:', len(sc))

#transcripts in GF

print('transcripts in GF:', d.count())

#Highest transcript GF
counts = d.value_counts()
print('Top three GF\'s with highest transcript count:\n', counts.head(3))
