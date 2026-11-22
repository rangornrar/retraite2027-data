"""Génère v1/fiscalite.json : loi actuelle 2026 + mesures fiscales des candidats de scenarios.json (22/11/2026)."""
import json, sys
MAJ = "2026-11-22"
PT = "https://presitracker2027.fr/themes/fis"
def src(label, url=None, date=None):
    d = {"label": label}
    if url: d["url"] = url
    if date: d["date"] = date
    return d
def v(val, s): return {"value": val, "source": s}
def m(theme, text, modelled, s): return {"theme": theme, "text": text, "modelled": modelled, "source": s}
def pt(label, date=None): return src(f"{label}, recensé par PresiTracker2027", PT, date)

T = lambda *l: [{"upTo": a, "rate": b} if a is not None else {"rate": b} for a, b in l]
IR = T((11600, 0), (29579, .11), (84577, .30), (181917, .41), (None, .45))
SUCC = T((8072, .05), (12109, .10), (15932, .15), (552324, .20), (902838, .30), (1805677, .40), (None, .45))
IFI = {"totalBase": False, "threshold": 1300000,
       "brackets": T((800000, 0), (1300000, .005), (2570000, .007), (5000000, .01), (10000000, .0125), (None, .015)),
       "residenceAllowance": .30, "decoteUntil": 1400000, "decoteFlat": 17500, "decoteRate": .0125}
SP_IR = src("Barème 2026 des revenus 2025 (loi de finances 2026, art. 4)", "https://www.service-public.gouv.fr/particuliers/actualites/A14660", "2026-04-07")
SP_AM = src("Brochure pratique 2026, aide-mémoire (DGFiP)", "https://www.impots.gouv.fr/www2/fichiers/documentation/brochure/ir_2026/pdf_som/aide_memoire.pdf", "2026-04-01")
BOFIP_QF = src("Plafonnement du quotient familial : 1 807 € par demi-part (BOFiP)", "https://bofip.impots.gouv.fr/node/377293", "2026-04-07")
DECOTE = src("Décote 2026 : 897 € (seul) ou 1 483 € (couple) − 45,25 % de l'impôt brut", "https://www.toutsurmesfinances.com/impots/?p=56674", "2026-02-19")
CSS = src("CSG 9,2 % dont 6,8 % déductible, CRDS 0,5 %, sur 98,25 % du salaire (code de la sécurité sociale, art. L136-1-2 et L136-8)")
CGI_IFI = src("IFI : seuil 1,3 M€, barème de 0,5 % à 1,5 %, abattement de 30 % sur la résidence principale (CGI, art. 964 à 983)")
CGI_SUCC = src("Droits de succession en ligne directe : abattement de 100 000 € par enfant, barème de 5 % à 45 % (CGI, art. 777 et 779)")
CGI_IS = src("IS 25 % ; 15 % jusqu'à 42 500 € de bénéfice pour les PME de moins de 10 M€ de CA (CGI, art. 219)")
CGI_CSB = src("Contribution sociale de 3,3 % sur l'IS au-delà de 763 000 €, CA d'au moins 7,63 M€ (CGI, art. 235 ter ZC)")
BERCY_CE = src("Contribution exceptionnelle 2026 : 20,6 % de l'IS (CA de 1,5 à 3 Md€), 41,2 % au-delà (loi de finances 2026)", "https://www.economie.gouv.fr/node/3239369", "2026-02-19")
SP_CVAE = src("CVAE 2026 : 0 % sous 500 000 € de CA, jusqu'à 0,28 % au-delà de 50 M€ ; valeur ajoutée plafonnée à 80 % ou 85 % du CA", "https://entreprendre.service-public.gouv.fr/vosdroits/F23546", "2026-03-30")
BERCY_TA = src("Taxe additionnelle à la CVAE : 9,23 % en 2026", "https://www.economie.gouv.fr/node/37027", "2026-01-01")
C3S = src("C3S : 0,16 % du CA au-delà de 19 M€ (code de la sécurité sociale, art. L137-30 et suivants)", "https://www.institutmontaigne.org/presidentielle-2022/valerie-pecresse/supprimer-la-contribution-sociale-de-solidarite-des-entreprises")
LOI = src("Loi actuelle")

