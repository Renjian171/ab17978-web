"""
Utilities for parsing genome data:
- Newick tree → ECharts-compatible JSON
- .fna files → genome statistics
"""
import os
from django.conf import settings
from Bio import Phylo  # 引入权威的 Biopython 树解析库

GENOME_DIR = r"C:\Users\ymh\Desktop\bacteria\GENOME_DB"
TREE_FILE = os.path.join(GENOME_DIR, "Phylogenetic_Tree", "gtdbtk.bac120.user_msa.fasta.treefile")

# ============================================================
#  Strain descriptions for Genome Descriptions section
# ============================================================
STRAIN_DESCRIPTIONS = {
    # ── Acinetobacter baumannii ──
    "A. baumannii 17978": (
        "Acinetobacter baumannii ATCC 17978 is a Gram-negative, non-motile, strictly aerobic "
        "coccobacillus and is one of the most widely studied reference strains of the species. "
        "Originally isolated in 1951 from a fatal case of meningitis in an infant, this strain has "
        "been instrumental in understanding the molecular pathogenesis and antibiotic resistance "
        "mechanisms of A. baumannii. The complete genome consists of a single circular chromosome "
        "of approximately 3.90 Mb with a GC content of ~39%, encoding approximately 3,801 "
        "protein-coding genes, plus three naturally occurring plasmids: pAB1 (~13.4 kb), pAB2 "
        "(~11.3 kb), and pAB3 (~149 kb). ATCC 17978 is notable for being the first A. baumannii "
        "strain to have its complete genome sequenced (published in 2007 by the J. Craig Venter "
        "Institute), which facilitated the annotation of key virulence factors including outer "
        "membrane protein OmpA, the K1 capsular polysaccharide locus, and the acinetobactin iron "
        "acquisition system. Unlike many clinical MDR isolates, ATCC 17978 is antibiotic-sensitive "
        "and amenable to genetic manipulation, making it the foundational model for functional "
        "genomics and host–pathogen interaction studies in A. baumannii. The strain belongs to "
        "sequence type ST437 (Pasteur scheme) and is classified as a member of international "
        "clone I (IC-I). Its genome has been extensively used for comparative genomics, "
        "transcriptomics (including TSS mapping), and proteomics analyses, and the strain serves "
        "as the reference for the AB Database."
    ),
    "A. baumannii 19606": (
        "Acinetobacter baumannii ATCC 19606 is the type strain of the species, originally isolated "
        "from human urine in the United States prior to 1948. It is a Gram-negative, non-motile, "
        "non-spore-forming, strictly aerobic coccobacillus. Unlike many clinical isolates of A. baumannii, "
        "ATCC 19606 is notably antibiotic-sensitive and amenable to genetic manipulation, making it a "
        "widely used reference and model organism for studying virulence, pathogenesis, and antimicrobial "
        "resistance mechanisms. The strain is a member of sequence type ST52 (Pasteur scheme). Its genome "
        "consists of a single circular chromosome of approximately 3.98 Mb with a GC content of ~39%, "
        "encoding approximately 3,732 protein-coding genes. The strain harbours at least two plasmids, "
        "including pMAC (~9.5 kb) which carries the ohr gene conferring resistance to organic "
        "hydroperoxides. A high-quality genome-scale metabolic model (iATCC19606v2) has been constructed "
        "for this strain, covering 1,009 genes, 2,114 reactions, and 1,422 metabolites, with 85.6% "
        "accuracy in predicting growth phenotypes. The strain also carries a chromosomal sul2 gene "
        "conferring resistance to sulphonamides and a complete 41–52 kb prophage designated Φ19606. "
        "Comparative analyses across different laboratory stocks have revealed genetic drift including "
        "SNPs, macro- and micro-deletions, and variable prophage presence."
    ),
    "A. baumannii 6080": (
        "Acinetobacter baumannii 6080 is a Gram-negative, non-motile, strictly aerobic coccobacillus "
        "belonging to the Acinetobacter calcoaceticus-baumannii (ACB) complex. It was isolated from a "
        "clinical specimen and represents a multidrug-resistant (MDR) strain of significant clinical "
        "concern. A. baumannii has emerged as one of the most troublesome nosocomial pathogens worldwide, "
        "particularly in intensive care units, where it causes ventilator-associated pneumonia, bloodstream "
        "infections, wound infections, and urinary tract infections. The bacterium is notorious for its "
        "ability to survive on dry surfaces for extended periods and to rapidly acquire antimicrobial "
        "resistance determinants through horizontal gene transfer. Strain 6080 carries multiple antibiotic "
        "resistance genes characteristic of MDR A. baumannii, including beta-lactamases and efflux pump "
        "systems. Its genome size is consistent with other A. baumannii clinical isolates, featuring a "
        "GC content of approximately 39% and numerous mobile genetic elements that contribute to its "
        "genomic plasticity."
    ),
    "A. baumannii AB-18_FGL": (
        "Acinetobacter baumannii AB-18_FGL is a Gram-negative, aerobic, non-motile coccobacillus "
        "isolated from a clinical setting. A. baumannii is a member of the ESKAPE group of pathogens "
        "(Enterococcus faecium, Staphylococcus aureus, Klebsiella pneumoniae, Acinetobacter baumannii, "
        "Pseudomonas aeruginosa, and Enterobacter species) that are the leading cause of nosocomial "
        "infections globally. This strain exhibits the characteristic genomic features of A. baumannii, "
        "including a compact genome with relatively low GC content (~39%) and a remarkable capacity for "
        "acquiring foreign DNA. A. baumannii is naturally competent for transformation, allowing it to "
        "uptake extracellular DNA from its environment, which facilitates the rapid spread of antibiotic "
        "resistance genes. The species can form biofilms on abiotic surfaces including medical devices "
        "such as catheters and ventilators, contributing to its persistence in hospital environments. "
        "AB-18_FGL represents one of the many genomically diverse lineages within the A. baumannii "
        "species complex."
    ),
    "A. baumannii AB-38_FGL": (
        "Acinetobacter baumannii AB-38_FGL is a Gram-negative, strictly aerobic, oxidase-negative, "
        "non-motile clinical isolate. Like other members of the species, it is a significant opportunistic "
        "pathogen primarily affecting immunocompromised patients and those with prolonged hospital stays. "
        "The bacterium demonstrates intrinsic resistance to many commonly used antimicrobial agents and "
        "has an exceptional capacity to develop or acquire resistance to virtually all antibiotics, "
        "including carbapenems and colistin — the drugs of last resort. The genome of AB-38_FGL harbours "
        "multiple genomic islands and resistance determinants acquired through horizontal gene transfer. "
        "A. baumannii employs a type VI secretion system (T6SS) for interbacterial competition, giving "
        "it a competitive advantage in polymicrobial infections. The strain also produces an exocellular "
        "polysaccharide capsule that protects it from desiccation, disinfectants, and host immune "
        "responses."
    ),
    "A. baumannii AB30": (
        "Acinetobacter baumannii AB30 is a Gram-negative, non-fermentative, aerobic coccobacillus "
        "isolated from clinical specimens. A. baumannii has earned the nickname 'Iraqibacter' due to "
        "its high prevalence among wounded military personnel returning from conflicts in the Middle "
        "East. The bacterium thrives in warm, humid environments and has been isolated from soil, water, "
        "and hospital surfaces. Strain AB30 is one of numerous clinical isolates studied to understand "
        "the population structure and evolutionary dynamics of the species. A. baumannii utilizes a "
        "diverse array of carbon sources and can grow at temperatures ranging from 20°C to 44°C, "
        "contributing to its environmental persistence. The outer membrane of A. baumannii contains "
        "lipooligosaccharide (LOS) rather than the full-length lipopolysaccharide (LPS) found in most "
        "Gram-negative bacteria, which affects its interaction with the host innate immune system."
    ),
    "A. baumannii AC1633": (
        "Acinetobacter baumannii AC1633 is a Gram-negative, strictly aerobic, non-motile, catalase-positive, "
        "oxidase-negative coccobacillus belonging to the ACB complex. This clinical isolate contributes to "
        "the growing understanding of the genomic diversity within the species. A. baumannii is estimated "
        "to cause approximately 2–10% of all Gram-negative hospital-acquired infections in the United States "
        "and Europe, with higher rates reported in Asia and Latin America. The mortality rate attributable "
        "to A. baumannii bloodstream infections ranges from 20% to 60%, depending on the patient population "
        "and the timeliness of appropriate antimicrobial therapy. Strain AC1633 possesses the hallmark "
        "genomic features of the species, including numerous insertion sequences (particularly ISAba1, "
        "which can provide promoter sequences that upregulate downstream antibiotic resistance genes) "
        "and a relatively small genome reflecting ongoing genome reduction and adaptation to a pathogenic "
        "lifestyle."
    ),
    "A. baumannii AF-401": (
        "Acinetobacter baumannii AF-401 is a Gram-negative, non-motile, strictly aerobic, non-fermentative "
        "bacterium. It is a clinical isolate that forms part of the diverse population structure of "
        "A. baumannii, which comprises several international clonal lineages (ICLs). The species is "
        "characterised by its ability to survive for months on dry inanimate surfaces — a trait uncommon "
        "among Gram-negative bacteria and central to its role in hospital outbreaks. This desiccation "
        "resistance is mediated by the presence of the outer membrane protein OmpA and the production of "
        "a thick polysaccharide capsule. AF-401, like other A. baumannii strains, demonstrates twitching "
        "motility mediated by type IV pili, which facilitates surface colonisation and biofilm formation. "
        "Biofilm-associated A. baumannii cells are up to 1,000-fold more resistant to antibiotics and "
        "disinfectants compared to their planktonic counterparts."
    ),
    "A. baumannii AR_0101": (
        "Acinetobacter baumannii AR_0101 is a multidrug-resistant clinical isolate from the CDC & FDA "
        "Antimicrobial Resistance Isolate Bank, originally recovered from human urine. It belongs to "
        "sequence type ST79 (Pasteur MLST scheme) and exhibits an extensive drug resistance profile. "
        "The strain is resistant to carbapenems (imipenem MIC >64 μg/mL, meropenem MIC >8 μg/mL), "
        "cephalosporins (cefepime, ceftazidime, ceftriaxone all >32 μg/mL), fluoroquinolones "
        "(ciprofloxacin and levofloxacin >8 μg/mL), piperacillin-tazobactam, and trimethoprim-sulfamethoxazole. "
        "Molecularly, it harbours the carbapenem-hydrolyzing class D beta-lactamase OXA-24, the "
        "Acinetobacter-derived cephalosporinase ADC-214, and OXA-65. Aminoglycoside resistance is "
        "conferred by aac(6')-Ian, ant(3'')-IIa, aph(6)-Id, and strA genes. It carries sul2 for "
        "sulphonamide resistance and the ABAF efflux pump system. Susceptibility is retained only to "
        "colistin (MIC 1 μg/mL), polymyxin B (MIC 2 μg/mL), and minocycline (MIC ≤4 μg/mL). AR_0101 "
        "is part of the CDC's Gram Negative Carbapenemase Detection (CarbaNP) panel and serves as a "
        "reference strain for antimicrobial resistance surveillance and diagnostic test development."
    ),
    "A. baumannii BAL114": (
        "Acinetobacter baumannii BAL114 is a Gram-negative, non-fermentative, strictly aerobic "
        "coccobacillus isolated from clinical specimens. This strain represents one of the many "
        "genetically diverse clinical lineages of A. baumannii circulating in healthcare settings "
        "globally. The species has been identified by the World Health Organization as the top priority "
        "pathogen for which new antibiotics are critically needed. A. baumannii employs several "
        "mechanisms of iron acquisition essential for its pathogenesis, including the production of "
        "siderophores (acinetobactin and baumannoferrin) and haem uptake systems. The bacterium can "
        "also utilise haem and haemoglobin as iron sources during infection. BAL114 contains genes "
        "encoding the Csu pilus-chaperone-usher system, which mediates adherence to abiotic surfaces "
        "and is critical for the initial steps of biofilm formation on medical devices."
    ),
    "A. baumannii DETAB-E51": (
        "Acinetobacter baumannii DETAB-E51 is a Gram-negative, strictly aerobic, non-motile, "
        "catalase-positive, oxidase-negative clinical isolate. The strain name reflects its origin "
        "from a healthcare-associated infection surveillance programme. A. baumannii has a remarkable "
        "capacity for natural transformation, with some strains estimated to take up exogenous DNA at "
        "frequencies approaching those of naturally competent species such as Bacillus subtilis. This "
        "competence is mediated by type IV pili and is induced by stressors including antibiotics and "
        "nutrient limitation. The DETAB-E51 genome includes the typical A. baumannii core genome of "
        "approximately 2,200 genes, plus a variable accessory genome largely composed of mobile genetic "
        "elements, phage-related sequences, and antibiotic resistance determinants acquired through "
        "horizontal gene transfer. The species demonstrates considerable metabolic versatility, capable "
        "of utilising diverse carbon and energy sources including amino acids, organic acids, and "
        "aromatic compounds."
    ),
    "A. baumannii MRSN 58": (
        "Acinetobacter baumannii MRSN 58 is a clinical isolate from the Multidrug-Resistant Organism "
        "Repository and Surveillance Network (MRSN), a U.S. Department of Defense programme that "
        "collects, characterises, and archives MDR bacteria from military treatment facilities worldwide. "
        "This strain was isolated from a wounded service member, underscoring the prominence of A. baumannii "
        "in combat-associated wound infections. Military personnel with blast injuries, burns, and open "
        "wounds are at particularly high risk for A. baumannii infections, which can lead to osteomyelitis, "
        "wound dehiscence, and bacteraemia. MRSN 58 is part of a collection that has been instrumental in "
        "understanding the global dissemination of MDR A. baumannii clones and the molecular epidemiology "
        "of carbapenem resistance. The MRSN programme has documented the emergence and spread of various "
        "OXA-type carbapenemases, including OXA-23, OXA-24/40, OXA-58, and OXA-143, among clinical "
        "isolates, informing infection control practices and antimicrobial stewardship."
    ),
    "A. baumannii MRSN15313": (
        "Acinetobacter baumannii MRSN15313 is a clinical isolate from the MRSN surveillance network, "
        "representing a multidrug-resistant phenotype. Like other MRSN isolates, it has been extensively "
        "characterised for its antimicrobial susceptibility profile and molecular resistance mechanisms. "
        "The genome of MRSN15313 reveals the characteristic genomic architecture of MDR A. baumannii: a "
        "compact core chromosome interspersed with resistance islands (AbaR-type genomic islands) that "
        "can harbour dozens of resistance genes within a single insertion. These resistance islands often "
        "integrate at specific chromosomal locations, such as the ATPase gene comM, disrupting natural "
        "competence but providing a stable platform for resistance gene accumulation. The strain also "
        "carries genes encoding the AdeABC and AdeIJK resistance-nodulation-division (RND) efflux pumps, "
        "which contribute to intrinsic and acquired resistance to a broad range of antimicrobials including "
        "beta-lactams, fluoroquinolones, tetracyclines, and aminoglycosides."
    ),
    "A. baumannii UC23022": (
        "Acinetobacter baumannii UC23022 is a Gram-negative, strictly aerobic, non-motile, "
        "non-lactose-fermenting coccobacillus. It is a clinical isolate that contributes to the "
        "genomic diversity of the species. A. baumannii employs quorum sensing (QS) systems mediated "
        "by N-acyl homoserine lactone (AHL) signal molecules to regulate biofilm formation, surface "
        "motility, and virulence gene expression. The AbaR protein is the primary LuxR-type QS receptor "
        "in A. baumannii. QS-regulated traits include the production of the surfactant-like lipopeptide "
        "and biofilm-associated protein (Bap), which is essential for the development of mature biofilms "
        "on abiotic surfaces. Strain UC23022 also produces outer membrane vesicles (OMVs) that can "
        "deliver virulence factors including the OmpA protein to host cells, inducing mitochondrial "
        "dysfunction and cell death. OMVs have also been implicated in the horizontal transfer of "
        "antibiotic resistance genes between A. baumannii cells."
    ),
    "A. baumannii VB82": (
        "Acinetobacter baumannii VB82 is a Gram-negative, non-fermentative, strictly aerobic "
        "coccobacillus of clinical origin. The strain exhibits the typical biochemical profile of "
        "A. baumannii: it is non-haemolytic on sheep blood agar, grows on MacConkey agar producing "
        "non-lactose-fermenting colonies, and is citrate-positive. A key challenge in the clinical "
        "management of A. baumannii infections is the discordance between in vitro susceptibility and "
        "in vivo efficacy of antibiotics, particularly for polymyxins and tigecycline. The presence of "
        "heteroresistance — where subpopulations of apparently susceptible bacteria exhibit reduced "
        "susceptibility — complicates treatment. VB82 may exhibit heteroresistance to colistin, a "
        "phenomenon increasingly reported among clinical A. baumannii isolates worldwide and associated "
        "with mutations in the PmrAB two-component regulatory system and lipid A biosynthesis genes "
        "that modify the lipooligosaccharide target of polymyxins."
    ),
    "A. baumannii XH1056": (
        "Acinetobacter baumannii XH1056 is a Gram-negative, obligately aerobic, non-motile, "
        "oxidase-negative coccobacillus isolated from clinical specimens in China. The 'XH' designation "
        "indicates its origin from a Chinese hospital surveillance programme. China has reported some of "
        "the highest rates of carbapenem-resistant A. baumannii (CRAB) globally, with over 70% of "
        "clinical A. baumannii isolates resistant to carbapenems in many tertiary hospitals. XH1056 "
        "contributes to understanding the unique molecular epidemiology of A. baumannii in East Asian "
        "healthcare settings, where clonal complex 92 (CC92, corresponding to international clone II) "
        "predominates. This globally disseminated clone is associated with high-level antibiotic "
        "resistance and increased mortality. The strain genome contains the typical A. baumannii "
        "virulence determinants including phoA and phoR (regulating lipid A modification), pmrCAB "
        "(controlling colistin resistance), and genes for poly-β-1,6-N-acetylglucosamine (PNAG) "
        "production, a key component of the A. baumannii biofilm matrix."
    ),

    # ── Other Acinetobacter species ──
    "A. bouvetii JCM18991": (
        "Acinetobacter bouvetii JCM 18991 (= DSM 14964 = 4B02) is the type strain of the species, "
        "formally described by Carr et al. in 2003. It is a Gram-negative, strictly aerobic, non-motile, "
        "oval-shaped coccobacillus originally isolated from activated sludge in a wastewater treatment "
        "plant in Bendigo, Victoria, Australia. Unlike the clinically significant A. baumannii, "
        "A. bouvetii is primarily an environmental bacterium found in water and soil ecosystems, with "
        "no significant association with human disease. The species belongs to the genus Acinetobacter "
        "within the family Moraxellaceae. It is non-spore-forming, mesophilic, with optimal growth at "
        "25–35°C, and is classified as biosafety level 1. The strain is catalase-positive, oxidase-negative, "
        "and utilises a variety of organic compounds as carbon sources. Phylogenetically, it is distinct "
        "from the A. calcoaceticus-baumannii complex, based on 16S rRNA gene sequence analysis and DNA-DNA "
        "hybridization studies. The 16S rRNA gene sequence is deposited under accession AF509827."
    ),
    "A. chenhuanii XH1741": (
        "Acinetobacter chenhuanii XH1741 is a recently described species within the genus Acinetobacter, "
        "isolated from a clinical specimen in China. The species was named in honour of the Chinese "
        "microbiologist Chen Huan. It is a Gram-negative, strictly aerobic, non-motile, oxidase-negative "
        "coccobacillus. Phylogenetic analysis based on 16S rRNA gene and whole-genome sequences places "
        "it within the expanding Acinetobacter genus, which now comprises over 70 validly published "
        "species with diverse ecological niches ranging from free-living environmental saprophytes to "
        "opportunistic human pathogens. The description of A. chenhuanii highlights the ongoing discovery "
        "of novel Acinetobacter species facilitated by advanced genomic approaches. The strain exhibits "
        "the characteristic metabolic versatility of the genus, capable of growing on a range of simple "
        "carbon sources including acetate, ethanol, and various amino acids."
    ),
    "A. corruptisaponis KCTC 92772": (
        "Acinetobacter corruptisaponis KCTC 92772 is a recently characterised species of the genus "
        "Acinetobacter, with the species epithet derived from Latin 'corruptus' (corrupted) and 'sapo' "
        "(soap), referring to its isolation from degraded soap or detergent-contaminated environments. "
        "It is a Gram-negative, strictly aerobic, non-motile, oxidase-negative, catalase-positive "
        "coccobacillus. The strain grows optimally at mesophilic temperatures (25–30°C) and is "
        "non-haemolytic. Like many environmental Acinetobacter species, A. corruptisaponis is "
        "metabolically versatile and capable of degrading diverse organic compounds, potentially "
        "including surfactants and detergents. The species contributes to the understanding of the "
        "remarkable ecological diversity within the Acinetobacter genus, which spans from free-living "
        "soil and water bacteria to strict human pathogens. The strain is deposited at the Korean "
        "Collection for Type Cultures (KCTC)."
    ),
    "A. lanii 185": (
        "Acinetobacter lanii 185 is a member of the genus Acinetobacter, which encompasses a "
        "taxonomically diverse group of Gram-negative, strictly aerobic, non-fermentative "
        "coccobacilli. This environmental isolate contributes to our understanding of the breadth "
        "of metabolic capabilities and ecological niches occupied by non-pathogenic Acinetobacter "
        "species. Unlike the clinically notorious A. baumannii, many Acinetobacter species including "
        "A. lanii are environmental organisms that play important roles in soil ecosystems, including "
        "the degradation of complex organic compounds such as lignin-derived aromatics, long-chain "
        "hydrocarbons, and pesticides. The genus is characterised by a DNA G+C content ranging from "
        "34% to 47% and demonstrates natural competence in many species. A. lanii 185 grows optimally "
        "under aerobic conditions at mesophilic temperatures and is oxidase-negative and catalase-positive."
    ),
    "A. larvae BRTC-1": (
        "Acinetobacter larvae BRTC-1 is a Gram-negative, strictly aerobic, non-motile coccobacillus "
        "associated with insect larvae. The species name reflects its entomological origin. The genus "
        "Acinetobacter is ubiquitous in nature and its members have been isolated from diverse sources "
        "including soil, water, sewage, food products, human skin, and various animal hosts. Certain "
        "Acinetobacter species have been explored for their biotechnological potential, including "
        "bioremediation of hydrocarbon-contaminated environments, production of bioemulsifiers, and "
        "phosphate removal from wastewater. Other strains produce lipases and esterases with industrial "
        "applications. BRTC-1 may represent a novel ecological niche within the genus, potentially "
        "contributing to the gut microbiota of insects or acting as an entomopathogen. The strain "
        "is maintained at the Bee Research and Training Center (BRTC) collection."
    ),
    "A. lwoffii DSM2403": (
        "Acinetobacter lwoffii DSM 2403 (= ATCC 15309 = NCTC 5866 = CIP 64.10) is the type strain "
        "of the species, originally described by Audureau in 1940 and named after the French "
        "microbiologist André Lwoff. It is a Gram-negative, strictly aerobic, non-motile, oxidase-negative, "
        "catalase-positive coccobacillus. Unlike A. baumannii, A. lwoffii is generally considered a "
        "low-virulence commensal organism commonly found on human skin, in the oropharynx, and in the "
        "environment. However, it can cause opportunistic infections, particularly in immunocompromised "
        "patients, including catheter-related bloodstream infections, endocarditis, and meningitis. "
        "A. lwoffii is characteristically susceptible to most antibiotics, in stark contrast to "
        "multidrug-resistant A. baumannii, and can be reliably differentiated by its inability to "
        "grow at 44°C and its failure to utilise glucose oxidatively. Phylogenetic studies place "
        "A. lwoffii in a distinct clade separate from the ACB complex. The species is of interest "
        "for comparative genomics to understand the genetic basis of the transition from environmental "
        "commensal to multidrug-resistant pathogen within the genus."
    ),
    "A. tibetensis Y-23": (
        "Acinetobacter tibetensis Y-23 is a recently described species of the genus Acinetobacter, "
        "isolated from soil or environmental samples collected on the Tibetan Plateau, China. The "
        "species name reflects its geographic origin in Tibet, a high-altitude environment characterised "
        "by low temperatures, high UV radiation, and oligotrophic conditions. A. tibetensis is a "
        "Gram-negative, strictly aerobic, psychrotolerant or psychrophilic, non-motile coccobacillus "
        "adapted to cold environments. The strain likely possesses cold-adapted enzymes and membrane "
        "lipid modifications that enable growth at low temperatures. High-altitude Acinetobacter "
        "species such as A. tibetensis are of interest for understanding microbial adaptation to "
        "extreme environments and for bioprospecting cold-active enzymes with potential applications "
        "in industrial processes, bioremediation, and molecular biology. The genome of Y-23 likely "
        "encodes cold-shock proteins, compatible solute transporters, and modified fatty acid "
        "desaturases that maintain membrane fluidity at low temperatures."
    ),

    # ── Pseudomonas ──
    "P. entomophila L48": (
        "Pseudomonas entomophila L48ᵀ (= DSM 28517 = CECT 7985) is the type strain of the species, "
        "isolated in 2000 from a female Drosophila melanogaster fruit fly in Guadeloupe, French Caribbean. "
        "It is a Gram-negative, rod-shaped, strictly aerobic, motile bacterium with a single polar "
        "flagellum, and is notable for being the first identified natural pathogen of Drosophila "
        "melanogaster. Unlike many Gram-negative animal pathogens, P. entomophila lacks both Type III "
        "and Type IV secretion systems, relying instead on a suite of virulence factors including "
        "insecticidal toxin complexes (TccC-type), extracellular proteases and lipases, hydrogen cyanide "
        "(HCN) production, diffusible haemolytic activity, and novel secondary metabolites regulated "
        "by the GacS/GacA two-component system. It produces two siderophores for iron acquisition: "
        "a structurally novel pyoverdine and pseudomonine, enabling strong iron competition in the "
        "insect gut. The species is orally infectious to Drosophila larvae and adults, and lethal to "
        "insects from multiple orders, suggesting biocontrol potential. The complete genome consists of "
        "a single circular chromosome of approximately 5.9 Mb encoding ~5,134 protein-coding genes. "
        "Phylogenetically, P. entomophila belongs to the Pseudomonas putida group and shares extensive "
        "catabolic gene content with the saprophyte P. putida KT2440. P. entomophila was formally "
        "described as a novel species by Mulet et al. in 2012."
    ),
    "P. monsensis PGSB 8459": (
        "Pseudomonas monsensis PGSB 8459 is a Gram-negative, rod-shaped, strictly aerobic, motile "
        "bacterium belonging to the genus Pseudomonas within the class Gammaproteobacteria. The species "
        "epithet 'monsensis' is derived from Mons, Belgium, reflecting its geographic origin. Members "
        "of the genus Pseudomonas are renowned for their extraordinary metabolic versatility, capable "
        "of degrading a vast array of organic compounds including hydrocarbons, aromatic pollutants, "
        "and pesticides, and can colonise diverse ecological niches from soil and freshwater to plant "
        "rhizospheres and animal hosts. P. monsensis contributes to the understanding of the ecological "
        "diversity within the Pseudomonas genus. The strain is well-adapted to soil environments, "
        "producing a range of extracellular enzymes involved in nutrient cycling and organic matter "
        "decomposition. Motility is conferred by polar flagella, and the organism is catalase-positive "
        "and oxidase-positive, typical of fluorescent pseudomonads. The genome of PGSB 8459 encodes "
        "numerous transporters and catabolic pathways reflecting its saprophytic soil lifestyle."
    ),
    "P. protegens CHA0": (
        "Pseudomonas protegens CHA0 (formerly Pseudomonas fluorescens CHA0) is the type strain of the "
        "species and is a Gram-negative, rod-shaped, motile, strictly aerobic, plant-beneficial bacterium "
        "originally isolated in 1983 from tobacco roots grown in a soil naturally suppressive to black "
        "root rot caused by Thielaviopsis basicola, in Morens, Switzerland. CHA0 is a model organism for "
        "studying the molecular mechanisms of biological control of soilborne plant pathogens, producing "
        "a remarkable arsenal of antimicrobial secondary metabolites including 2,4-diacetylphloroglucinol "
        "(2,4-DAPG), pyoluteorin, pyrrolnitrin, hydrogen cyanide (HCN), siderophores (pyoverdine, "
        "pyochelin), and various extracellular enzymes. Notably, it also produces the Fit (P. fluorescens "
        "insecticidal toxin) toxin and is pathogenic to lepidopteran insect larvae upon oral ingestion. "
        "The strain possesses a Type VI Secretion System (T6SS) used in interbacterial competition and "
        "produces R-tailocins (phage tail-like bacteriocins). Its genome consists of a single circular "
        "chromosome of ~6.87 Mb with a GC content of ~63.4%, encoding approximately 6,115 protein-coding "
        "genes, three complete prophages, and seven CRISPR clusters. It shares 98.87% nucleotide identity "
        "with P. protegens Pf-5. The genome was fully sequenced and reannotated by Smits et al. in 2019, "
        "with manual curation of all known biocontrol and insect pathogenicity determinants."
    ),
    "P. putida NBRC 14164": (
        "Pseudomonas putida NBRC 14164 (= ATCC 12633 = DSM 291 = JCM 13063) is the type strain of "
        "the species and is a Gram-negative, rod-shaped, motile by means of one or more polar flagella, "
        "strictly aerobic, non-fermentative, oxidase-positive, catalase-positive bacterium. P. putida "
        "is widely distributed in soil and aquatic environments and is renowned for its robust metabolism "
        "and stress tolerance, making it a premier platform organism for synthetic biology and "
        "biotechnological applications. Unlike P. aeruginosa, P. putida is generally recognised as a "
        "safe (GRAS) organism with low virulence potential. The species is a powerhouse of metabolic "
        "diversity, capable of degrading numerous recalcitrant organic compounds including toluene, "
        "xylene, naphthalene, camphor, and various halogenated compounds, making it invaluable for "
        "bioremediation. The type strain genome encodes extensive oxidative enzymes, solvent tolerance "
        "mechanisms (including cis-trans isomerisation of membrane fatty acids and efflux pumps), and "
        "the Entner-Doudoroff pathway as the primary route for carbohydrate catabolism. P. putida "
        "NBRC 14164 has served as a reference for the phylogenetic and taxonomic framework of the "
        "Pseudomonas putida group, which now encompasses numerous closely related species with diverse "
        "ecological functions."
    ),
    "P. synxantha NCTC10696": (
        "Pseudomonas synxantha NCTC 10696 (= ATCC 9890 = DSM 18928 = LMG 2335) is the type strain of "
        "the species and is a Gram-negative, rod-shaped, motile, strictly aerobic bacterium. The species "
        "name, derived from Greek 'syn' (together) and 'xanthos' (yellow), refers to the characteristic "
        "production of a yellow, non-fluorescent, non-diffusible pigment. P. synxantha belongs to the "
        "Pseudomonas fluorescens group within the Gammaproteobacteria. It was originally isolated from "
        "creamery water and has been studied extensively as a psychrotrophic spoilage bacterium in the "
        "dairy industry, particularly in refrigerated milk and dairy products where it can produce "
        "heat-resistant lipases and proteases that survive pasteurisation and cause off-flavours, "
        "bitterness, and gelation during shelf life. The species can grow at refrigeration temperatures "
        "(as low as 4°C) making it a significant concern for the cold chain. Beyond its role in food "
        "spoilage, P. synxantha contributes to nutrient cycling in soil and water environments through "
        "the production of various extracellular hydrolytic enzymes. The strain is oxidase-positive, "
        "catalase-positive, and produces fluorescent siderophores on iron-limited media. "
        "Phylogenetically, it is closely related to Pseudomonas libanensis and Pseudomonas gessardii "
        "within the P. fluorescens species complex."
    ),
}


