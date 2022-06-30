from nltk.corpus import stopwords
import re


# nltk.download()
# st = set(stopwords.words('english'))
# print(len(st))

replace_dict = {'A': 'α', 'B': 'β'}

def abbre_pattern(abbreviation: str):
    pattern = 'w'
    for ch in ['/', '\\', ',', '.', '-', '_', '&']:
        if ch in abbreviation:
            abbreviation = abbreviation.replace(ch, '')
    for c in abbreviation:
        if c.isdigit() & (pattern[-1] == 'w'):
            pattern += 'n'
        elif not c.isdigit():
            pattern += 'w'
    return pattern[1:]


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
                print(f"start {one_def}")
                # print(one_def)
            else:
                continue
        while len(temp_abbre) != 0:
            temp_letter = temp_abbre[0]
            temp_word = temp_sentence[i]
            if temp_letter.lower() in temp_word.lower():
                one_def.append(i)
                print(f"processing {one_def}")
                temp_sentence[i] = temp_word[(temp_word.lower().index(temp_letter.lower()) + 1):]
                temp_abbre = temp_abbre[1:]
            else:
                break
    print(f"got one {one_def}")


def find_all_candidate(arr_sentence: list, abbreviation: str, start_idx, end_idx):
    all_candidate = []
    clean_abbreviation = abbreviation

    # clean abbreviation
    for ch in ['/', '\\', ',', '.', '-', '_', '&']:
        if ch in clean_abbreviation:
            clean_abbreviation = clean_abbreviation.replace(ch, '')
    separate_abbre = []
    numbers = ''
    for i in clean_abbreviation:
        if i.isnumeric():
            numbers += i
            if i == clean_abbreviation[-1]:
                separate_abbre.append(numbers)
                numbers = ''
        else:
            if len(numbers) > 0:
                separate_abbre.append(numbers)
                numbers = ''
            separate_abbre.append(i)
    # print(separate_abbre)

    temp_candidates = []
    temp_sentence = []
    for i in range(len(separate_abbre)):
        abbre_char = separate_abbre[i]
        replace_char = replace_dict.get(abbre_char)
        if i == 0:
            for j in range(start_idx, end_idx):
                if abbre_char.lower() == arr_sentence[j].lower()[0]:
                    all_candidate.append([(j, 0)])
                    # print(all_candidate)
        elif len(all_candidate) > 0:
            for one in all_candidate:
                tmp_oneCandidate = one.copy()
                if len(one) == i:
                    last_flag = one[-1]
                    temp_sentence = arr_sentence.copy()
                    temp_sentence[last_flag[0]] = temp_sentence[last_flag[0]][
                                                  (last_flag[1] + len(separate_abbre[i - 1])):]
                    for m in range(last_flag[0], end_idx):
                        if m - last_flag[0] > 3:
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
                                if replace_char in temp_sentence[m].lower():
                                    idxes = [e.start() for e in
                                             re.finditer(replace_char, temp_sentence[m].lower())]
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
    char_to_replace = {'(': '',
                       ')': '',
                       '{': '',
                       '}': '',
                       '[': '',
                       ']': '',
                       ', ': ' '}
    for key, value in char_to_replace.items():
        clean_sentence = clean_sentence.replace(key, value)
    arr_sentence = clean_sentence.split(' ')
    return arr_sentence


def generate_potential_definitions(sentence: str, abbreviation: str):
    abb_pattern = abbre_pattern(abbreviation)
    arr_sentence = separate_sentence(sentence)
    # print(arr_sentence)

    max_len = min(len(abb_pattern) + 5, len(abb_pattern) * 2)
    idx_abb = arr_sentence.index(abbreviation)
    start_idx = (idx_abb - max_len) if (idx_abb - max_len) > 0 else 0
    end_idx = (idx_abb + max_len) if (idx_abb + max_len) < (len(arr_sentence) - 1) else (len(arr_sentence) - 1)
    print(start_idx, idx_abb, end_idx)

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
        formation_rules = []
        def_patterns = []
        stop_words = list(stopwords.words('english'))
        arr_sentence = separate_sentence(sentence)
        for item in candidates:
            one_def = 'z'
            one_candidate_rule = []
            last_idx = -1
            for i in range(len(item)):
                if abb_pattern[i].isnumeric():
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
        for item in formation_rules[i]:
            if item[1] == 'f' or item[1] == 'e':
                score += 3
            elif item[1] == 'i':
                score += 2
            elif item[1] == 'l':
                score += 1
        res[i] = score * cons
    res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
    idx = list(res.keys())[0]
    return d_patterns[idx], formation_rules[idx]


def find_definition(sentence: str, formation_rules: list):
    arr_sentence = separate_sentence(sentence)
    res = arr_sentence[formation_rules[0][0]:(formation_rules[-1][0]+1)]

    return ' '.join(res)


def Hybrid_definition_mining(sentence: str, abbreviation: str):
    ls_can1, ls_can2 = generate_potential_definitions(sentence, abbreviation)
    a1, formation_rules1, definition_patterns1 = formationRules_and_definition_patterns(sentence, abbreviation, ls_can1)
    a2, formation_rules2, definition_patterns2 = formationRules_and_definition_patterns(sentence, abbreviation, ls_can2)
    if len(formation_rules1) + len(formation_rules2) == 0:
        return ''
    def_pattern, form_rule = find_best_candidate(a1, (definition_patterns1 + definition_patterns2), (formation_rules1 + formation_rules2))
    res_str = find_definition(sentence, form_rule)

    return res_str

text1 = 'Nasopharyngeal carcinoma (NPC), one of the most common cancers in population with Chinese or Asian progeny, poses a serious health problem for southern China'
abb1 = 'NPC'

text2 = 'However, heat shock protein 70 (HSP70) and cytochrome P450 (CYP450) were expressed significantly and constantly only in LNM NPC patients'
abb2 = 'CYP450'

text3 = 'performed protein chip profiling analysis with surface-enhanced laser desorption ionization time-of-flight mass spectrometry (SELDI-TOF-MS) technology on sera from NPC patients and demonstrated that SAA may be a potentially usefully biomarker for NPC [24]'
abb3 = 'SELDI-TOF-MS'

ls_can1, ls_can2 = generate_potential_definitions(text1, abb1)
print(f'before the abbreviation: {ls_can1}')
print(f'after the abbreviation: {ls_can2}')

a, b, c = formationRules_and_definition_patterns(text1, abb1, ls_can1)
a1, b1, c1 = formationRules_and_definition_patterns(text1, abb1, ls_can2)
print(f'formation rules: {b}')
print(f'definition patterns: {c}')
print(f'formation rules: {b1}')
print(f'definition patterns: {c1}')
d, e = find_best_candidate(a, c, b)
print(f'best candidate: {e}')
res = find_definition(text1, e)
print(f'final result: {res}')

for i in range(len(b)):
    print(b[i])
    print(len(c[i]))

zz = separate_sentence(text1)
print (zz)
