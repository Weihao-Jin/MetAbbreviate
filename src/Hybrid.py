import json

import numpy as np
from nltk.corpus import stopwords
import re
import regex as re2


# nltk.download()
# st = set(stopwords.words('english'))
# print(len(st))

# replace_dict = {'A': 'α', 'B': 'β', '1': 'one', '2': 'two', '3': 'three'}


def save_replacement_file(replace_dict:dict):
    with open("Auto-CORPus/src/replacement_dictionary.json", "w", encoding='utf8') as f:
        json.dump(replace_dict, f, ensure_ascii=False)


def read_replacement_file():
    # with open("Auto-CORPus/src/replacement_dictionary.json", "r", encoding='utf8') as f:
    with open("src/replacement_dictionary.json", "r", encoding='utf8') as f:
        result = json.loads(f.read())
    return result


replace_dict = read_replacement_file()


def abbre_pattern(abbreviation: str):
    pattern = 'w'
    for ch in ['/', '\\', ',', '.', '-', '_', '&']:
        if ch in abbreviation:
            abbreviation = abbreviation.replace(ch, ' ')
    for c in abbreviation:
        if c == ' ':
            pattern += ' '
        elif c.isdigit() & (pattern[-1] in ['w', ' ']):
            pattern += 'n'
        elif not c.isdigit():
            pattern += 'w'

    return pattern[1:].replace(' ', '')


def find_shortest_candidate(arr_sentence: list, abbreviation: str, start_idx, end_idx):
    one_def = []
    temp_sentence = arr_sentence.copy()
    temp_abbre = abbreviation
    for i in range(start_idx, end_idx):
        if len(one_def) == 0:
            if temp_sentence[i][0].lower() == temp_abbre[0].lower():
                temp_sentence[i] = temp_sentence[i][1:]
                temp_abbre = temp_abbre[1:]
                one_def.append(i)
                # print(f"start {one_def}")
                # print(one_def)
            else:
                continue
        while len(temp_abbre) != 0:
            temp_letter = temp_abbre[0]
            temp_word = temp_sentence[i]
            if temp_letter.lower() in temp_word.lower():
                one_def.append(i)
                # print(f"processing {one_def}")
                temp_sentence[i] = temp_word[(temp_word.lower().index(temp_letter.lower()) + 1):]
                temp_abbre = temp_abbre[1:]
            else:
                break
    # print(f"got one {one_def}")