# ============================================================
#  Newick Parser (Powered by Biopython)
# ============================================================

def clade_to_dict(clade):
    """
    递归函数：将 Biopython 的 Clade 对象转换为 ECharts 支持的嵌套字典
    """
    node = {}
    
    # 提取节点名称（自动清洗引号和多余空白，彻底解决名字粘连）
    if clade.name:
        node["name"] = str(clade.name).strip().strip("'").strip('"')
    else:
        node["name"] = ""

    # 提取分支长度
    if clade.branch_length is not None:
        node["value"] = round(clade.branch_length, 6)

    # 如果有子分支，递归调用保持拓扑结构
    if clade.clades:
        node["children"] = [clade_to_dict(child) for child in clade.clades]

    return node

def get_tree_json():
    """Read the Newick tree file and return ECharts-compatible JSON."""
    if not os.path.isfile(TREE_FILE):
        return {"error": "Tree file not found"}

    try:
        # 使用 Biopython 强力解析，不会错过任何一个分支
        tree = Phylo.read(TREE_FILE, "newick")
        
        # 从根节点开始，将其转换为 ECharts 需要的 JSON 字典
        tree_dict = clade_to_dict(tree.root)
        
        return tree_dict
        
    except Exception as e:
        print(f"解析进化树文件失败: {e}")
        return {"error": str(e)}


