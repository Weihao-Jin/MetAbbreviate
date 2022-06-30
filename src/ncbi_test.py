import json

import requests
import xml.etree.ElementTree as ET

# db_list = ['protein', 'nuccore', 'ipg', 'nucleotide', 'genome', 'bioproject', 'gap', 'gapplus', ]

def __try_to_categorize__(term, database, to_dir=None):
    res_dict = {}
    for db in database:
        req = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db={db}&term={term}"
        response = requests.get(req)
        root = ET.fromstring(response.content)
        count = root.find("Count").text
        res_dict[db] = int(count)
    res_dict = dict(sorted(res_dict.items(), key=lambda item: item[1], reverse=True))
    return res_dict

def find_usabel_datasets(to_file):
    dblist_xml = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi")
    root = ET.fromstring(dblist_xml.content)
    dbList = []
    for db in root[0]:
        dbList.append(db.text)
    with open(to_file, 'w') as f:
        f.write(json.dumps(dbList))

valid_databases_path = 'D:/Downloads/jinweihao/2021-2022/DS-NLP/output/ncbi_xml/valid_databases.txt'
# find_usabel_datasets(valid_databases_path)
val_db = None
with open(valid_databases_path, 'r') as f:
    val_db = json.loads(f.read())

res = __try_to_categorize__("HIV", val_db)
res = dict(sorted(res.items(), key=lambda item: item[1], reverse=True))
# -------------------------------------
term = "38-kDa"
db = "nuccore"

# req = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=3269"
req = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db={db}&term={term}"
response = requests.get(req)
root = ET.fromstring(response.content)
tree = ET.ElementTree(root)
# print(root.find("Count").text)

file_name = term
to_file = f"D:/Downloads/jinweihao/2021-2022/DS-NLP/output/ncbi_xml/{file_name}_{db}.xml"

with open(to_file, 'w') as f:
    tree.write(f, encoding='unicode')




