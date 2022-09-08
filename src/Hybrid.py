import json

import numpy as np
# from nltk.corpus import stopwords
import re



def save_replacement_file(replace_dict: dict):
    with open("Auto-CORPus/src/replacement_dictionary.json", "w", encoding='utf8') as f:
        json.dump(replace_dict, f, ensure_ascii=False)


def read_replacement_file():
    # with open("Auto-CORPus/src/replacement_dictionary.json", "r", encoding='utf8') as f:
    with open("src/replacement_dictionary.json", "r", encoding='utf8') as f:
        result = json.loads(f.read())
    return result


def read_stopwords():
    stop_words = []
    with open("src/stop_words.txt", "r") as f:
        for line in f:
            stop_words.append(line.strip())
    return stop_words


replace_dict = read_replacement_file()
stop_words = read_stopwords()


def abbre_pattern(abbreviation: str):
    pattern = 'w'
    for ch in ['/', '\\', ',', '.', '-', '_', '&', '+']:
        if ch in abbreviation:
            abbreviation = abbreviation.replace(ch, ' ').strip()
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
            else:
                continue
        while len(temp_abbre) != 0:
            temp_letter = temp_abbre[0]
            temp_word = temp_sentence[i]
            if temp_letter.lower() in temp_word.lower():
                one_def.append(i)
                temp_sentence[i] = temp_word[(temp_word.lower().index(temp_letter.lower()) + 1):]
                temp_abbre = temp_abbre[1:]
            else:
                break


def find_all_candidate(arr_sentence: list, abbreviation: str, start_idx, end_idx):
    all_candidate = []
    clean_abbreviation = abbreviation

    for ch in ['/', '\\', ',', '.', '-', '_', '&', '+']:
        if ch in clean_abbreviation:
            clean_abbreviation = clean_abbreviation.replace(ch, ' ').strip()
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
            if i == len(clean_abbreviation) - 1:
                separate_abbre.append(numbers)
                numbers = ''
        else:
            if len(numbers) > 0:
                separate_abbre.append(numbers)
                numbers = ''
            separate_abbre.append(clean_abbreviation[i])

    temp_candidates = []
    temp_sentence = []
    for i in range(len(separate_abbre)):
        abbre_char = separate_abbre[i]
        replace_char = replace_dict.get(abbre_char)
        # stop_words = list(stopwords.words('english'))
        if i == 0:
            for j in range(start_idx, end_idx):
                if abbre_char.isnumeric() and arr_sentence[j].lower():
                    all_candidate.append([(j, -1)])
                elif abbre_char.lower() == arr_sentence[j].lower()[0]:
                    all_candidate.append([(j, 0)])
                elif replace_char is not None and replace_char.lower() == arr_sentence[j].lower()[0]:
                    all_candidate.append([(j, -2)])
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


def separate_sentence(sentence: str, abbre: str):
    tmp_sen = sentence.replace(abbre, '<<FLAG>>')
    char_to_replace = {'(': ' ',
                       ')': ' ',
                       '{': ' ',
                       '}': ' ',
                       '[': ' ',
                       ']': ' ',
                       ', ': ' ',
                       '; ': ' ',
                       '-': ' ',
                       '+': ' ',
                       '_': ' ',
                       ',': ' ',
                       '‐': ' '}
    for key, value in char_to_replace.items():
        tmp_sen = tmp_sen.replace(key, value)
    arr_sentence = tmp_sen.split(' ')
    arr_sentence = list(filter(lambda a: a != '', arr_sentence))
    new_arr_sentence = []
    for item in arr_sentence:
        if '<<FLAG>>' == item:
            new_arr_sentence.append(abbre)
            continue
        elif '<<FLAG>>' in item:
            item = item.replace('<<FLAG>>', abbre)
        match = re.match(r"([^0-9]+)([0-9]+)", item, re.I)
        if match:
            new_arr_sentence.extend(match.groups())
        else:
            new_arr_sentence.append(item)
    return new_arr_sentence