# ============================================================
#  FNA Genome Statistics Parser (保留您原本的逻辑)
# ============================================================

def parse_fna_stats(filepath):
    """
    Parse a .fna file to extract genome statistics.
    Returns dict with:
      - filename, strain_name, total_length, contig_count,
        gc_content, n50, longest_contig, shortest_contig, contig_lengths
    """
    contigs = {}
    current_id = None
    current_seq = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_id is not None:
                    contigs[current_id] = "".join(current_seq)
                current_id = line[1:].split()[0]  # First word of header
                current_seq = []
            else:
                if current_id is not None:
                    current_seq.append(line.upper())

    if current_id is not None:
        contigs[current_id] = "".join(current_seq)

    if not contigs:
        return None

    lengths = sorted([len(seq) for seq in contigs.values()], reverse=True)

    total_length = sum(lengths)
    contig_count = len(lengths)

    # GC content
    all_seq = "".join(contigs.values())
    gc_count = all_seq.count("G") + all_seq.count("C")
    at_count = all_seq.count("A") + all_seq.count("T")
    gc_content = (gc_count / (gc_count + at_count) * 100) if (gc_count + at_count) > 0 else 0

    # N50
    half_total = total_length / 2
    cumsum = 0
    n50 = 0
    for l in lengths:
        cumsum += l
        if cumsum >= half_total:
            n50 = l
            break

    # Extract strain name from filename
    basename = os.path.basename(filepath)
    strain_name = basename.replace(".fna", "")

    return {
        "filename": basename,
        "strain_name": strain_name,
        "total_length": total_length,
        "contig_count": contig_count,
        "gc_content": round(gc_content, 2),
        "n50": n50,
        "longest_contig": lengths[0] if lengths else 0,
        "shortest_contig": lengths[-1] if lengths else 0,
    }

