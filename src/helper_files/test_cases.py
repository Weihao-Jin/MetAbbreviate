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

# txt3 = 'We have named the new method hydriDK+ (hybrid algorithm + domain knowledge).'
# abb3 = 'hydriDK+'
# abb4 = 'hydriDK+'
#
# txt1 = "Treatment options available for GERD range from over-the-counter (OTC) antacids to proton pump inhibitors (PPIs) and anti-reflux surgery."
# abb1 = 'PPIs'
# #
# txt2 = 'antiserum showed that DC-SIGN1 is expressed on endothelial cells and CC chemokine receptor 5 (CCR5)-positive macrophage-like cells'
# txt2_1 = 'inducing the production of RANTES and decreasing C-C chemokine receptor 5 (CCR5) expression.'
# abb2 = 'CCR5'
#
# txt = 'However, heat shock protein 70 (HSP70) and cytochrome P450 (CYP450) were expressed significantly and constantly only in LNM NPC patients'
# abb = 'CYP450'
#
# txt5 = 'α-Linolenic acid (ALA,ω-3) and linoleic acid (LA,ω-6), which are the precursors of EPA'
# abb5 = 'ALA'
#
# txt6 = 'ADNI is funded by the NIA, the National Institute of Biomedical Imaging and Bioengineering (NIBIB) and through generous contributions from Abbott, AstraZeneca AB, Bayer Schering Pharma AG, Bristol-Myers Squibb, Eisai Global Clinical Development, Elan Corporation, Genentech, GE Healthcare, GlaxoS'
# abb6 = 'NIBIB'
#
# txt7 = 'graded using the Early Treatment Diabetic Retinopathy Study (ETDRS) severity scale and the'
# abb7 = 'ETDRS'
#
# print(f'\n\t\t\t\t{Hybrid_definition_mining(txt1, abb1)}')
# print(f'\n\t\t\t\t{Hybrid_definition_mining(txt2, abb2)}')
# print(f'\n\t\t\t\t{Hybrid_definition_mining(txt2_1, abb2)}')
# print(separate_sentence(txt1, abb1))
# print(Hybrid_definition_mining(txt3, abb3))
# print(Hybrid_definition_mining(txt3, abb4))
# print(Hybrid_definition_mining(txt, abb))
# print(Hybrid_definition_mining(txt5, abb5))
# print(Hybrid_definition_mining(txt6, abb6))
# print(separate_sentence(txt, 'hydriDK'))
# print(separate_sentence(txt, 'hydriDK+'))
# print(Hybrid_definition_mining(txt7, abb7))

# ls_can1, ls_can2 = generate_potential_definitions(txt5, abb5)
#
# a1, formation_rules1, definition_patterns1 = formationRules_and_definition_patterns(txt, abb, ls_can1)
# a2, formation_rules2, definition_patterns2 = formationRules_and_definition_patterns(txt, abb, ls_can2)
#
# def_pattern, form_rule, score = find_best_candidate(a1, (definition_patterns1 + definition_patterns2),
#                                                     (formation_rules1 + formation_rules2))
# res_str = find_definition(txt, form_rule, abb)

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