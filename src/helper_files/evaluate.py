import os, json
# folder = 'D:/Downloads/jinweihao/2021-2022/DS-NLP/output/PMC601-700'
# folder = 'D:/Downloads/jinweihao/2021-2022/DS-NLP/output/PMC/MWAS/liver'
# folder = 'D:/Downloads/jinweihao/2021-2022/DS-NLP/output/PMC/MWAS/PLOS'
# folder = 'D:/Downloads/jinweihao/2021-2022/DS-NLP/output/PMC/prot/cancer'
folder = 'D:/Downloads/jinweihao/2021-2022/DS-NLP/output/PMC/prot/liver'
full = 0
hyb = 0
author = 0

only_full = 0
both_full_hybrid = 0
only_hybrid = 0
only_author = 0
author_hybrid = 0
new_correct = 0
all_abb = 0
for filename in os.listdir(folder):
    if 'abb' in filename and 'pot' not in filename:
        with open(os.path.join(folder, filename), 'r', encoding='utf8') as f:
            j_file = json.loads(f.read())
            if len(j_file) == 0:
                continue
            for item in j_file['documents'][0]['passages']:
                tmp_full = 0
                tmp_Hybrid = 0
                tmp_author = 0
                all_abb += 1
                for key, value in item.items():
                    if 'extraction' in key:
                        if 'full' in value:
                            tmp_full += 1
                        if 'Hyb' in value:
                            tmp_Hybrid += 1
                        if 'abb' in value:
                            tmp_author += 1
                        if 'full' in value and 'Hyb' in value:
                            both_full_hybrid += 1
                        if 'Hyb' in value and 'abb' in value:
                            author_hybrid += 1
                            if 'full' not in value:
                                new_correct += 1
                if tmp_full > 0 and tmp_Hybrid == 0:
                    only_full += 1
                if tmp_full == 0 and tmp_Hybrid > 0:
                    only_hybrid += 1
                if tmp_author > 0 and tmp_Hybrid == 0 and tmp_full == 0:
                    only_author += 1
                if tmp_full > 0:
                    full += 1
                if tmp_author > 0:
                    author += 1
                if tmp_Hybrid > 0:
                    hyb += 1

print(f'ADA: {all_abb}')
print(f'FS: {full}')
print(f'HFFS: {only_full}')
print(f'HS: {hyb}')
print(f'FFHS: {only_hybrid}')
print(f'AS: {author}')
print(f'OAS: {only_author}')
print(f'F&H: {both_full_hybrid}')
print(f'A&H: {author_hybrid}')
print(f'NC: {new_correct}')
print(f'cover_rate: {(both_full_hybrid/full)}')
print(f'nc_rate: {(new_correct/author)}')