def find_all_candidate(arr_sentence: list, abbreviation: str, start_idx, end_idx):
    all_candidate = []
    clean_abbreviation = abbreviation

    # clean abbreviation
    for ch in ['/', '\\', ',', '.', '-', '_', '&']:
        if ch in clean_abbreviation:
            clean_abbreviation = clean_abbreviation.replace(ch, ' ')
    separate_abbre = []
    numbers = ''
    for i in range(len(clean_abbreviation)):
        if clean_abbreviation[i] == ' ':
            if len(numbers) > 0:
                separate_abbre.append(numbers)
                numbers = ''
            continue
        elif clean_abbreviation[i].isnumeric():
            numbers += clean_abbreviation[i]
            if i == len(clean_abbreviation)-1:
                separate_abbre.append(numbers)
                numbers = ''
        else:
            if len(numbers) > 0:
                separate_abbre.append(numbers)
                numbers = ''
            separate_abbre.append(clean_abbreviation[i])
    # print(separate_abbre)

    temp_candidates = []
    temp_sentence = []
    for i in range(len(separate_abbre)):
        abbre_char = separate_abbre[i]
        replace_char = replace_dict.get(abbre_char)
        stop_words = list(stopwords.words('english'))
        # print(f'{abbre_char}: {replace_char}')
        if i == 0:
            for j in range(start_idx, end_idx):
                # if arr_sentence[j].lower()[0] in stop_words:
                #     continue
                if abbre_char.lower() == arr_sentence[j].lower()[0]:
                    all_candidate.append([(j, 0)])
                    # print(all_candidate)
                if replace_char is not None and replace_char.lower() == arr_sentence[j].lower()[0]:
                    all_candidate.append([(j, 0)])
        elif len(all_candidate) > 0:
            for one in all_candidate:
                tmp_oneCandidate = one.copy()
                if len(one) == i:
                    last_flag = one[-1]
                    temp_sentence = arr_sentence.copy()
                    temp_sentence[last_flag[0]] = temp_sentence[last_flag[0]][
                                                  (last_flag[1] + len(separate_abbre[i - 1])):]
                    for m in range(last_flag[0], end_idx):
                        if m - last_flag[0] > 2:
                            break
                        else:
                            if abbre_char.lower() in temp_sentence[m].lower():
                                idxes = [e.start() for e in re.finditer(abbre_char.lower(), temp_sentence[m].lower())]
                                para = 1 if m == last_flag[0] else 0
                                for idx in idxes:
                                    tmp_oneCandidate.append(
                                        (m, idx + para * (last_flag[1] + len(separate_abbre[i - 1]))))
                                    temp_candidates.append(tmp_oneCandidate)
                                    tmp_oneCandidate = one.copy()
                            if replace_char is not None:
                                # print(replace_char)
                                if replace_char in temp_sentence[m].lower():
                                    idxes = [e.start() for e in
                                             re.finditer(replace_char.lower(), temp_sentence[m].lower())]
                                    para = 1 if m == last_flag[0] else 0
                                    for idx in idxes:
                                        tmp_oneCandidate.append(
                                            (m, idx + para * (last_flag[1] + len(separate_abbre[i - 1]))))
                                        temp_candidates.append(tmp_oneCandidate)
                                        tmp_oneCandidate = one.copy()
            if len(temp_candidates) == 0:
                all_candidate = []
                break
            else:
                all_candidate = temp_candidates.copy()
                temp_candidates = []
    return all_candidate
    # print(all_candidate)


def separate_sentence(sentence: str):
    clean_sentence = sentence
    char_to_replace = {'(': ' ',
                       ')': ' ',
                       '{': ' ',
                       '}': ' ',
                       '[': ' ',
                       ']': ' ',
                       ', ': ' ',
                       '; ': ' ',
                       '-': ' '}
    for key, value in char_to_replace.items():
        clean_sentence = clean_sentence.replace(key, value)
    arr_sentence = clean_sentence.split(' ')
    arr_sentence = list(filter(lambda a: a != '', arr_sentence))
    return arr_sentence


def generate_potential_definitions(sentence: str, abbreviation: str):
    abb_pattern = abbre_pattern(abbreviation)
    arr_sentence = separate_sentence(sentence)
    # print(arr_sentence)

    max_len = min(len(abb_pattern) + 5, len(abb_pattern) * 2)
    if abbreviation not in arr_sentence:
        return None, None
    idx_abb = arr_sentence.index(abbreviation)
    start_idx = (idx_abb - max_len) if (idx_abb - max_len) > 0 else 0
    end_idx = (idx_abb + max_len) if (idx_abb + max_len) < (len(arr_sentence) - 1) else (len(arr_sentence) - 1)
    # print(start_idx, idx_abb, end_idx)

    # find_shortest_candidate(arr_sentence, abbreviation, start_idx, idx_abb)
    # find_shortest_candidate(arr_sentence, abbreviation, idx_abb + 1, end_idx + 1)
    before_abb = find_all_candidate(arr_sentence, abbreviation, start_idx, idx_abb)
    after_abb = find_all_candidate(arr_sentence, abbreviation, idx_abb + 1, end_idx + 1)
    return before_abb, after_abb