reference = {"id": "loi-actuelle", "params": {
    "csgSalary": v({"rate": .092, "deductible": .068, "crds": .005, "base": .9825}, CSS),
    "irBrackets": v(IR, SP_IR),
    "irDecote": v({"single": 897, "couple": 1483, "rate": .4525}, DECOTE),
    "workExpenses": v({"rate": .10, "min": 509, "max": 14555}, SP_AM),
    "qfCap": v({"cap": 1807}, BOFIP_QF),
    "qfFullShareSecondChild": v(False, src("Demi-part pour chacun des deux premiers enfants, une part à partir du troisième (CGI, art. 194)")),
    "irExemptUnderAge": v({"age": None}, LOI),
    "youngChildReduction": v(0, LOI),
    "wealthTax": v(IFI, CGI_IFI),
    "topFortunes": v([], LOI),
    "inheritance": v({"childAllowance": 100000, "brackets": SUCC}, CGI_SUCC),
    "corporateTax": v({"rate": .25, "reducedRate": .15, "reducedCeiling": 42500, "reducedMaxTurnover": 10000000}, CGI_IS),
    "csb": v({"rate": .033, "allowance": 763000, "minTurnover": 7630000}, CGI_CSB),
    "exceptionalContribution": v([{"threshold": 1.5e9, "rate": .206}, {"threshold": 3e9, "rate": .412}], BERCY_CE),
    "reinvestedCoefficient": v(1, LOI),
    "youngFounderExemptionYears": v(0, LOI),
    "newCompanyMoratoriumYears": v(0, LOI),
    "cvae": v({"points": [{"turnover": 500000, "rate": 0}, {"turnover": 3e6, "rate": .00094},
                          {"turnover": 1e7, "rate": .00263}, {"turnover": 5e7, "rate": .00282}],
               "maxRate": .0028, "additionalTax": .0923, "cap85Above": 7600000}, SP_CVAE),
    "c3s": v({"threshold": 1.9e7, "rate": .0016}, C3S),
    "cfeCoefficient": v(1, src("CFE : impôt local, montant saisi par l'utilisateur")),
    "cfeIndustrialExempt": v(False, LOI),
    "dividendTax": v([], LOI),
}, "measures": [
    m("REVENU", "Projet de loi de finances 2027 en discussion : barème revalorisé de 2,1 %, contribution exceptionnelle des grandes entreprises reconduite. L'app applique la loi votée pour 2026.", False,
      src("Toutsurmesfinances, barème 2027", "https://www.toutsurmesfinances.com/impots/bareme-de-l-impot-sur-le-revenu.html")),
    m("PRODUCTION", "CVAE : suppression progressive jusqu'en 2030 (0,19 % en 2028, 0,09 % en 2029)", False, BERCY_TA),
]}

C = {}
def cand(id_, params=None, nc=None, mesures=()):
    C[id_] = {"id": id_, "params": params or {}, "notComputable": nc or {}, "measures": list(mesures)}

cand("arthaud", mesures=[
    m("SOCIETES", "Réquisition des profits des secteurs pétrolier et de l'armement", False, pt("Meeting LO", "2026-09-26")),
    m("SOCIETES", "Levée du secret commercial des entreprises", False, pt("Meeting LO", "2026-09-26"))])
S_ATTAL = src("Débat TF1-LCI du 16/11/2026 (Toutsurmesfinances)", "https://www.toutsurmesfinances.com/actualites/?p=2982", "2026-11-16")
cand("attal", {"csgSalary": v({"rate": 0, "deductible": 0, "crds": .005, "base": .9825}, S_ATTAL)}, mesures=[
    m("REVENU", "Supprimer la CSG sur les salaires (gain annoncé jusqu'à 270 € net par mois) ; calendrier non précisé. L'app la retire des salaires, la CRDS reste", True, S_ATTAL),
    m("REVENU", "Baisse des cotisations salariales, non chiffrée ; aucune hausse d'impôts", False, pt("Acteurs publics ; programme « travail et salaires »", "2026-07-03")),
    m("PATRIMOINE", "Pas de hausse de la fiscalité de l'assurance-vie ni des successions ; donations facilitées aux petits-enfants", False, pt("Assises AFER, meeting de Lyon", "2026-10-10"))])