def generate_potential_definitions(sentence: str, abbreviation: str):
    abb_pattern = abbre_pattern(abbreviation)
    arr_sentence = separate_sentence(sentence, abbreviation)

    max_len = min(len(abb_pattern) + 5, len(abb_pattern) * 2)
    if abbreviation not in arr_sentence:
        return None, None
    idx_abb = arr_sentence.index(abbreviation)
    start_idx = (idx_abb - max_len) if (idx_abb - max_len) > 0 else 0
    end_idx = (idx_abb + max_len) if (idx_abb + max_len) < (len(arr_sentence) - 1) else (len(arr_sentence) - 1)

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
        arr_sentence = separate_sentence(sentence, abbreviation)
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
                    elif 0 < tmp_n < len(arr_sentence[item[i][0]]) - 1:
                        one_candidate_rule.append((item[i][0], 'i'))
                    elif tmp_n == len(arr_sentence[item[i][0]]) - 1:
                        one_candidate_rule.append((item[i][0], 'l'))
                    elif tmp_n == -1:
                        one_candidate_rule.append((item[i][0], 'e'))
                    elif tmp_n == -2:
                        one_candidate_rule.append((item[i][0], 'r'))
                last_idx = item[i][0]
            if one_def[1] != 's':
                formation_rules.append(one_candidate_rule)
                def_patterns.append(one_def[1:])
    return abb_pattern, formation_rules, def_patterns


def find_best_candidate(a_pattern: str, d_patterns: list, formation_rules: list, sentence: str, abbreviation: str):
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
            elif item[1] == 'r':
                score += 2.5
            elif item[1] == 'i':
                score += 2
            elif item[1] == 'l':
                score += 1
        res[i] = score * cons - np.var(idx_list)
    res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
    definition = ''
    score = -1
    for key in res.keys():
        tmp_definition = find_definition(sentence, formation_rules[key], abbreviation)
        # print(key)
        # print(tmp_definition)
        if tmp_definition in abbreviation or abbreviation in tmp_definition:
            continue
        else:
            score = res[key]
            definition = tmp_definition
            break
    return definition, score


def find_definition(sentence: str, formation_rules: list, abbre: str):
    """

    :type formation_rules: object
    """

    arr_sentence = separate_sentence(sentence, abbre)
    abbreviation_idx = [i for i, e in enumerate(arr_sentence) if e == abbre]
    start_word = arr_sentence[formation_rules[0][0]]
    end_word = arr_sentence[formation_rules[-1][0]]
    appearances_start = [i for i, x in enumerate(arr_sentence) if x == start_word]
    appearances_end = [i for i, x in enumerate(arr_sentence) if x == end_word]
    tmp_indexes_start = [idx for idx in range(len(sentence)) if sentence.startswith(start_word, idx)]
    tmp_indexes_end = [idx for idx in range(len(sentence)) if sentence.startswith(end_word, idx)]
    min_start_idx = len(''.join(arr_sentence[0:max(appearances_start[0], 0)]))
    min_end_idx = len(''.join(arr_sentence[0:max(appearances_end[0], 0)]))
    indexes_start = [i for i in tmp_indexes_start if i >= min_start_idx]
    indexes_end = [i for i in tmp_indexes_end if i >= min_end_idx]
    idx_start = indexes_start[appearances_start.index(formation_rules[0][0])]
    idx_end = indexes_end[appearances_end.index(formation_rules[-1][0])] + len(end_word) - 1
    # check if result misses content connected by hyphen or inside the brackets

    if idx_start - 1 > -1:
        if sentence[idx_start - 1] == '-':
            for i in range(idx_start - 1, -1, -1):
                if sentence[i] != ' ':
                    idx_start = i
                else:
                    break

    if idx_end + 1 < len(sentence):
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

    output = sentence[idx_start:(idx_end + 1)].replace('\n', ' ').strip()
    if output != '':
        return output
    else:
        words = arr_sentence[formation_rules[0][0]:(formation_rules[-1][0] + 1)]
        output = ' '.join(words).replace('\n', ' ').strip()
        return output


def complete_abbreviations(abbs: list, sentence: str):
    dic_abbTimes = {}
    new_abbs = abbs.copy()
    for abb in abbs:
        if dic_abbTimes.get(abb) is None:
            dic_abbTimes[abb] = 1
        else:
            dic_abbTimes[abb] += 1
    start_idx_list = []
    stops = [',', '.', ';']
    for abb in abbs:
        indexes_start = [idx for idx in range(len(sentence)) if sentence.startswith(abb, idx)]
        start_idx_list.append(indexes_start[len(indexes_start) - dic_abbTimes[abb]])
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
    res_str, score = find_best_candidate(a1, (definition_patterns1 + definition_patterns2),
                                         (formation_rules1 + formation_rules2), sentence, abbreviation)
    return (res_str, round(score, 2))