def formationRules_and_definition_patterns(sentence: str, abbreviation: str, candidates: list):
    if len(candidates) == 0:
        return '', [], []
    else:
        abb_pattern = abbre_pattern(abbreviation)
        # print(abb_pattern)
        formation_rules = []
        def_patterns = []
        stop_words = list(stopwords.words('english'))
        arr_sentence = separate_sentence(sentence)
        for item in candidates:
            one_def = 'z'
            one_candidate_rule = []
            last_idx = -1
            for i in range(len(item)):
                if abb_pattern[i] == 'n':
                    one_candidate_rule.append((item[i][0], 'e'))
                    one_def += 'n'
                else:
                    if arr_sentence[item[i][0]] in stop_words:
                        one_def += 's'
                    else:
                        if last_idx != item[i][0]:
                            one_def += 'w'
                    tmp_n = item[i][1]
                    if tmp_n == 0:
                        one_candidate_rule.append((item[i][0], 'f'))
                    elif tmp_n < len(arr_sentence[item[i][0]]) - 1:
                        one_candidate_rule.append((item[i][0], 'i'))
                    elif tmp_n == len(arr_sentence[item[i][0]]) - 1:
                        one_candidate_rule.append((item[i][0], 'l'))
                last_idx = item[i][0]
            if one_def[1] != 's':
                formation_rules.append(one_candidate_rule)
                def_patterns.append(one_def[1:])
    return abb_pattern, formation_rules, def_patterns


def find_best_candidate(a_pattern: str, d_patterns: list, formation_rules: list):
    res = {}
    for i in range(len(d_patterns)):
        cons = 1
        len_abb = len(a_pattern)
        if len_abb == len(d_patterns[i]):
            cons = 1
        elif len_abb < len(d_patterns[i]):
            cons = 0.9
        elif len_abb > len(d_patterns[i]):
            cons = 0.8
        score = 0

        idx_list = []
        for item in formation_rules[i]:
            idx_list.append(item[0])
            if item[1] == 'f' or item[1] == 'e':
                score += 3
            elif item[1] == 'i':
                score += 2
            elif item[1] == 'l':
                score += 1
        res[i] = score * cons - np.var(idx_list)
    res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
    idx = list(res.keys())[0]
    return d_patterns[idx], formation_rules[idx], res[idx]


def find_definition(sentence: str, formation_rules: list):
    """

    :type formation_rules: object
    """
    # arr_sentence = separate_sentence(sentence)
    # res = arr_sentence[formation_rules[0][0]:(formation_rules[-1][0]+1)]
    #
    # output = ' '.join(res)
    # return output.replace('\n', ' ')

    arr_sentence = separate_sentence(sentence)
    start_word = arr_sentence[formation_rules[0][0]]
    end_word = arr_sentence[formation_rules[-1][0]]
    # print(start_word)
    # print(end_word)
    appearances_start = [i for i, x in enumerate(arr_sentence) if x == start_word]
    appearances_end = [i for i, x in enumerate(arr_sentence) if x == end_word]
    # print(arr_sentence)
    # print(appearances_start)
    # print(appearances_end)
    indexes_start = [idx for idx in range(len(sentence)) if sentence.startswith(start_word, idx)]
    indexes_end = [idx for idx in range(len(sentence)) if sentence.startswith(end_word, idx)]

    # print(indexes_start)
    # print(indexes_end)
    idx_start = indexes_start[appearances_start.index(formation_rules[0][0])]
    idx_end = indexes_end[appearances_end.index(formation_rules[-1][0])] + len(end_word) - 1
    # print(idx_start)
    # print(idx_end)
    # check if result misses content connected by hyphen or inside the brackets

    if sentence[idx_start - 1] == '-':
        for i in range(idx_start - 1, -1, -1):
            if sentence[i] != ' ':
                idx_start = i
            else:
                break

    if sentence[idx_end + 1] == '-':
        for i in range(idx_end + 1, len(sentence)):
            if sentence[i] != ' ':
                idx_end = i
            else:
                break

    start_bracket_counts = 0
    end_bracket_counts = 0
    for i in range(idx_start - 1, -1, -1):
        if sentence[i] == '(':
            start_bracket_counts -= 1
        elif sentence[i] == ')':
            start_bracket_counts += 1
        if start_bracket_counts == -1:
            idx_start = i + 1
            break

    for i in range(idx_end + 1, len(sentence)):
        if sentence[i] == '(':
            end_bracket_counts += 1
        elif sentence[i] == ')':
            end_bracket_counts -= 1
        if end_bracket_counts == -1:
            idx_end = i - 1
            break

    return sentence[idx_start:(idx_end + 1)].replace('\n', ' ').strip()