def get_all_genome_stats():
    """Parse all .fna files (including in sub-folders) and return stats list."""
    results = []
    if not os.path.isdir(GENOME_DIR):
        return results

    for item in sorted(os.listdir(GENOME_DIR)):
        item_path = os.path.join(GENOME_DIR, item)
        # Check both root-level .fna and sub-folder .fna
        if os.path.isdir(item_path):
            for fname in sorted(os.listdir(item_path)):
                if fname.endswith(".fna"):
                    filepath = os.path.join(item_path, fname)
                    stats = parse_fna_stats(filepath)
                    if stats:
                        strain_name = stats.get("strain_name", "")
                        stats["description"] = STRAIN_DESCRIPTIONS.get(strain_name, "")
                        results.append(stats)
        elif item.endswith(".fna"):
            stats = parse_fna_stats(item_path)
            if stats:
                strain_name = stats.get("strain_name", "")
                stats["description"] = STRAIN_DESCRIPTIONS.get(strain_name, "")
                results.append(stats)
    return results


# ============================================================
#  Ab17978 Genes Page — GFF3 / BED Parsers
# ============================================================

AB17978_DIR = r"C:\Users\ymh\Desktop\bacteria"

# File paths
AB17978_FILES = {
    "chromosome_fna": os.path.join(AB17978_DIR, "Ab17978.fna"),
    "merged_gff3": os.path.join(AB17978_DIR, "final_merged_annotation.gff3"),
    "plasmid1_fna": os.path.join(AB17978_DIR, "Ab17978_Plasmid_1(1).fna"),
    "plasmid1_gff3": os.path.join(AB17978_DIR, "Ab17978_Plasmid_1(1).gff3"),
    "plasmid2_fna": os.path.join(AB17978_DIR, "Ab17978_Plasmid_2(1).fna"),
    "plasmid2_gff3": os.path.join(AB17978_DIR, "Ab17978_Plasmid_2(1).gff3"),
    "plasmid3_fna": os.path.join(AB17978_DIR, "Ab17978_Plasmid_3.fna"),
    "plasmid3_gff3": os.path.join(AB17978_DIR, "Ab17978_Plasmid_3(1).gff3"),
    "srna_tss_bed": os.path.join(AB17978_DIR, "best_srna_tssWYQ(2)(1).bed"),
    "primary_tss_bed": os.path.join(AB17978_DIR, "primary_per_geneWYQ(2)(1).bed"),
}