cand("asselineau")
cand("batho")
cand("becht")
cand("bertrand", mesures=[m("CONSOMMATION", "Pas de taxation des voitures électriques", False, pt("L'Opinion", "2026-08-19"))])
cand("bouamrane", mesures=[m("SOCIETES", "Aides aux entreprises conditionnées au paiement de leurs impôts en France", False, pt("Oumma", "2026-07-02"))])
S_BRANCO = pt("« Le Projet 2027 » (Les Ruches)")
cand("branco", {"newCompanyMoratoriumYears": v(3, S_BRANCO)},
     {"PATRIMOINE": "ISF rétabli sans barème publié", "SUCCESSION": "Seuils annoncés sans barème des droits"}, [
    m("PATRIMOINE", "Droits de mutation supprimés pour 90 % des foyers ; taxation « confiscatoire » au-delà de 100 M€ (10 M€ hors ligne directe) ; ISF rétabli", False, S_BRANCO),
    m("SOCIETES", "Moratoire fiscal de trois ans pour les nouvelles entreprises ; suppression de 267 petites taxes", True, S_BRANCO),
    m("CONSOMMATION", "TVA relevée de 10 points sur le luxe et les aliments ultra-transformés ; TVA sociale sur les biens non essentiels", False, S_BRANCO)])
S_CAZ = pt("« Lettre aux Français »", "2026-07-15")
cand("cazeneuve", nc={"PATRIMOINE": "Contribution des très grandes fortunes non chiffrée", "PRODUCTION": "Baisse des impôts de production non chiffrée"}, mesures=[
    m("PATRIMOINE", "Contribution des très grandes fortunes et des hauts revenus du capital ; critique de la flat tax", False, S_CAZ),
    m("PRODUCTION", "Baisse des impôts de production", False, S_CAZ)])
cand("dubuisson", mesures=[m("PATRIMOINE", "Opposé à une taxe de 2 % sur les patrimoines de plus de 100 M€", False, pt("dubuisson2027.fr", "2026-10-19"))])
S_NDA_L = pt("Programme, page logement", "2026-09-30")
S_NDA_E = pt("Projet économie et travail", "2026-10-10")
ifi_nda = dict(IFI); ifi_nda["residenceAllowance"] = 1.0
cand("dupont-aignan", {
    "wealthTax": v(ifi_nda, S_NDA_L),
    "inheritance": v({"childAllowance": 100000, "brackets": SUCC, "residenceExcluded": True}, S_NDA_L),
    "reinvestedCoefficient": v(.5, S_NDA_E)}, mesures=[
    m("PATRIMOINE", "Résidence principale exclue de l'IFI et des droits de succession", True, S_NDA_L),
    m("PATRIMOINE", "Impôt sur les très grandes fortunes, hors résidence principale, sans taux publié ; donations exonérées relevées de 100 000 €", False, S_NDA_E),
    m("SOCIETES", "Impôt sur les sociétés divisé par deux sur les bénéfices réinvestis", True, S_NDA_E),
    m("SOCIETES", "Multinationales imposées au prorata de leur chiffre d'affaires en France ; taxe sur les données personnelles", False, S_NDA_E),
    m("CONSOMMATION", "TVA supprimée sur 50 produits", False, S_NDA_E)])
TOUT = {k: "Suppression de la fiscalité annoncée sans détail" for k in ["SALAIRE", "IMPOT_REVENU", "PATRIMOINE", "SUCCESSION", "IMPOT_SOCIETES", "PRODUCTION"]}
cand("durif", nc=TOUT, mesures=[m("REVENU", "« Fiscalité supprimée », sans impôts précisés ni remplacement", False, pt("Programme « Zéro Défaut »", "2026-09-15"))])
cand("egger")
S_GLU = pt("AFP via Public Sénat", "2026-11-09")
cand("glucksmann", {"topFortunes": v([{"threshold": 1e8, "rate": .05}], S_GLU)},
     {"SALAIRE": "Baisse de la CSG sur les salaires annoncée sans taux", "SUCCESSION": "Taxation des très grands héritages non chiffrée"}, [
    m("PATRIMOINE", "Contribution exceptionnelle de 5 % sur les patrimoines de plus de 100 M€", True, S_GLU),
    m("REVENU", "Baisse de la CSG sur les salaires pour rapprocher le net du brut", False, pt("LCP", "2026-10-09")),
    m("PATRIMOINE", "Taxation des hauts patrimoines et des très grands héritages", False, pt("Sud Radio", "2026-10-04")),
    m("SOCIETES", "Taxation des superprofits, taxe européenne sur les superprofits pétroliers et gaziers", False, S_GLU),
    m("CONSOMMATION", "Fin de l'exonération du kérosène sur les vols intérieurs ; hausse de la taxe sur les billets d'avion ; jets privés et yachts ciblés", False, S_GLU)])