def complete_abbreviations(abbs: list, sentence: str):
    dic_abbTimes = {}
    new_abbs = abbs.copy()
    for abb in abbs:
        if dic_abbTimes.get(abb) is None:
            dic_abbTimes[abb] = 1
        else:
            dic_abbTimes[abb] += 1
    # print(dic_abbTimes)
    start_idx_list = []
    stops = [',', '.', ';']
    for abb in abbs:
        indexes_start = [idx for idx in range(len(sentence)) if sentence.startswith(abb, idx)]
        start_idx_list.append(indexes_start[len(indexes_start)-dic_abbTimes[abb]])
        dic_abbTimes[abb] -= 1
    for j in range(len(start_idx_list)):
        idx_start = start_idx_list[j]
        idx_end = idx_start + len(abbs[j]) - 1
        start_bracket_counts = 0
        end_bracket_counts = 0
        new_idx_start = idx_start
        new_idx_end = idx_end
        for n in range(idx_start - 1, max(idx_start - 20, -1), -1):
            if sentence[n] in stops:
                break
            if sentence[n] == '(':
                start_bracket_counts -= 1
            elif sentence[n] == ')':
                start_bracket_counts += 1
            if start_bracket_counts == -1:
                new_idx_start = n + 1
                break
        for n in range(idx_end + 1, min(len(sentence), idx_end + 20)):
            if sentence[n] in stops:
                break
            if sentence[n] == '(':
                end_bracket_counts += 1
            elif sentence[n] == ')':
                end_bracket_counts -= 1
            if end_bracket_counts == -1:
                new_idx_end = n - 1
                break
        if new_idx_end != idx_end or new_idx_start != idx_start:
            new_abbs[j] = sentence[new_idx_start:(new_idx_end + 1)].strip()
    return new_abbs


def Hybrid_definition_mining(sentence: str, abbreviation: str) -> object:
    ls_can1, ls_can2 = generate_potential_definitions(sentence, abbreviation)
    if ls_can2 is None and ls_can1 is None:
        return '', -1
    a1, formation_rules1, definition_patterns1 = formationRules_and_definition_patterns(sentence, abbreviation, ls_can1)
    a2, formation_rules2, definition_patterns2 = formationRules_and_definition_patterns(sentence, abbreviation, ls_can2)
    if len(formation_rules1) + len(formation_rules2) == 0:
        return '', -1
    def_pattern, form_rule, score= find_best_candidate(a1, (definition_patterns1 + definition_patterns2), (formation_rules1 + formation_rules2))
    res_str = find_definition(sentence, form_rule)
    if res_str == abbreviation:
        return '', -1
    return (res_str, round(score, 2))

#
# text = 'Briefly, the African American cohorts included the African American Diabetes Heart Study (AADHS; n = 531), the Atherosclerosis Risk in Communities (ARIC) study (n = 2658), the Bone Mineral Density in Childhood Study (BMDCS; n = 161), the Children’s Hospital of Philadelphia (CHOP) cohort (n = 379), the Cardiovascular Heart Study (CHS; n = 303), the Health, Aging and Body Composition (Health ABC) study (n = 981), Mount Sinai BioMe BioBank (n = 361), the Jackson Heart Study (JHS; n = 2132), and the Multi-Ethnic Study of Atherosclerosis (MESA; n = 1035).'
# re_letter = r'\b[A-Z](?:[-_.///a-z]?[A-Z0-9α-ωΑ-Ω])+[a-z]*\b'
# re_digit = r'\b[0-9](?:[-_.,:///]?[a-zA-Z0-9α-ωΑ-Ω])+[A-Z]{1}(?:[,:&_.-///]?[a-zA-Z0-9α-ωΑ-Ω])*\b'
# re_symble = r'[[α-ωΑ-Ω][0-9A-Z](?:[-_.///]?[A-Z0-9])+[]](?:[_&-.///]?[A-Z0-9])+\b'
# all_abb = []
# res = {}
# res1 = re2.findall(re_letter, text)
# res2 = re2.findall(re_digit, text)
# res3 = re2.findall(re_symble, text)
# if len(res1) + len(res2) + len(res3) > 0:
#     all_abb = list(set(res1 + res2 + res3))
# print(all_abb)
# new_abbs = complete_abbreviations(all_abb, text)
# print(new_abbs)
# for abb in new_abbs:
#     res[abb] = Hybrid_definition_mining(text, abb)
# for i in res.items():
#     print(i)