FEATURE_COLORS = {
    "CDS_forward": "#3182ce",
    "CDS_reverse": "#e53e3e",
    "rRNA": "#38a169",
    "tRNA": "#dd6b20",
    "sRNA": "#805ad5",
    "oriC": "#d69e2e",
    "region": "#718096",
    "TSS_primary": "#2b6cb0",
    "TSS_srna": "#6b46c1",
}


def parse_gff3_features(filepath, replicon_name):
    """
    Parse a GFF3 file and return structured feature data.
    Only extracts feature lines (skips ## comments).
    """
    features = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("##"):
                    continue
                if line.startswith("#"):
                    continue
                cols = line.split("\t")
                if len(cols) < 9:
                    continue

                seqid = cols[0]
                source = cols[1]
                ftype = cols[2]
                start = int(cols[3])
                end = int(cols[4])
                strand = cols[6]
                # Some GFF3 files have embedded tabs in attribute values;
                # join extra columns back into the attributes field.
                attrs = "\t".join(cols[8:])

                # Parse attributes (replace embedded tabs with spaces)
                attr_dict = {}
                for pair in attrs.split(";"):
                    pair = pair.strip().replace("\t", " ")
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        attr_dict[k] = v

                feature = {
                    "start": start,
                    "end": end,
                    "strand": strand,
                    "type": ftype,
                    "source": source,
                    "name": attr_dict.get("Name", ""),
                    "product": attr_dict.get("product", ""),
                    "locus_tag": attr_dict.get("locus_tag", attr_dict.get("ID", "")),
                    "gene": attr_dict.get("gene", ""),
                }

                # Simplify CDS type to include strand info
                if ftype == "CDS":
                    feature["color_key"] = "CDS_forward" if strand == "+" else "CDS_reverse"
                else:
                    feature["color_key"] = ftype

                features.append(feature)
    except FileNotFoundError:
        pass
    return features


