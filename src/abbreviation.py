import logging
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from Hybrid import Hybrid_definition_mining
import json
import copy
# import Hybrid

import regex as re2

# definitions_dict = {}

class abbreviations:

    def __yield_lines_from_doc(self, doc_text):
        for line in doc_text.split("."):
            yield line.strip()

    def __conditions(self, candidate):
        """
        Based on Schwartz&Hearst

        2 <= len(str) <= 10
        len(tokens) <= 2
        re.search(r'\p{L}', str)
        str[0].isalnum()

        and extra:
        if it matches (\p{L}\.?\s?){2,}
        it is a good candidate.

        :param candidate: candidate abbreviation
        :return: True if this is a good candidate
        """
        LF_in_parentheses = False
        viable = True
        if re2.match(r'(\p{L}\.?\s?){2,}', candidate.lstrip()):
            viable = True
        if len(candidate) < 2 or len(candidate) > 10:
            viable = False
        if len(candidate.split()) > 2:
            viable = False
            LF_in_parentheses = True  # customize funcition find LF in parentheses
        if candidate.islower():  # customize funcition discard all lower case candidate
            viable = False
        if not re2.search(r'\p{L}', candidate):  # \p{L} = All Unicode letter
            viable = False
        if not candidate[0].isalnum():
            viable = False

        return viable

    def __best_candidates(self, sentence):
        """
        :param sentence: line read from input file
        :return: a Candidate iterator
        """

        if '(' in sentence:
            # Check some things first
            if sentence.count('(') != sentence.count(')'):
                raise ValueError("Unbalanced parentheses: {}".format(sentence))

            if sentence.find('(') > sentence.find(')'):
                raise ValueError("First parentheses is right: {}".format(sentence))

            close_index = -1
            while 1:
                # Look for open parenthesis. Need leading whitespace to avoid matching mathematical and chemical formulae
                open_index = sentence.find(' (', close_index + 1)

                if open_index == -1: break

                # Advance beyond whitespace
                open_index += 1

                # Look for closing parentheses
                close_index = open_index + 1
                open_count = 1
                skip = False
                while open_count:
                    try:
                        char = sentence[close_index]
                    except IndexError:
                        # We found an opening bracket but no associated closing bracket
                        # Skip the opening bracket
                        skip = True
                        break
                    if char == '(':
                        open_count += 1
                    elif char in [')', ';', ':']:
                        open_count -= 1
                    close_index += 1

                if skip:
                    close_index = open_index + 1
                    continue

                # Output if conditions are met
                start = open_index + 1
                stop = close_index - 1
                candidate = sentence[start:stop]

                # Take into account whitespace that should be removed
                start = start + len(candidate) - len(candidate.lstrip())
                stop = stop - len(candidate) + len(candidate.rstrip())
                candidate = sentence[start:stop]
                # print (candidate)

                if self.__conditions(candidate):
                    new_candidate = Candidate(candidate)
                    new_candidate.set_position(start, stop)
                    yield new_candidate

    # elif LF_in_parentheses:

    def __get_definition(self, candidate, sentence):
        """
        Takes a candidate and a sentence and returns the definition candidate.

        The definition candidate is the set of tokens (in front of the candidate)
        that starts with a token starting with the first character of the candidate

        :param candidate: candidate abbreviation
        :param sentence: current sentence (single line from input file)
        :return: candidate definition for this abbreviation
        """
        # Take the tokens in front of the candidate
        tokens = re2.split(r'[\s\-]+', sentence[:candidate.start - 2].lower())
        # the char that we are looking for
        key = candidate[0].lower()

        # Count the number of tokens that start with the same character as the candidate
        first_chars = [t[0] for t in filter(None, tokens)]

        definition_freq = first_chars.count(key)
        candidate_freq = candidate.lower().count(key)

        # Look for the list of tokens in front of candidate that
        # have a sufficient number of tokens starting with key
        if candidate_freq <= definition_freq:
            # we should at least have a good number of starts
            count = 0
            start = 0
            start_index = len(first_chars) - 1
            while count < candidate_freq:
                if abs(start) > len(first_chars):
                    raise ValueError("candidate {} not found".format(candidate))
                start -= 1
                # Look up key in the definition
                try:
                    start_index = first_chars.index(key, len(first_chars) + start)
                except ValueError:
                    pass

                # Count the number of keys in definition
                count = first_chars[start_index:].count(key)

            # We found enough keys in the definition so return the definition as a definition candidate
            start = len(' '.join(tokens[:start_index]))
            stop = candidate.start - 1
            candidate = sentence[start:stop]

            # Remove whitespace
            start = start + len(candidate) - len(candidate.lstrip())
            stop = stop - len(candidate) + len(candidate.rstrip())
            candidate = sentence[start:stop]

            new_candidate = Candidate(candidate)
            new_candidate.set_position(start, stop)
            return new_candidate

        else:
            raise ValueError('There are less keys in the tokens in front of candidate than there are in the candidate')

    def __select_definition(self, definition, abbrev):
        """
        Takes a definition candidate and an abbreviation candidate
        and returns True if the chars in the abbreviation occur in the definition

        Based on
        A simple algorithm for identifying abbreviation definitions in biomedical texts, Schwartz & Hearst
        :param definition: candidate definition
        :param abbrev: candidate abbreviation
        :return:
        """

        if len(definition) < len(abbrev):
            raise ValueError('Abbreviation is longer than definition')

        if abbrev in definition.split():
            raise ValueError('Abbreviation is full word of definition')

        s_index = -1
        l_index = -1

        while 1:
            try:
                long_char = definition[l_index].lower()
            except IndexError:
                raise

            short_char = abbrev[s_index].lower()

            if not short_char.isalnum():
                s_index -= 1

            if s_index == -1 * len(abbrev):
                if short_char == long_char:
                    if l_index == -1 * len(definition) or not definition[l_index - 1].isalnum():
                        break
                    else:
                        l_index -= 1
                else:
                    l_index -= 1
                    if l_index == -1 * (len(definition) + 1):
                        raise ValueError("definition {} was not found in {}".format(abbrev, definition))

            else:
                if short_char == long_char:
                    s_index -= 1
                    l_index -= 1
                else:
                    l_index -= 1

        new_candidate = Candidate(definition[l_index:len(definition)])
        new_candidate.set_position(definition.start, definition.stop)
        definition = new_candidate

        tokens = len(definition.split())
        length = len(abbrev)

        if tokens > min([length + 5, length * 2]):
            raise ValueError("did not meet min(|A|+5, |A|*2) constraint")

        # Do not return definitions that contain unbalanced parentheses
        if definition.count('(') != definition.count(')'):
            raise ValueError("Unbalanced parentheses not allowed in a definition")

        return definition

    def __extract_abbreviation_definition_pairs(self, doc_text=None, most_common_definition=False,
                                                first_definition=False, all_definition=True):
        abbrev_map = dict()
        list_abbrev_map = defaultdict(list)
        counter_abbrev_map = dict()
        omit = 0
        written = 0
        sentence_iterator = enumerate(self.__yield_lines_from_doc(doc_text))

        collect_definitions = False
        if most_common_definition or first_definition or all_definition:
            collect_definitions = True

        for i, sentence in sentence_iterator:
            # Remove any quotes around potential candidate terms
            clean_sentence = re2.sub(r'([(])[\'"\p{Pi}]|[\'"\p{Pf}]([);:])', r'\1\2', sentence)
            try:
                for candidate in self.__best_candidates(clean_sentence):
                    try:
                        definition = self.__get_definition(candidate, clean_sentence)
                    except (ValueError, IndexError) as e:
                        self.log.debug("{} Omitting candidate {}. Reason: {}".format(i, candidate, e.args[0]))
                        omit += 1
                    else:
                        try:
                            definition = self.__select_definition(definition, candidate)
                        except (ValueError, IndexError) as e:
                            self.log.debug(
                                "{} Omitting definition {} for candidate {}. Reason: {}".format(i, definition,
                                                                                                candidate, e.args[0]))
                            omit += 1
                        else:
                            # Either append the current definition to the list of previous definitions ...
                            if collect_definitions:
                                list_abbrev_map[candidate].append(definition)
                            else:
                                # Or update the abbreviations map with the current definition
                                abbrev_map[candidate] = definition
                            written += 1
            except (ValueError, IndexError) as e:
                self.log.debug("{} Error processing sentence {}: {}".format(i, sentence, e.args[0]))
        self.log.debug("{} abbreviations detected and kept ({} omitted)".format(written, omit))

        # Return most common definition for each term
        if collect_definitions:
            if most_common_definition:
                # Return the most common definition for each term
                for k, v in list_abbrev_map.items():
                    counter_abbrev_map[k] = Counter(v).most_common(1)[0][0]
            elif first_definition:
                # Return the first definition for each term
                for k, v in list_abbrev_map.items():
                    counter_abbrev_map[k] = v
            elif all_definition:
                for k, v in list_abbrev_map.items():
                    counter_abbrev_map[k] = v
            return counter_abbrev_map

        # Or return the last encountered definition for each term
        return abbrev_map

    def __extract_abbreviation(self, main_text):
        pairs = self.__extract_abbreviation_definition_pairs(doc_text=main_text, most_common_definition=True)

        return pairs

    def __listToDict(self, lst):
        op = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
        return op

    def __abbre_table_to_dict(self, t):
        abbre_list = []
        rows = t.findAll("tr")
        for i in rows:
            elements = i.findAll(['td', 'th'])
            vals = [j.get_text() for j in elements]
            if len(vals) > 1:
                abbre_list += vals
        abbre_dict = self.__listToDict(abbre_list)
        return abbre_dict

    def __abbre_list_to_dict(self, t):
        abbre_list = []
        SF = t.findAll("dt")
        SF_list = [SF_word.get_text() for SF_word in SF]
        LF = t.findAll("dd")
        LF_list = [LF_word.get_text() for LF_word in LF]
        abbre_dict = dict(zip(SF_list, LF_list))
        return abbre_dict

    def __get_abbre_plain_text(self, soup_og):
        abbre_text = soup_og.get_text()
        abbre_list = abbre_text.split(';')
        list_lenth = len(abbre_list)
        return abbre_list, list_lenth

    def __get_abbre_dict_given_by_author(self, soup_og):
        header = soup_og.find_all('h2', recursive=True)
        abbre_dict = {}
        for number, element in enumerate(header):
            if re2.search('abbreviation', element.get_text(), re2.IGNORECASE):
                nearest_down_tag = element.next_element
                while nearest_down_tag:
                    tag_name = nearest_down_tag.name

                    # when abbre is table
                    if tag_name == 'table':
                        abbre_dict = self.__abbre_table_to_dict(nearest_down_tag)
                        break

                    # when abbre is list
                    elif tag_name == 'dl':
                        abbre_dict = self.__abbre_list_to_dict(nearest_down_tag)
                        break

                    # when abbre is plain text
                    elif tag_name == 'p':
                        abbre_list, list_lenth = self.__get_abbre_plain_text(nearest_down_tag)
                        if list_lenth <= 2:
                            nearest_down_tag = nearest_down_tag.next_element
                            continue
                        else:
                            for abbre_pair in abbre_list:
                                if len(abbre_pair.split(':')) == 2:
                                    abbre_dict.update({abbre_pair.split(':')[0]: abbre_pair.split(':')[1]})
                                elif len(abbre_pair.split(',')) == 2:
                                    abbre_dict.update({abbre_pair.split(',')[0]: abbre_pair.split(',')[1]})
                                elif len(abbre_pair.split(' ')) == 2:
                                    abbre_dict.update({abbre_pair.split(' ')[0]: abbre_pair.split(' ')[1]})
                            break

                    # search until next h2
                    elif tag_name == 'h2':
                        break
                    else:
                        nearest_down_tag = nearest_down_tag.next_element
        return abbre_dict

    def __get_abbreviations(self, main_text, soup, config):
        paragraphs = main_text['paragraphs']
        all_abbreviations = {}
        hybrid_all_abbreviations = {}
        para_num = 1
        for paragraph in paragraphs:
            maintext = paragraph['body']
            pairs = self.__extract_abbreviation(maintext)
            all_abbreviations.update(pairs)
            # hybrid method
            hybrid_pairs = self.__re_find_abbreviation2(maintext, para_num, hybrid_all_abbreviations)
            hybrid_all_abbreviations.update(hybrid_pairs)
            para_num += 1
        author_provided_abbreviations = self.__get_abbre_dict_given_by_author(soup)

        abbrev_json = {}
        Hybrid_scores = {}
        potential_abbreviations = {}
        # with open("hybridallabbrev_json.json", "w", encoding='utf8') as f:
        #     json.dump(hybrid_all_abbreviations, f, ensure_ascii=False)

        for key in author_provided_abbreviations.keys():
            abbrev_json[key] = {author_provided_abbreviations[key].replace("\n", " "): ["abbreviations section"]}
        for key in all_abbreviations:
            clean_def = all_abbreviations[key].replace("\n", " ")
            if key in abbrev_json:
                if clean_def in abbrev_json[key].keys():
                    abbrev_json[key][clean_def].append("fulltext")
                else:
                    abbrev_json[key][clean_def] = ["fulltext"]
            else:
                abbrev_json[key] = {clean_def: ["fulltext"]}

        for one_abb in hybrid_all_abbreviations:
            definitions = hybrid_all_abbreviations[one_abb]
            if definitions is None:
                print(one_abb)
                continue
            if len(definitions) == 1 and definitions[0][1] == -1:
                potential_abbreviations[one_abb] = 'Not Found Yet'
                continue
            Hybrid_scores[one_abb] = []
            if one_abb in abbrev_json:
                for definition_score in definitions:
                    if definition_score[1] == -1:
                        continue
                    Hybrid_scores[one_abb].append(definition_score)
                    if definition_score[0] in abbrev_json[one_abb].keys():
                        abbrev_json[one_abb][definition_score[0]].append("HybriDK+")
                    else:
                        abbrev_json[one_abb][definition_score[0]] = ["HybriDK+"]
            else:
                abbrev_json[one_abb] = {}
                for definition_score in definitions:
                    if definition_score[1] == -1:
                        continue
                    Hybrid_scores[one_abb].append(definition_score)
                    abbrev_json[one_abb][definition_score[0]] = ["HybriDK+"]
            # if "" in abbrev_json[one_abb].keys() and len(abbrev_json[one_abb].keys()) > 1:
            #     abbrev_json[one_abb].pop('')
            # if one_abb in abbrev_json:
            #     abbrev_json[one_abb]['Hybrid_method'] = hybrid_all_abbreviations[one_abb]
            # else:
            #     abbrev_json[one_abb] = {'Hybrid_method': hybrid_all_abbreviations[one_abb]}

        # abbrev_json['abbreviations_section'] = author_provided_abbreviations
        # abbrev_json['fulltext_algorithm'] = all_abbreviations
        # with open("Hybrid_scores.json", "w", encoding='utf8') as f:
        #     json.dump(Hybrid_scores, f, ensure_ascii=False)
        # with open("potential_abbreviations.json", "w", encoding='utf8') as f:
        #     json.dump(potential_abbreviations, f, ensure_ascii=False)

        return abbrev_json, Hybrid_scores, potential_abbreviations
        # return abbrev_json

    def __biocify_abbreviations(self, abbreviations, Hybrid_scores, potential_abbreviations, file_path):
        offset = 0
        template = {
            "source": "Auto-CORPus (abbreviations)",
            # "inputfile": file_path,
            "date": f'{datetime.today().strftime("%Y%m%d")}',
            "key": "autocorpus_abbreviations.key",
            "documents": [
                {
                    "id": Path(file_path).name.split(".")[0],
                    "inputfile": file_path,
                    "passages": []
                }
            ]
        }

        hybrid_template = copy.deepcopy(template)
        potentialAbb_template = copy.deepcopy(template)
        passages = template["documents"][0]["passages"]
        HybridScore_passages = hybrid_template["documents"][0]["passages"]
        potentialAbbre_passages = potentialAbb_template["documents"][0]["passages"]

        for short in abbreviations.keys():
            counter = 1
            shortTemplate = {
                "text_short": short
            }
            for long in abbreviations[short].keys():
                # if long == 'Hybrid_method':
                #     for definition in abbreviations[short][long]:
                #         shortTemplate[F"text_long_{counter}"] = definition
                #         shortTemplate[F"extraction_algorithm_{counter}"] = ", ".join(abbreviations[short][long])
                #     continue
                shortTemplate[F"text_long_{counter}"] = long.replace("\n", " ")
                shortTemplate[F"extraction_algorithm_{counter}"] = ", ".join(abbreviations[short][long])
                counter += 1
            passages.append(shortTemplate)

        for short in Hybrid_scores.keys():
            counter = 1
            score_shortTemplate = {
                "text_short": short
            }
            for long in Hybrid_scores[short]:
                score_shortTemplate[F"text_long_{counter}"] = long[0]
                score_shortTemplate[F"Hybrid_score_{counter}"] = long[1]
                counter += 1
            HybridScore_passages.append(score_shortTemplate)

        for short in potential_abbreviations.keys():
            counter = 1
            potential_shortTemplate = {
                "text_short": short,
                "text_long": potential_abbreviations[short]
            }
            # for long in potential_abbreviations[short]:
            #     potential_shortTemplate[F"text_long_{counter}"] = long[0]
            #     counter += 1
            potentialAbbre_passages.append(potential_shortTemplate)

        return template, hybrid_template, potentialAbb_template
        # return template

    def __init__(self, main_text, soup, config, file_path):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        self.log = logging.getLogger(__name__)
        abbrev_json, Hybrid_scores, potential_abbreviations = self.__get_abbreviations(main_text, soup, config)
        self.abbreviations, self.Hybrid_scores, self.potential_abbres = self.__biocify_abbreviations(abbrev_json, Hybrid_scores, potential_abbreviations, file_path)
        # self.abbreviations = self.__wh_findabbrev(self.__wh_getabbrev(main_text, soup, config), file_path)
        pass

    def to_dict(self):
        return self.abbreviations

    def get_hybrid_scores(self):
        return self.Hybrid_scores

    def get_potential_abbres(self):
        return self.potential_abbres

    def __wh_findabbrev(self, abbreviations, file_path):
        offset = 0
        template = {
            "source": "Auto-CORPus (abbreviations)",
            # "inputfile": file_path,
            "date": f'{datetime.today().strftime("%Y%m%d")}',
            "key": "autocorpus_abbreviations.key",
            "documents": [
                {
                    "id": Path(file_path).name.split(".")[0],
                    "inputfile": file_path,
                    "passages": []
                }
            ]
        }
        passages = template["documents"][0]["passages"]
        # for short in abbreviations.keys():
        #     counter = 1
        #     shortTemplate = {
        #         "text_short": short
        #     }
        #     for long in abbreviations[short].keys():
        #         shortTemplate[F"text_long_{counter}"] = long.replace("\n", " ")
        #         shortTemplate[F"extraction_algorithm_{counter}"] = ", ".join(abbreviations[short][long])
        #         counter += 1
        #     passages.append(shortTemplate)
        for pos in abbreviations.keys():
            counter = 1
            shortTemplate = {
                "position": pos
            }
            for re_format in abbreviations[pos].keys():
                shortTemplate[re_format] = abbreviations[pos][re_format]
            passages.append(shortTemplate)
        return template

    def __wh_getabbrev(self, main_text, soup, config):
        paragraphs = main_text['paragraphs']
        all_abbreviations = {}
        para_num = 1
        definition_dict = {}
        for paragraph in paragraphs:
            maintext = paragraph['body']
            pairs = self.__re_find_abbreviation(maintext, para_num, definition_dict)
            all_abbreviations.update(pairs)
            para_num += 1
        return all_abbreviations

    def __re_find_abbreviation(self, main_text, para_num, definition_dict):
        re_letter = r'\b[A-Z](?:[-_.///a-z]?[A-Z0-9α-ωΑ-Ω])+[a-z]*\b'
        re_digit = r'\b[0-9](?:[-_.,:///]?[a-zA-Z0-9α-ωΑ-Ω])+[A-Z]{1}(?:[,:&_.-///]?[a-zA-Z0-9α-ωΑ-Ω])*\b'
        re_symble = r'[[α-ωΑ-Ω][0-9A-Z](?:[-_.///]?[A-Z0-9])+[]](?:[_&-.///]?[A-Z0-9])+\b'

        res = {}
        sentence_iterator = enumerate(self.__yield_lines_from_doc(main_text))
        for i, sentence in sentence_iterator:
            res1 = re2.findall(re_letter, sentence)
            res2 = re2.findall(re_digit, sentence)
            res3 = re2.findall(re_symble, sentence)
            if len(res1) + len(res2) + len(res3) > 0:
                all_abb = list(set(res1 + res2 + res3))
                temp = {'sentence': sentence, 'all': all_abb}
                # print(all_abb)
                for abbre in all_abb:
                    previously_found = definition_dict.get(abbre)
                    (definition, score) = Hybrid_definition_mining(sentence, abbre)
                    if previously_found is None:
                        # print(abbre)
                        temp[abbre] = definition
                        if definition != "":
                            definition_dict[abbre] = [definition]
                    else:
                        # if definition != "" and definition is not None and definition not in previously_found:
                        if definition != "" and definition not in previously_found:
                            previously_found = previously_found.append(definition)
                            definition_dict[abbre] = previously_found
                        temp[abbre] = previously_found if previously_found is not None else 'Not found'
                        # temp[abbre] = definition

                # print(temp)
                res[f'paragraph{para_num}_sentence{i}'] = temp
        return res

    def __re_find_abbreviation2(self, main_text, para_num, definition_dict):
        re_letter = r'\b[A-Z](?:[-_.///a-z]?[A-Z0-9α-ωΑ-Ω])+[a-z]*\b'
        re_digit = r'\b[0-9](?:[-_.,:///]?[a-zA-Z0-9α-ωΑ-Ω])+[A-Z]{1}(?:[,:&_.-///]?[a-zA-Z0-9α-ωΑ-Ω])*\b'
        re_symble = r'[[α-ωΑ-Ω][0-9A-Z](?:[-_.///]?[A-Z0-9])+[]](?:[_&-.///]?[A-Z0-9])+\b'

        temp = {}
        sentence_iterator = enumerate(self.__yield_lines_from_doc(main_text))
        for i, sentence in sentence_iterator:
            res1 = re2.findall(re_letter, sentence)
            res2 = re2.findall(re_digit, sentence)
            res3 = re2.findall(re_symble, sentence)
            if len(res1) + len(res2) + len(res3) > 0:
                all_abb = list(set(res1 + res2 + res3))
                # print(all_abb)
                for abbre in all_abb:
                    previously_found = definition_dict.get(abbre)
                    definition_score_tuple = Hybrid_definition_mining(sentence, abbre)
                    # if abbre == 'NIBIB':
                    #     print(definition_score_tuple)
                    #     print(previously_found)
                    if temp.get(abbre) is not None:
                        if definition_score_tuple not in temp[abbre]:
                            temp[abbre].append(definition_score_tuple)
                    elif previously_found is None:
                        # print(abbre)
                        temp[abbre] = [definition_score_tuple]
                    else:
                        if definition_score_tuple not in previously_found:
                            previously_found.append(definition_score_tuple)
                            temp[abbre] = previously_found
                        # temp[abbre] = definition
        return temp


