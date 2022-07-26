import pandas as pd
import numpy as np

filepath = 'D:/Downloads/jinweihao/2021-2022/DS-NLP/LRRFIP1_heatmap_exon.csv'

e = pd.DataFrame()
res = pd.DataFrame()
# e['col1'] = [0, 0, 0, 0]
# e['col2'] = [0, 1, 0, 0]
# e['col3'] = ['1.1', '10.1;11.1', '5.1;8.1', '3.4;5.4']
#
# e['sort'] = e['col3'].str.split('.', 1).str.get(0)
# print(e)
e = pd.read_csv(filepath, sep='\t')
e['sort'] = e['Exon_Label'].str.split('.', 1).str.get(0).astype(int)
e.sort_values('sort', inplace=True)

print('2'>'11')