cand("kazib", mesures=[m("SOCIETES", "Suppression des aides publiques aux grandes entreprises", False, pt("anasse2027.fr"))])
cand("labib", nc={"PATRIMOINE": "Prélèvements sur les milliardaires non chiffrés"},
     mesures=[m("PATRIMOINE", "Mesures sociales financées par des prélèvements sur actionnaires et milliardaires", False, pt("Fête de l'Humanité", "2026-09-12"))])
cand("lalanne")
S_LP_L = pt("Livret « La France entreprend »")
S_LP_B = pt("Contre-budget RN 2026")
cand("le-pen", {
    "irExemptUnderAge": v({"age": 30}, S_LP_L),
    "qfFullShareSecondChild": v(True, src("Part fiscale pleine dès le deuxième enfant (contre-budget ; Europe 1, 25/10/2026), recensé par PresiTracker2027", PT, "2026-10-25")),
    "youngFounderExemptionYears": v(5, S_LP_L)},
    {"PATRIMOINE": "IFI remplacé par un impôt sur la fortune financière sans barème publié",
     "PRODUCTION": "Baisse de 16,2 Md€ répartie entre CFE, CVAE et C3S, sans taux par impôt"}, [
    m("REVENU", "Exonération d'impôt sur le revenu pour les moins de 30 ans (l'app l'applique au salaire du déclarant)", True, S_LP_L),
    m("REVENU", "Part fiscale pleine dès le deuxième enfant ; barème de l'impôt et CSG indexés sur l'inflation", True, S_LP_B),
    m("PATRIMOINE", "Impôt sur la fortune financière remplaçant l'IFI (résidence principale, biens professionnels exclus)", False, S_LP_B),
    m("PATRIMOINE", "Transmission d'entreprise exonérée contre une détention de 10 ans", False, S_LP_L),
    m("SOCIETES", "Exonération d'IS pendant cinq ans pour les entreprises créées par un moins de 30 ans", True, S_LP_L),
    m("PRODUCTION", "Baisse des impôts de production de 16,2 Md€ (CFE 8,8 ; CVAE 2,6 ; C3S 4,8)", False, S_LP_B),
    m("SOCIETES", "Taxation à 33 % des profits exceptionnels en période de crise ; taxe sur les rachats d'actions", False, S_LP_L)])
S_LIS = src("Programme de David Lisnard (L'Hémicycle)", "https://lhemicycle.com/candidat/david-lisnard/", "2026-11-21")
S_LIS_M = pt("Meeting de Paris", "2026-01-21")
cand("lisnard", {
    "qfCap": v({"cap": None}, pt("Programme « L'ambition française »")),
    "corporateTax": v({"rate": .20, "reducedRate": .15, "reducedCeiling": 42500, "reducedMaxTurnover": 10000000}, S_LIS),
    "c3s": v(None, S_LIS_M), "cvae": v(None, S_LIS)},
    {"SALAIRE": "Alignement de la CSG des actifs sur celle des retraités sans taux arrêté"}, [
    m("REVENU", "Déplafonnement du quotient familial", True, pt("Programme « L'ambition française »")),
    m("REVENU", "Baisser la CSG des actifs au niveau de celle des retraités (taux cités : 9,2 % et 6,6 %)", False, pt("Discours de La Gagne", "2026-08")),
    m("SOCIETES", "Impôt sur les sociétés à 20 %", True, S_LIS),
    m("PRODUCTION", "Impôts de production divisés par deux ; suppression de la C3S et de la CVAE (« le cas échéant » pour la CVAE en janvier)", True, S_LIS_M),
    m("PATRIMOINE", "Transmission des entreprises libérée des droits de succession", False, pt("Benfeld", "2026-09-25"))])