def parse_bed_file(filepath):
    """
    Parse a BED file and return TSS positions.
    BED format: chrom start end name score strand [other...]
    """
    entries = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                cols = line.split("\t")
                if len(cols) < 6:
                    continue
                entries.append({
                    "chrom": cols[0],
                    "start": int(cols[1]),
                    "end": int(cols[2]),
                    "name": cols[3],
                    "score": cols[4],
                    "strand": cols[5],
                    "target": cols[6] if len(cols) > 6 else "",
                })
    except FileNotFoundError:
        pass
    return entries


def get_genes_data():
    """
    Orchestration: parse all Ab17978 annotation files and return
    structured data for the Genes page visualization.
    """
    # --- Chromosome ---
    chr_features = parse_gff3_features(AB17978_FILES["merged_gff3"], "Chromosome")
    chromosome = {
        "name": "Chromosome",
        "seqid": "Ab17978_Chromosome",
        "length": 3902108,
        "type": "chromosome",
        "features": chr_features,
        "feature_counts": {},
    }
    for f in chr_features:
        key = f["color_key"]
        chromosome["feature_counts"][key] = chromosome["feature_counts"].get(key, 0) + 1

    # --- Plasmids ---
    plasmids = []
    for p_num, (name, gff_key, fna_key) in enumerate([
        ("Plasmid 1", "plasmid1_gff3", "plasmid1_fna"),
        ("Plasmid 2", "plasmid2_gff3", "plasmid2_fna"),
        ("Plasmid 3", "plasmid3_gff3", "plasmid3_fna"),
    ], start=1):
        p_features = parse_gff3_features(AB17978_FILES[gff_key], name)
        # Each plasmid length from the file
        p_lengths = {1: 148955, 2: 13409, 3: 11302}
        p_info = {
            "name": name,
            "seqid": f"Ab17978_Plasmid_{p_num}",
            "length": p_lengths[p_num],
            "type": "plasmid",
            "features": p_features,
            "feature_counts": {},
        }
        for f in p_features:
            key = f["color_key"]
            p_info["feature_counts"][key] = p_info["feature_counts"].get(key, 0) + 1
        plasmids.append(p_info)

    # --- TSS data ---
    srna_tss = parse_bed_file(AB17978_FILES["srna_tss_bed"])
    primary_tss = parse_bed_file(AB17978_FILES["primary_tss_bed"])

    return {
        "replicons": [chromosome] + plasmids,
        "tss": {
            "srna": srna_tss,
            "primary": primary_tss,
        },
        "color_map": FEATURE_COLORS,
    }