# # text = 'Two genomewide association study (GWAS) meta-analyses of 25(OH)D concentrations in populations of European ancestry have been conducted identifying loci including group-specific component (vitamin D binding protein) gene (GC), nicotinamide adenine dinucleotide synthetase 1 gene (NADSYN1)/7-dehydrocholesterol reductase gene (DHCR7), vitamin D 25-hydroxylase gene (CYP2R1), and vitamin D 24-hydroxylase gene (CYP24A1).'
# # abb1 = 'NADSYN1'
# # abb2 = 'DHCR7'
# text1 = "Finally, clinical studies also suggest that the antileukemic effects of ATRA could be detected, especially for patients with an altered expression of chromatin-modifying genes, MDS1 and EVI1 complex locus (MECOM) overexpression, nucleophosmin 1 (NPM1) mutations or isocitrate dehydrogenase (IDH) mutations with lysine demethylase 1A (KDM1A) deregulation [13,17]"
# abb1 = 'NPM1'
# text1 = 'ly caused by increased cyclin dependent kinase 1 and 2 (CDK1/2)'
# abb1 = 'CDK1/2'
# # print(Hybrid_definition_mining(text, abb1))
# # print(Hybrid_definition_mining(text, abb2))
# print(Hybrid_definition_mining(text1, abb1))
#
# #
# # text1 = 'arachidonic acid; ALA, α-linolenic acid, EPA, eicosapentaenoic acid; DHA, doco'
# # abb1 = 'ALA'
# #
# # # text1 = 's carcinoma cell line of human NPC cells, induced by 12-O-Tetradecanoyl-phorbol-13-acetate (TPA)'
# # # abb1 = 'TPA'
# #
# # print(Hybrid_definition_mining(text1, abb1))
# # print(separate_sentence(text1))
# #
# ls_can1, ls_can2 = generate_potential_definitions(text1, abb1)
# print(f'before the abbreviation: {ls_can1}')
# print(f'after the abbreviation: {ls_can2}')
#
# a, b, c = formationRules_and_definition_patterns(text1, abb1, ls_can1)
# a1, b1, c1 = formationRules_and_definition_patterns(text1, abb1, ls_can2)
# print(f'formation rules: {b}')
# print(f'definition patterns: {c}')
# print(f'formation rules: {b1}')
# print(f'definition patterns: {c1}')
# d, e = find_best_candidate(a, c, b)
# print(f'best candidate: {e}')
# res = find_definition(text1, e)
# print(f'final result: {res}')
# #
# # for i in range(len(b)):
# #     print(b[i])
# #     print(len(c[i]))
# #
# # zz = separate_sentence(text1)
# # print (zz)
#
#
# # text1 = 'Nasopharyngeal carcinoma (NPC), one of the most common cancers in population with Chinese or Asian progeny, poses a serious health problem for southern China'
# # abb1 = 'NPC'
# #
# # text2 = 'However, heat shock protein 70 (HSP70) and cytochrome P450 (CYP450) were expressed significantly and constantly only in LNM NPC patients'
# # abb2 = 'CYP450'
# #
# # text3 = 'performed protein chip profiling analysis with surface-enhanced laser desorption ionization time-of-flight mass spectrometry (SELDI-TOF-MS) technology on sera from NPC patients and demonstrated that SAA may be a potentially usefully biomarker for NPC [24]'
# # abb3 = 'SELDI-TOF-MS'