cand("markovic")
cand("mathieu")
S_LFI = pt("Budget LFI du 14/10/2026 et « L'Avenir en commun »", "2026-10-14")
cand("melenchon", nc={
    "SALAIRE": "CSG progressive à 14 tranches sans barème publié",
    "IMPOT_REVENU": "Barème à 14 tranches annoncé sans seuils ni taux publiés",
    "PATRIMOINE": "ISF rétabli sans barème publié",
    "SUCCESSION": "Hausse des droits sur les plus hauts patrimoines sans barème publié",
    "IMPOT_SOCIETES": "IS progressif sans taux publiés",
    "PRODUCTION": "CVAE rétablie pour les plus grandes entreprises sans taux"}, mesures=[
    m("REVENU", "Impôt sur le revenu à 14 tranches ; CSG progressive ; fin du quotient conjugal, crédit d'impôt par enfant ; fin de la flat tax", False, S_LFI),
    m("PATRIMOINE", "ISF rétabli avec un volet climatique ; taxe de 2 % sur les patrimoines de plus de 100 M€ ; taxe foncière progressive", False, S_LFI),
    m("PATRIMOINE", "Héritage maximal de 12 M€ ; droits relevés sur les plus hauts patrimoines ; cinq logements transmissibles au plus", False, S_LFI),
    m("SOCIETES", "IS progressif selon les bénéfices et leur usage ; taxe sur les superprofits ; taxe sur les multinationales ; fin des exonérations de cotisations au-dessus de 2 Smic", False, S_LFI),
    m("CONSOMMATION", "TVA réduite sur les produits de première nécessité, « TVA grand luxe »", False, S_LFI)])
cand("philippe", {"youngChildReduction": v(3000, src("Programme « Pour une France plus attentive à ses enfants » ; Public Sénat, 18/11/2026, recensé par PresiTracker2027", PT, "2026-11-18"))},
     {"PRODUCTION": "Baisse de 50 Md€ par an des impôts de production sans répartition par impôt"}, [
    m("REVENU", "Pas d'impôt sur le revenu pendant les trois premières années d'un enfant pour les classes moyennes (4e au 7e décile), réduction de 3 000 €/an au-delà. L'app retient une réduction plafonnée à 3 000 €", True,
      pt("Public Sénat", "2026-11-18")),
    m("REVENU", "Aucun nouvel impôt ni nouvelle norme pendant le quinquennat", False, pt("« Pour une France plus prospère »")),
    m("PRODUCTION", "Impôts de production baissés de 50 Md€ par an, compensés par 50 Md€ d'aides en moins", False, pt("Public Sénat", "2026-11-18")),
    m("PATRIMOINE", "Pacte Dutreil maintenu ; plafonds de donation relevés les trois premières années", False, pt("Programme Horizons"))])
cand("philippot", nc={"SUCCESSION": "Baisse des droits sur les petits héritages sans seuil"}, mesures=[
    m("PATRIMOINE", "Moindre taxation des petits héritages", False, pt("Projet pour la France 2026-2027", "2026-09-15")),
    m("SOCIETES", "Allègement fiscal pour les indépendants et les TPE, non chiffré", False, pt("Projet pour la France 2026-2027", "2026-09-15"))])
cand("platret")
cand("polony", mesures=[m("SOCIETES", "Taxe sur les superprofits des groupes pétroliers, sans mécanisme détaillé", False, pt("Sud Radio", "2026-09-15"))])
S_RET = pt("Projet industrie et entreprises (LR)", "2026-10-19")
cand("retailleau", {"c3s": v(None, S_RET), "cvae": v(None, S_RET), "cfeIndustrialExempt": v(True, S_RET)},
     {"IMPOT_REVENU": "Baisse de 21 Md€ des impôts des ménages sans détail"}, [
    m("PRODUCTION", "Suppression de la C3S et de la CVAE, exonération de la part industrielle de la CFE", True, S_RET),
    m("SOCIETES", "Baisse de 30 Md€ des impôts des entreprises, dont plus de 25 Md€ sur le coût du travail", False, pt("Public Sénat", "2026-10-12")),
    m("REVENU", "Baisse de 21 Md€ des impôts des ménages", False, pt("Public Sénat", "2026-10-12")),
    m("PATRIMOINE", "Dons familiaux exonérés jusqu'à 150 000 € pour les moins de 30 ans pendant trois ans", False, pt("Projet logement"))])
cand("riner")
cand("rohou")
S_ROU = pt("Fête de l'Humanité", "2026-09-15")
cand("roussel", {"inheritance": v({"childAllowance": 100000, "brackets": SUCC, "exemptBelow": 200000}, S_ROU)},
     {"PATRIMOINE": "ISF rétabli sans barème publié"}, [
    m("PATRIMOINE", "Héritages de moins de 200 000 € exonérés", True, S_ROU),
    m("PATRIMOINE", "Rétablissement de l'ISF", False, S_ROU)])