# Cache for parsed genes data
_GENES_CACHE = None


def _cached_genes_data():
    global _GENES_CACHE
    if _GENES_CACHE is None:
        _GENES_CACHE = get_genes_data()
    return _GENES_CACHE


def search_genes(query):
    """
    Search features across all replicons by locus_tag, gene, name, or product.
    Returns a list of matching features with replicon context.
    """
    data = _cached_genes_data()
    q = query.strip().lower()
    if not q:
        return []

    results = []
    for rep in data["replicons"]:
        for f in rep["features"]:
            # Search in locus_tag, gene, name, product (case-insensitive)
            searchable = " ".join([
                f.get("locus_tag", ""),
                f.get("gene", ""),
                f.get("name", ""),
                f.get("product", ""),
            ]).lower()

            if q in searchable:
                results.append({
                    **f,
                    "replicon_name": rep["name"],
                    "replicon_seqid": rep["seqid"],
                    "replicon_length": rep["length"],
                    "replicon_type": rep["type"],
                })

    # Limit results and sort: CDS first, then by locus_tag
    results.sort(key=lambda x: (x["type"] != "CDS", x.get("locus_tag", "")))
    return results[:200]


def get_gene_context(locus_tag, replicon_seqid=None, radius=5000):
    """
    Given a locus_tag, return features in the surrounding region (±radius).
    """
    data = _cached_genes_data()

    # Find the target feature and its replicon
    target = None
    target_rep = None
    for rep in data["replicons"]:
        if replicon_seqid and rep["seqid"] != replicon_seqid:
            continue
        for f in rep["features"]:
            if f.get("locus_tag", "") == locus_tag:
                target = f
                target_rep = rep
                break
        if target:
            break

    if not target:
        return {"error": f"Gene '{locus_tag}' not found"}

    # Collect features within the window
    region_start = max(0, target["start"] - radius)
    region_end = target["end"] + radius

    context_features = []
    for f in target_rep["features"]:
        if f["end"] >= region_start and f["start"] <= region_end:
            context_features.append(f)

    # Sort by position
    context_features.sort(key=lambda x: (x["start"], x["end"]))

    # Protein sequence for CDS targets (FAA or FNA translation)
    target_sequence = None
    if target["type"] == "CDS":
        target_sequence = get_sequence_for_gene(
            target.get("locus_tag", ""),
            target_rep["seqid"],
            target["start"],
            target["end"],
            target.get("strand", "+"),
        )

    return {
        "target": {
            **target,
            "sequence": target_sequence,
            "replicon_name": target_rep["name"],
            "replicon_seqid": target_rep["seqid"],
            "replicon_length": target_rep["length"],
            "replicon_type": target_rep["type"],
        },
        "region_start": region_start,
        "region_end": region_end,
        "radius": radius,
        "features": context_features,
        "feature_count": len(context_features),
        "color_map": FEATURE_COLORS,
    }


