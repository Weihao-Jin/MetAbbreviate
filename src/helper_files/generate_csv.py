import json
import os
import regex as re
import pandas as pd

name_in_box = 'proteomics'
name_to_file = 'proteomics'
path = f'D:/Downloads/jinweihao/2021-2022/DS-NLP/output/re_find/{name_in_box}'
to_file = f'D:/Downloads/jinweihao/2021-2022/DS-NLP/output/re_find/abbre_csv/{name_to_file}'
output = pd.DataFrame(columns=['PMCID', 'position', 'sentence', 'abbreviation', 'method'])

for x in os.listdir(path):
    if x.endswith('abbreviations.json'):
        all_abbreviations = []
        with open(f'{path}/{x}', 'r', encoding='utf-8') as f:
            PMCid = re.search(f'(.*)_abbreviations', x).group(1)
            abbres_file = json.load(f)
            abbres = abbres_file['documents'][0]['passages']
            for dic in abbres:
                merged_lis = dic['res1'] + dic['res2'] + dic['res3']
                for one_abbre in merged_lis:
                    # output.loc[len(output.index)] = [PMCid, dic['position'], dic['sentence'], one_abbre,
                    #                                  're in main text']
                    if one_abbre not in all_abbreviations:
                        all_abbreviations.append(one_abbre)
                        output.loc[len(output.index)] = [PMCid, dic['position'], dic['sentence'], one_abbre, 're in main text']
output.to_csv(f'{to_file}.csv', encoding='utf_8_sig')

