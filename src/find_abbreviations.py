from abbreviation import abbreviations
from section import section
from table import table
import autoCORPus

def __extract_text(self, soup, config):
    """
    convert beautiful soup object into a python dict object with cleaned main text body

    Args:
        soup: BeautifulSoup object of html

    Return:
        result: dict of the maintext
    """
    result = {}

    # Tags of text body to be extracted are hard-coded as p (main text) and span (keywords and refs)
    body_select_tag = 'p,span,a'

    # Extract title
    # try:
    # 	h1 = soup.find(config['title']['name'],
    # 	               config['title']['attrs']).get_text().strip('/n')
    # except:
    # 	h1 = ''
    result['title'] = self.__get_title(soup, config)
    maintext = self.__get_keywords(soup, config) if self.__get_keywords(soup, config) else []
    sections = self.__get_sections(soup, config)
    # sections = [x['node'] for x in sections]
    for sec in sections:
        maintext.extend(section(config, sec).to_dict())
    # filter out the sections which do not contain any info
    filteredText = []
    [filteredText.append(x) for x in maintext if x]
    uniqueText = []
    seen_text = []
    for text in filteredText:
        if text['body'] not in seen_text:
            seen_text.append(text['body'])
            uniqueText.append(text)

    result['paragraphs'] = self.__set_unknown_section_headings(uniqueText)

    return result

def __handle_html(self, file_path, config):
        '''
        handles common HTML processing elements across main_text and linked_tables (creates soup and parses tables)
        :return: soup object
        '''

        soup = self.__soupify_infile(file_path)
        if "tables" in config:
            if self.tables == {}:
                self.tables, self.empty_tables = table(soup, config, file_path, self.base_dir).to_dict()
            else:
                seenIDs = set()
                for tab in self.tables['documents']:
                    if "." in tab['id']:
                        seenIDs.add(tab['id'].split(".")[0])
                    else:
                        seenIDs.add(tab['id'])
                tmp_tables, tmp_empty = table(soup, config, file_path, self.base_dir).to_dict()
                additive = 0
                for tabl in tmp_tables['documents']:
                    if "." in tabl['id']:
                        tabl_id = tabl['id'].split(".")[0]
                        tabl_pos = ".".join(tabl['id'].split(".")[1:])
                    else:
                        tabl_id = tabl['id']
                        tabl_pos = None
                    if tabl_id in seenIDs:
                        tabl_id = str(len(seenIDs) + 1)
                        if tabl_pos:
                            tabl['id'] = F"{tabl_id}.{tabl_pos}"
                        else:
                            tabl['id'] = tabl_id
                    seenIDs.add(tabl_id)
                self.tables["documents"].extend(tmp_tables["documents"])
                self.empty_tables.extend(tmp_empty)
        return soup

def onefile_abbreviation(file_path, config, to_dir):
    ac = autoCORPus()
    soup = __handle_html(file_path, config)
    main_text = __extract_text(soup, config)
    abbreviations(main_text, soup, config, file_path).to_dict()

    return main_text

file_path = 'D:/Downloads/jinweihao/2021-2022/DS-NLP/data/MWAS_PMC_corpus/Analytica_Chimica_Acta_Journal/html/PMC3040422.html'
main_t = onefile_abbreviation()