def get_region_features(replicon_seqid, start, end):
    """
    Query features in an arbitrary genomic region.
    Used by the IGV-style genome browser for dynamic loading when the
    viewport moves outside the initially loaded context window.
    """
    data = _cached_genes_data()
    replicon = None

    for rep in data["replicons"]:
        if rep["seqid"] == replicon_seqid:
            replicon = rep
            break

    if not replicon:
        return {"error": f"Replicon '{replicon_seqid}' not found"}

    region_start = max(0, int(start))
    region_end = int(end)

    features = []
    for f in replicon["features"]:
        if f["end"] >= region_start and f["start"] <= region_end:
            features.append(f)

    features.sort(key=lambda x: (x["start"], x["end"]))

    return {
        "replicon_name": replicon["name"],
        "replicon_seqid": replicon["seqid"],
        "replicon_length": replicon["length"],
        "replicon_type": replicon["type"],
        "region_start": region_start,
        "region_end": region_end,
        "features": features,
        "feature_count": len(features),
        "color_map": FEATURE_COLORS,
    }


# ============================================================
#  Protein Sequence Extraction (FAA)
# ============================================================

FAA_FILE = os.path.join(AB17978_DIR, "Ab17978_complete.faa")
_FAA_CACHE = None  # {locus_tag: (header, sequence)}


def _load_faa():
    """Load the FAA protein file and index by locus_tag."""
    global _FAA_CACHE
    if _FAA_CACHE is not None:
        return _FAA_CACHE

    _FAA_CACHE = {}
    if not os.path.isfile(FAA_FILE):
        return _FAA_CACHE

    current_tag = None
    current_seq = []
    with open(FAA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_tag:
                    _FAA_CACHE[current_tag] = "".join(current_seq)
                # locus_tag is the first word after ">"
                header = line[1:]
                parts = header.split(None, 1)
                current_tag = parts[0] if parts else header
                current_seq = []
            else:
                current_seq.append(line.upper())
    if current_tag:
        _FAA_CACHE[current_tag] = "".join(current_seq)

    return _FAA_CACHE


def get_protein_sequence(locus_tag):
    """Return the amino acid sequence for a given locus_tag, or None."""
    faa = _load_faa()
    return faa.get(locus_tag)


# ============================================================
#  DNA → Protein Translation (for plasmid genes not in FAA)
# ============================================================

# Replicon → FNA file (for DNA extraction)
_REPLICON_FNA = {
    "Ab17978_Chromosome": os.path.join(AB17978_DIR, "Ab17978.fna"),
    "Ab17978_Plasmid_1": os.path.join(AB17978_DIR, "Ab17978_Plasmid_1(1).fna"),
    "Ab17978_Plasmid_2": os.path.join(AB17978_DIR, "Ab17978_Plasmid_2(1).fna"),
    "Ab17978_Plasmid_3": os.path.join(AB17978_DIR, "Ab17978_Plasmid_3.fna"),
}
_FNA_DNA_CACHE = {}

GENETIC_CODE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}

COMPLEMENT = str.maketrans("ATGCatgc", "TACGtacg")


def _reverse_complement(dna):
    return dna.translate(COMPLEMENT)[::-1]


def _translate(dna):
    """Translate a DNA sequence to protein (standard code)."""
    aa = []
    for i in range(0, len(dna) - 2, 3):
        codon = dna[i:i + 3]
        aa.append(GENETIC_CODE.get(codon, "X"))
    return "".join(aa).rstrip("*")


def _get_dna_sequence(replicon_seqid):
    """Load full DNA sequence for a replicon from FNA."""
    if replicon_seqid in _FNA_DNA_CACHE:
        return _FNA_DNA_CACHE[replicon_seqid]

    fna_path = _REPLICON_FNA.get(replicon_seqid)
    if not fna_path or not os.path.isfile(fna_path):
        return None

    seq_parts = []
    with open(fna_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                continue
            seq_parts.append(line.upper())

    full_seq = "".join(seq_parts)
    _FNA_DNA_CACHE[replicon_seqid] = full_seq
    return full_seq


def get_sequence_for_gene(locus_tag, replicon_seqid, start, end, strand):
    """
    Get the amino acid sequence for a gene.
    Tries the FAA file first, then falls back to DNA translation from FNA.
    """
    # Try FAA file first (chromosome genes)
    aa_seq = get_protein_sequence(locus_tag)
    if aa_seq:
        return aa_seq

    # Fall back: translate from DNA (plasmid genes)
    dna = _get_dna_sequence(replicon_seqid)
    if not dna:
        return None

    # Extract CDS region (1-based → 0-based)
    s = max(0, int(start) - 1)
    e = min(len(dna), int(end))
    if s >= len(dna) or e <= s:
        return None

    cds_dna = dna[s:e]
    if strand == "-":
        cds_dna = _reverse_complement(cds_dna)

    return _translate(cds_dna)