S_RUF = pt("« Pour un travaillisme écologique »", "2026-09-09")
S_RUF_RET = src("LCP (AFP), 21/11/2026", "https://lcp.fr/actualites/francois-ruffin-se-retire-de-la-presidentielle-2027-sans-soutenir-aucun-des-candidats-de", "2026-11-21")
cand("ruffin", {"topFortunes": v([{"threshold": 1e8, "rate": .02}], pt("Manifeste", "2026-04-10")),
                "dividendTax": v([{"threshold": 0, "rate": .02}, {"threshold": 1e7, "rate": .04}], S_RUF)}, mesures=[
    m("REVENU", "Candidature retirée le 21/11/2026 ; propositions conservées pour mémoire", False, S_RUF_RET),
    m("PATRIMOINE", "Soutien à la taxe Zucman de 2 % sur les patrimoines de plus de 100 M€", True, pt("Manifeste", "2026-04-10")),
    m("SOCIETES", "Taxe sur les dividendes soumise à référendum : 4 % au-delà de 10 M€ versés, 2 % en dessous", True, S_RUF),
    m("PATRIMOINE", "Fin de l'abattement pour durée de détention sur les plus-values immobilières ; meublés touristiques imposés de 40 à 70 %", False, pt("Cahier logement", "2026-09-24"))])
S_TON = pt("« Pour une prospérité écologique »", "2026-07-13")
cand("tondelier", {"topFortunes": v([{"threshold": 1e8, "rate": .02}], S_TON)},
     {"PATRIMOINE": "ISF climatique sans barème publié", "SUCCESSION": "Deux tranches ajoutées au-delà de 4 M€ et 13 M€ sans taux publiés"}, [
    m("PATRIMOINE", "Taxe Zucman de 2 % au-delà de 100 M€ ; ISF climatique ; barème des successions unifié, plafonnement du pacte Dutreil", False, S_TON),
    m("CONSOMMATION", "TVA « verte » modulée selon l'impact environnemental ; TVA réduite sur l'abonnement électrique", False, S_TON)])
S_VIL = pt("« Big Bang : la règle républicaine » (La France humaniste)", "2026-08-28")
S_VIL_E = pt("La France humaniste, « 20 propositions »")
cand("villepin", {
    "inheritance": v({"childAllowance": 100000, "brackets": SUCC, "exemptBelow": 1000000}, S_VIL),
    "cvae": v(None, S_VIL_E), "c3s": v(None, S_VIL_E), "cfeCoefficient": v(0, S_VIL_E)},
    {"PATRIMOINE": "Impôt unique sur la fortune dès 2,2 M€, fortement progressif, sans barème publié"}, [
    m("PATRIMOINE", "Pas de droits de succession sous 1 M€ ; au-delà, droits plus lourds sans barème publié (l'app applique le barème actuel au-delà)", True, S_VIL),
    m("PATRIMOINE", "Impôt unique sur la fortune, toutes sources de patrimoine, à partir de 2,2 M€, ciblant le 1 % le plus riche", False, S_VIL),
    m("REVENU", "Suppression d'environ 400 niches fiscales et sociales ; neuf grands impôts et un code fiscal de 40 pages", False, S_VIL),
    m("PRODUCTION", "Suppression des impôts de production (l'app retire CVAE, C3S et CFE)", True, S_VIL_E)])
cand("zemmour", {"inheritance": v({"abolished": True, "childAllowance": 100000, "brackets": SUCC}, pt("Entretien TV Agri, rapporté par Agra", "2026-10-07"))}, mesures=[
    m("PATRIMOINE", "Suppression des droits de succession, notamment pour la transmission des fermes", True, pt("Entretien TV Agri, rapporté par Agra", "2026-10-07"))])

ids_retraite = [s["id"] for s in json.load(open(sys.argv[2], encoding="utf-8"))["scenarios"] if s["type"] == "candidate"]
manquants = set(ids_retraite) - set(C); en_trop = set(C) - set(ids_retraite)
assert not manquants and not en_trop, (manquants, en_trop)
out = {"formatVersion": 1, "publishedAt": MAJ,
       "cotisations": {"pass": 48060, "oldAgeCapped": .069, "oldAgeUncapped": .004, "agircT1": .0401, "agircT2": .0972, "cet": .0014,
                       "source": "Taux salariés 2026 du secteur privé : vieillesse 6,90 % + 0,40 %, Agirc-Arrco et CEG 4,01 % / 9,72 %, CET 0,14 %"},
       "reference": reference, "candidates": [C[i] for i in ids_retraite]}
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(sys.argv[1], "a").write("\n")
print(len(C), "candidats")
