import spacy
import regex as re
from scispacy.abbreviation import AbbreviationDetector
re1 = r'\b[A-Z](?:[&_.-///a-z]?[A-Z0-9α-ωΑ-Ω])+[a-z]*\b'
# re1_1 = r'\b[A-Z](?:\W?[A-Z0-9])+[a-z]?\b'
# re2 = r'\b[A-Z](?:[&.]?[A-Z])+\b'
# re3 = r'\s[A-Z](?:[&.]?[A-Z])+\s'

# re_dig1 = r'\b[0-9](?:[_:&-.///]?[a-zA-Z0-9])+\b'
re_dig2 = r'\b[0-9](?:[,:&_.-///]?[a-zA-Z0-9α-ωΑ-Ω])+[A-Z]{1}(?:[,:&_.-///]?[a-zA-Z0-9α-ωΑ-Ω])*\b'
# re_dig2_1 = r'[\s([][0-9](?:[,_:&-.///]?[a-zA-Z0-9])+[a-zA-Z]{1}(?:[_:&-.///]?[a-zA-Z0-9])*\b'

re_sb = r'[[α-ωΑ-Ω][0-9A-Z](?:[_&-.///]?[A-Z0-9])+[]](?:[_&-.///]?[A-Z0-9])+\b'

text1 = 'We studied the long-chain conversion of [U-13C]alpha-linolenic acid (ALA) and linoleic acid (LA) and responses of erythrocyte phospholipid composition to variation in the dietary ratios of 18:3n-3 (ALA) and 18:2n-6 (LA) for 12 weeks in 38 moderately hyperlipidemic men. Diets were enriched with either flaxseed oil (FXO; 17 g/day ALA, n=21) or sunflower oil (SO; 17 g/day LA, n=17). The FXO diet induced increases in phospholipid ALA (>3-fold), 20:5n-3 [eicosapentaenoic acid (EPA), >2-fold], and 22:5n-3 [docosapentaenoic acid (DPA), 50%] but no change in 22:6n-3 [docosahexanoic acid (DHA)], LA, or 20:4n-6 [arachidonic acid (AA)]. The increases in EPA and DPA but not DHA were similar to those in subjects given the SO diet enriched with 3 g of EPA plus DHA from fish oil (n=19). The SO diet induced a small increase in LA but no change in AA. Long-chain conversion of [U-13C]ALA and [U-13C]LA, calculated from peak plasma 13C concentrations after simple modeling for tracer dilution in subsets from the FXO (n=6) and SO (n=5) diets, was similar but low for the two tracers (i.e., AA, 0.2%; EPA, 0.3%; and DPA, 0.02%) and varied directly with precursor concentrations and inversely with concentrations of fatty acids of the alternative series. [13C]DHA formation was very low (<0.01%) with no dietary influences.'
text2 = '“We developed a sensitive and selective ultra-performance liquid chromatography-tandem mass spectrometry (UPLC-MS/MS) method for the simultaneous profiling of 57 targeted oxylipins derived from five major n-6 and n-3 polyunsaturated fatty acids (PUFAs) that serve as oxylipin precursors, including linoleic (LA), arachidonic (AA), alpha-linolenic (ALA), eicosapentaenoic (EPA), and docosahexaenoic (DHA) acids. The targeted oxylipin panel provides broad coverage of lipid mediators and pathway markers generated from cyclooxygenases, lipoxygenases, cytochrome P450 epoxygenases/hydroxylases, and non-enzymatic oxidation pathways. The method is based on combination of protein precipitation and solid-phase extraction (SPE) for sample preparation, followed by UPLC-MS/MS. This is the first methodology to incorporate four hydroxy-epoxy-octadecenoic acids and four keto-epoxy-octadecenoic acids into an oxylipin profiling network. The novel method achieves excellent resolution and allows in-depth analysis of isomeric and isobaric species of oxylipin extracts in biological samples. The method was quantitatively characterized in human plasma with good linearity (R = 0.990–0.999), acceptable reproducibility (relative standard deviation (RSD) < 20% for the majority of analytes), accuracy (67.8 to 129.3%) for all analytes, and recovery (66.8–121.2%) for all analytes except 5,6-EET.” (abstract)'
text3 = 'The present study aimed to evaluate the effects of various dietary α-linolenic acid (ALA, 18:3n-3)/linoleic acid (LA, 18:2n-6) ratios in cultured fish. Thus, a great deal of attention has been placed on understanding fish lipid and fatty acid metabolism and, specifically, the capability of bioconverting polyunsaturated fatty acids with 18 carbon atoms (C18 PUFA), commonly found in most alternative terrestrial oils, to long-chain polyunsaturated fatty acids (LC-PUFA) which are typically present in oils of marine origin.'
text4 = 'For example, PD1 and PDX differ in double bond geometry and stereochemistry of the hydroxyl group at C10 position; PGF2α and 8-isoPGF2α stereoisomers differ in the configuration of the C7–C8 bond; and PGE2 and PGD2 regioisomers bear similar major fragment ions (Fig. 2). Additionally, we also achieved baseline resolution for the isomers sharing the same MRM transition for quantitation such as LXA4 and LXB4 (351 > 115), RvD1 and RvD2 (375 > 215), and RvD3 and RvD4 (375 > 147) with minimal cross-talk. '
text5 = 'However, 9,10,13-TriHOME and 9,12,13-TriHOME (329 > 171) only partially resolved. Furthermore, for coeluting isomers 9-HODE and 13-HODE, and partially resolved isomers 9-EpOME and 13-EpOME, 9-HODE and 9-EpOME were each found to produce a very minor peak at m/z 195, forming an MRM transition 295 > 195, corresponding to less than 1% of the response at the same concentration level for 13-HODE and 13-EpOME. '
text6 = 'Generation of oxylipins derived from n-6 LA and AA, and n-3 ALA, EPA, and DHA via LOX (lipoxygenase), cyclooxygenase (COX), cytochrome P450 (CYP), and non-enzymatic oxidation. Colors depict the precursor pathway metabolite families: LA (green), AA (red), ALA (tan), EPA (purple), DHA (dark red), LA, linoleic acid; AA, arachidonic acid; ALA, α-linolenic acid, EPA, eicosapentaenoic acid; DHA, docosahexaenoic acid; EpODE, epoxy-octadecadienoic acid; HODE, hydroxy-octadecadienoic acid; oxoODE, keto-octadecadienoic acid; EPOME, epoxy-octadecenoic acid; DiHOME, dihydroxy-octadecenoic acid, TriHOME, trihydroxy-octadecenoic acid; H-E-LA, hydroxyepoxy-octadecenoic acid; K-E-LA, keto-epoxy-octadecenoic acid; HPOTrE, hydroperoxy-octadecatrienoic acid, HOTrE, hydroxyoctadecatrienoic acid; PGG, hydroperoxide-endoperoxide prostaglandin; PG, prostaglandin; TX, thromboxane; LT, leukotriene; LX, lipoxin; HpETE, hydroperoxyeicosatetraenoic acids; HETE, hydroxypentaenoic acid; oxoETE, keto-eicosatetraenoic acid; EET, epoxyeicosatrienoic acids; HpEPE, hydroperoxyeicosapentaenoic acids; HEPE, hydroxyeicosapentaenoic acid; EEQ, epoxy eicosatetraenoic acid; HpDHA, hydroperoxy-docosahexaenoic acid, HDHA, hydroxyl-docosahexaenoic acid; EDP, epoxy docosapentaenoic acid; DiHDHA, hydroxydocosahexaenoic acid; PDX, 10S,17S-DiHDHA; PD/NPD, protectin; Rv, resolving'
text7 = ' as we have demonstrated previously using isotope-coded affinity tag (ICAT) '
text8 = 'The proportion of fatty acid variance explained by a particular variant allele was calculated for each cohort from the formula corr(Y, Ŷ)2 ≌ (β2*2*MAF(1-MAF))/Var(Y), where β is the regression coefficient for one copy of the allele, MAF is the minor allele frequency and Var(Y) is the variance of the fatty acid (Online Supplemental Material)'

nlp = spacy.load('D:/Downloads/jinweihao/2021-2022/DS-NLP/scispacy_vol/en_core_sci_sm-0.5.0/en_core_sci_sm/en_core_sci_sm-0.5.0')
nlp.add_pipe("abbreviation_detector")
doc = nlp(text6)

print("Abbreviation", "\t", "Definition")
for abrv in doc._.abbreviations:
	print(f"{abrv} \t ({abrv.start}, {abrv.end}) \t {abrv._.long_form}")


res = re.findall(re_dig2, text8)
print(res)

# def findbestCandidates(short, long):
# 	sIndex = len(short)-1
# 	lIndex = len(long)-1
# 	longlower = long.lower()
# 	while sIndex >= 0:
# 		currchar = short.lower()[sIndex]
# 		if not currchar.isalnum():
# 			continue
# 		while(lIndex >= 0 and longlower[lIndex] != currchar) or (sIndex == 0 and lIndex > 0 and longlower[lIndex-1].isalnum()):
# 			lIndex -= 1
# 		if lIndex < 0:
# 			return "failed"
# 		lIndex -= 1
# 		sIndex -= 1
# 	lIndex = long