class Candidate(str):
    def __init__(self, value):
        super().__init__()
        self.start = 0
        self.stop = 0

    def set_position(self, start, stop):
        self.start = start
        self.stop = stop

# -------------------------------------------------------------------

# import json
#
# import numpy as np
# from nltk.corpus import stopwords
# import re
#
#
# # nltk.download()
# # st = set(stopwords.words('english'))
# # print(len(st))
#
# # replace_dict = {'A': 'α', 'B': 'β', '1': 'one', '2': 'two', '3': 'three'}
#
#
# def save_replacement_file(replace_dict:dict):
#     with open("Auto-CORPus/src/replacement_dictionary.json", "w", encoding='utf8') as f:
#         json.dump(replace_dict, f, ensure_ascii=False)
#
#
# def read_replacement_file():
#     with open("src/replacement_dictionary.json", "r", encoding='utf8') as f:
#         result = json.loads(f.read())
#     return result
#
#
# replace_dict = read_replacement_file()
#
#
# def abbre_pattern(abbreviation: str):
#     pattern = 'w'
#     for ch in ['/', '\\', ',', '.', '-', '_', '&']:
#         if ch in abbreviation:
#             abbreviation = abbreviation.replace(ch, '')
#     for c in abbreviation:
#         if c.isdigit() & (pattern[-1] == 'w'):
#             pattern += 'n'
#         elif not c.isdigit():
#             pattern += 'w'
#     return pattern[1:]
#
#
# def find_shortest_candidate(arr_sentence: list, abbreviation: str, start_idx, end_idx):
#     one_def = []
#     temp_sentence = arr_sentence.copy()
#     temp_abbre = abbreviation
#     for i in range(start_idx, end_idx):
#         if len(one_def) == 0:
#             if temp_sentence[i][0].lower() == temp_abbre[0].lower():
#                 temp_sentence[i] = temp_sentence[i][1:]
#                 temp_abbre = temp_abbre[1:]
#                 one_def.append(i)
#                 # print(f"start {one_def}")
#                 # print(one_def)
#             else:
#                 continue
#         while len(temp_abbre) != 0:
#             temp_letter = temp_abbre[0]
#             temp_word = temp_sentence[i]
#             if temp_letter.lower() in temp_word.lower():
#                 one_def.append(i)
#                 # print(f"processing {one_def}")
#                 temp_sentence[i] = temp_word[(temp_word.lower().index(temp_letter.lower()) + 1):]
#                 temp_abbre = temp_abbre[1:]
#             else:
#                 break
#     print(f"got one {one_def}")
#
#
# def find_all_candidate(arr_sentence: list, abbreviation: str, start_idx, end_idx):
#     all_candidate = []
#     clean_abbreviation = abbreviation
#
#     # clean abbreviation
#     for ch in ['/', '\\', ',', '.', '-', '_', '&']:
#         if ch in clean_abbreviation:
#             clean_abbreviation = clean_abbreviation.replace(ch, '')
#     separate_abbre = []
#     numbers = ''
#     for i in range(len(clean_abbreviation)):
#         if clean_abbreviation[i].isnumeric():
#             numbers += clean_abbreviation[i]
#             if i == len(clean_abbreviation)-1:
#                 separate_abbre.append(numbers)
#                 numbers = ''
#         else:
#             if len(numbers) > 0:
#                 separate_abbre.append(numbers)
#                 numbers = ''
#             separate_abbre.append(clean_abbreviation[i])
#     # print(separate_abbre)
#
#     temp_candidates = []
#     temp_sentence = []
#     for i in range(len(separate_abbre)):
#         abbre_char = separate_abbre[i]
#         replace_char = replace_dict.get(abbre_char)
#         # print(f'{abbre_char}: {replace_char}')
#         if i == 0:
#             for j in range(start_idx, end_idx):
#                 if abbre_char.lower() == arr_sentence[j].lower()[0]:
#                     all_candidate.append([(j, 0)])
#                     # print(all_candidate)
#                 if replace_char is not None and replace_char.lower() == arr_sentence[j].lower()[0]:
#                     all_candidate.append([(j, 0)])
#         elif len(all_candidate) > 0:
#             for one in all_candidate:
#                 tmp_oneCandidate = one.copy()
#                 if len(one) == i:
#                     last_flag = one[-1]
#                     temp_sentence = arr_sentence.copy()
#                     temp_sentence[last_flag[0]] = temp_sentence[last_flag[0]][
#                                                   (last_flag[1] + len(separate_abbre[i - 1])):]
#                     for m in range(last_flag[0], end_idx):
#                         if m - last_flag[0] > 2:
#                             break
#                         else:
#                             if abbre_char.lower() in temp_sentence[m].lower():
#                                 idxes = [e.start() for e in re.finditer(abbre_char.lower(), temp_sentence[m].lower())]
#                                 para = 1 if m == last_flag[0] else 0
#                                 for idx in idxes:
#                                     tmp_oneCandidate.append(
#                                         (m, idx + para * (last_flag[1] + len(separate_abbre[i - 1]))))
#                                     temp_candidates.append(tmp_oneCandidate)
#                                     tmp_oneCandidate = one.copy()
#                             if replace_char is not None:
#                                 # print(replace_char)
#                                 if replace_char in temp_sentence[m].lower():
#                                     idxes = [e.start() for e in
#                                              re.finditer(replace_char.lower(), temp_sentence[m].lower())]
#                                     para = 1 if m == last_flag[0] else 0
#                                     for idx in idxes:
#                                         tmp_oneCandidate.append(
#                                             (m, idx + para * (last_flag[1] + len(separate_abbre[i - 1]))))
#                                         temp_candidates.append(tmp_oneCandidate)
#                                         tmp_oneCandidate = one.copy()
#             if len(temp_candidates) == 0:
#                 all_candidate = []
#                 break
#             else:
#                 all_candidate = temp_candidates.copy()
#                 temp_candidates = []
#     return all_candidate
#     # print(all_candidate)
#
#
# def separate_sentence(sentence: str):
#     clean_sentence = sentence
#     char_to_replace = {'(': ' ',
#                        ')': ' ',
#                        '{': ' ',
#                        '}': ' ',
#                        '[': ' ',
#                        ']': ' ',
#                        ', ': ' ',
#                        '; ': ' ',
#                        '-': ' '}
#     for key, value in char_to_replace.items():
#         clean_sentence = clean_sentence.replace(key, value)
#     arr_sentence = clean_sentence.split(' ')
#     arr_sentence = list(filter(lambda a: a != '', arr_sentence))
#     return arr_sentence
#
#
# def generate_potential_definitions(sentence: str, abbreviation: str):
#     abb_pattern = abbre_pattern(abbreviation)
#     arr_sentence = separate_sentence(sentence)
#     # print(arr_sentence)
#
#     max_len = min(len(abb_pattern) + 5, len(abb_pattern) * 2)
#     if abbreviation not in arr_sentence:
#         return None, None
#     idx_abb = arr_sentence.index(abbreviation)
#     start_idx = (idx_abb - max_len) if (idx_abb - max_len) > 0 else 0
#     end_idx = (idx_abb + max_len) if (idx_abb + max_len) < (len(arr_sentence) - 1) else (len(arr_sentence) - 1)
#     # print(start_idx, idx_abb, end_idx)
#
#     # find_shortest_candidate(arr_sentence, abbreviation, start_idx, idx_abb)
#     # find_shortest_candidate(arr_sentence, abbreviation, idx_abb + 1, end_idx + 1)
#     before_abb = find_all_candidate(arr_sentence, abbreviation, start_idx, idx_abb)
#     after_abb = find_all_candidate(arr_sentence, abbreviation, idx_abb + 1, end_idx + 1)
#     return before_abb, after_abb
#
#
# def formationRules_and_definition_patterns(sentence: str, abbreviation: str, candidates: list):
#     if len(candidates) == 0:
#         return '', [], []
#     else:
#         abb_pattern = abbre_pattern(abbreviation)
#         formation_rules = []
#         def_patterns = []
#         stop_words = list(stopwords.words('english'))
#         arr_sentence = separate_sentence(sentence)
#         for item in candidates:
#             one_def = 'z'
#             one_candidate_rule = []
#             last_idx = -1
#             for i in range(len(item)):
#                 if abb_pattern[i] == 'n':
#                     one_candidate_rule.append((item[i][0], 'e'))
#                     one_def += 'n'
#                 else:
#                     if arr_sentence[item[i][0]] in stop_words:
#                         one_def += 's'
#                     else:
#                         if last_idx != item[i][0]:
#                             one_def += 'w'
#                     tmp_n = item[i][1]
#                     if tmp_n == 0:
#                         one_candidate_rule.append((item[i][0], 'f'))
#                     elif tmp_n < len(arr_sentence[item[i][0]]) - 1:
#                         one_candidate_rule.append((item[i][0], 'i'))
#                     elif tmp_n == len(arr_sentence[item[i][0]]) - 1:
#                         one_candidate_rule.append((item[i][0], 'l'))
#                 last_idx = item[i][0]
#             formation_rules.append(one_candidate_rule)
#             def_patterns.append(one_def[1:])
#     return abb_pattern, formation_rules, def_patterns
#
#
# def find_best_candidate(a_pattern: str, d_patterns: list, formation_rules: list):
#     res = {}
#     for i in range(len(d_patterns)):
#         cons = 1
#         len_abb = len(a_pattern)
#         if len_abb == len(d_patterns[i]):
#             cons = 1
#         elif len_abb < len(d_patterns[i]):
#             cons = 0.9
#         elif len_abb > len(d_patterns[i]):
#             cons = 0.8
#         score = 0
#
#         idx_list = []
#         for item in formation_rules[i]:
#             idx_list.append(item[0])
#             if item[1] == 'f' or item[1] == 'e':
#                 score += 3
#             elif item[1] == 'i':
#                 score += 2
#             elif item[1] == 'l':
#                 score += 1
#         res[i] = score * cons - np.var(idx_list)
#     res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
#     idx = list(res.keys())[0]
#     return d_patterns[idx], formation_rules[idx]
#
#
# def find_definition(sentence: str, formation_rules: list):
#     """
#
#     :type formation_rules: object
#     """
#     # arr_sentence = separate_sentence(sentence)
#     # res = arr_sentence[formation_rules[0][0]:(formation_rules[-1][0]+1)]
#     #
#     # return ' '.join(res)
#
#     arr_sentence = separate_sentence(sentence)
#     start_word = arr_sentence[formation_rules[0][0]]
#     end_word = arr_sentence[formation_rules[-1][0]]
#     appearances_start = [i for i, x in enumerate(arr_sentence) if x == start_word]
#     appearances_end = [i for i, x in enumerate(arr_sentence) if x == end_word]
#     indexes_start = [idx for idx in range(len(sentence)) if sentence.startswith(start_word, idx)]
#     indexes_end = [idx for idx in range(len(sentence)) if sentence.startswith(end_word, idx)]
#     idx_start = indexes_start[appearances_start.index(formation_rules[0][0])]
#     idx_end = indexes_end[appearances_end.index(formation_rules[-1][0])] + len(end_word) - 1
#
#     # check if result misses content connected by hyphen or inside the brackets
#
#     if sentence[idx_start - 1] == '-':
#         for i in range(idx_start - 1, -1, -1):
#             if sentence[i] != ' ':
#                 idx_start = i
#             else:
#                 break
#
#     if sentence[idx_end + 1] == '-':
#         for i in range(idx_end + 1, len(sentence)):
#             if sentence[i] != ' ':
#                 idx_end = i
#             else:
#                 break
#
#     start_bracket_counts = 0
#     end_bracket_counts = 0
#     for i in range(idx_start - 1, -1, -1):
#         if sentence[i] == '(':
#             start_bracket_counts -= 1
#         elif sentence[i] == ')':
#             start_bracket_counts += 1
#         if start_bracket_counts == -1:
#             idx_start = i + 1
#             break
#
#     for i in range(idx_end + 1, len(sentence)):
#         if sentence[i] == '(':
#             end_bracket_counts += 1
#         elif sentence[i] == ')':
#             end_bracket_counts -= 1
#         if end_bracket_counts == -1:
#             idx_end = i - 1
#             break
#
#     return sentence[idx_start:(idx_end + 1)]
#
#
# def Hybrid_definition_mining(sentence: str, abbreviation: str):
#     ls_can1, ls_can2 = generate_potential_definitions(sentence, abbreviation)
#     if ls_can2 is None and ls_can1 is None:
#         return ''
#     a1, formation_rules1, definition_patterns1 = formationRules_and_definition_patterns(sentence, abbreviation, ls_can1)
#     a2, formation_rules2, definition_patterns2 = formationRules_and_definition_patterns(sentence, abbreviation, ls_can2)
#     if len(formation_rules1) + len(formation_rules2) == 0:
#         return ''
#     def_pattern, form_rule = find_best_candidate(a1, (definition_patterns1 + definition_patterns2), (formation_rules1 + formation_rules2))
#     res_str = find_definition(sentence, form_rule)
#
#     return res_str