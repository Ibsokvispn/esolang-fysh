#!/usr/bin/env python3
"""Distances entre programmes Fysh : p.fysh contre les propositions des LLM (llm/*.fysh).

Usage (depuis la racine du dépôt) :
    python3 analyse/distance.py            # écrit analyse/resultats/*.csv et analyse/resultats/distances.md
    python3 analyse/distance.py --heatmap  # produit aussi analyse/resultats/matrice.png (matplotlib)

Pré-traitement (voir analyse/README.md) :
  1. les commentaires (`><//> …` et `# …`) sont supprimés ;
  2. les deux lignes d'entrée `number1` / `number2` sont supprimées (elles sont remplacées par run.sh) ;
  3. zone « calcul » : on retire en plus les zones imposées par SPEC.md, c'est-à-dire toute ligne
     d'affichage `(+o …` et toute affectation d'une chaîne à une variable ;
     zone « complet » : on les garde.
Les mesures sont calculées sur la liste de tokens Fysh (voir `tokenize`).
"""
import bz2, csv, difflib, itertools, math, os, re, sys, zlib
from collections import Counter

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "analyse", "resultats")

# --------------------------------------------------------------------------- programmes
ETIQUETTES = {
    "p": "p (moi)",
    "p_claude-haiku-5-5-faible_1": "haiku",
    "p_claude-sonnet-5-5-moyen_1": "sonnet",
    "p_gemini-moyen_1": "gemini-1",
    "p_gemini-max_1": "gemini-2",
    "p_glm_1": "glm-1",
    "p_glm_2": "glm-2",
}


def charger():
    chemins = [("p", os.path.join(RACINE, "p.fysh"))]
    d = os.path.join(RACINE, "llm")
    for f in sorted(os.listdir(d)):
        if f.endswith(".fysh"):
            chemins.append((f[:-5], os.path.join(d, f)))
    ordre = list(ETIQUETTES)  # ordre des essais du journal ; les fichiers inconnus viennent à la fin
    chemins.sort(key=lambda c: ordre.index(c[0]) if c[0] in ordre else len(ordre))
    progs = {}
    for cle, chemin in chemins:
        with open(chemin, encoding="utf-8") as fh:
            progs[ETIQUETTES.get(cle, cle)] = fh.read()
    return progs


# --------------------------------------------------------------------------- pré-traitement
RE_COMMENT = re.compile(r"(><//>|#).*$")
RE_ENTREE = re.compile(r"^\s*><number([12])>\s*(≈|=)")
RE_AFFECT_CHAINE = re.compile(r"^\s*><\w+>\s*(≈|=)\s*(🫧[^🫧]*🫧|\*[^*]*\*)\s*~?\s*$")


def lignes_utiles(src, zone):
    """Lignes sans commentaires ni lignes vides ; sans les lignes d'entrée ; zone 'calcul' ou 'complet'."""
    vues = set()
    sortie = []
    for brut in src.splitlines():
        ligne = RE_COMMENT.sub("", brut).strip()
        if not ligne:
            continue
        m = RE_ENTREE.match(ligne)
        if m and m.group(1) not in vues:  # seule la 1re affectation de chaque variable est remplacée
            vues.add(m.group(1))
            continue
        if zone == "calcul" and (ligne.startswith("(+o") or RE_AFFECT_CHAINE.match(ligne)):
            continue
        sortie.append(re.sub(r"\s+", " ", ligne))
    return sortie


# --------------------------------------------------------------------------- tokens
SPEC_TOKENS = [
    ("STR", r"🫧[^🫧]*🫧|\*(?=[^\W\d])[^*\n]*\*"),
    ("NLIT", r"<[°o][{}()]+><"),
    ("LIT", r"><[{}()]+[°o]>"),
    ("IF", r"><\(\(\(\^>"),
    ("ELSE", r"><\(\(\(\*>"),
    ("OPEN", r"><>"),
    ("CLOSE", r"<><"),
    ("INC", r">><\w+>"),
    ("DEC", r"<\w+><<"),
    ("ID", r"><\w+>"),
    ("NID", r"<\w+><"),
    ("CALL", r"\[>\(\w+\)"),
    ("FUNC", r">\(\w+\)"),
    ("LOOP", r"🌀|@"),
    ("RET", r"<~"),
    ("PRINT", r"\(\+o"),
    ("GE", r"o≈|o="),
    ("LE", r"≈o|=o"),
    ("GT", r"o~"),
    ("LT", r"~o"),
    ("OP", r"&&|\|\||!!|</3|<3|♡|💔|>>|<<|&|\||!|-|\+|\*|/"),
    ("ASSIGN", r"≈|="),
    ("END", r"~"),
    ("PUNCT", r"[()\[\],]"),
    ("WORD", r"[^\W\d]\w*|\d+"),
    ("AUTRE", r"\S"),
]
RE_TOKENS = re.compile("|".join(f"(?P<{n}>{p})" for n, p in SPEC_TOKENS))


def tokenize(lignes):
    """Liste de (genre, texte). Les lignes sont rejointes par un espace."""
    texte = " ".join(lignes)
    return [(m.lastgroup, m.group()) for m in RE_TOKENS.finditer(texte)]


def abstrait(tok):
    """Forme abstraite d'un token : sans noms de variables ni valeurs de littéraux."""
    g, t = tok
    if g in ("ID", "NID", "WORD"):
        return "ID" if g != "NID" else "NID"
    if g in ("INC", "DEC", "STR", "LIT", "NLIT", "CALL", "FUNC", "GE", "LE", "GT", "LT", "LOOP", "ASSIGN"):
        return g
    return t  # opérateurs, IF, ELSE, OPEN, CLOSE, RET, PRINT, END, ponctuation


STRUCTURELS = {"IF", "ELSE", "LOOP", "OPEN", "CLOSE", "FUNC", "CALL", "RET"}


def squelette(toks):
    """Séquence des seuls tokens de contrôle (forme du flot de contrôle)."""
    return [abstrait(t) for t in toks if t[0] in STRUCTURELS]


# --------------------------------------------------------------------------- distances génériques
def lev(a, b):
    """Distance de Levenshtein entre deux séquences."""
    if len(a) < len(b):
        a, b = b, a
    prec = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cour = [i]
        for j, y in enumerate(b, 1):
            cour.append(min(prec[j] + 1, cour[j - 1] + 1, prec[j - 1] + (x != y)))
        prec = cour
    return prec[-1]


def norm(d, a, b):
    m = max(len(a), len(b))
    return 0.0 if m == 0 else d / m


def lev_norm(a, b):
    return norm(lev(a, b), a, b)


def jaccard_ngrammes(a, b, n=3):
    ga = {tuple(a[i:i + n]) for i in range(len(a) - n + 1)}
    gb = {tuple(b[i:i + n]) for i in range(len(b) - n + 1)}
    if not ga and not gb:
        return 0.0
    return 1 - len(ga & gb) / len(ga | gb)


def cosinus(a, b):
    ca, cb = Counter(a), Counter(b)
    num = sum(ca[k] * cb[k] for k in ca)
    den = math.sqrt(sum(v * v for v in ca.values())) * math.sqrt(sum(v * v for v in cb.values()))
    return 1.0 if den == 0 else max(0.0, 1 - num / den)


def ncd(a, b):
    """Distance de compression normalisée (zlib niveau 9) sur deux chaînes."""
    ca, cb, cab = (len(zlib.compress(x.encode(), 9)) for x in (a, b, a + b))
    return (cab - min(ca, cb)) / max(ca, cb)


def diff_lignes(la, lb):
    return 1 - difflib.SequenceMatcher(None, la, lb, autojunk=False).ratio()


# --------------------------------------------------------------------------- arbre et distance d'édition d'arbres
class Noeud:
    def __init__(self, etiquette):
        self.etiquette = etiquette  # tuple de tokens abstraits
        self.enfants = []


def construire_arbre(toks):
    """Arbre des blocs : chaque bloc (><> … <><) est un noeud ayant pour étiquette son en-tête,
    chaque instruction est une feuille ayant pour étiquette ses tokens abstraits."""
    racine = Noeud(("ROOT",))
    pile = [racine]
    courant = []

    def vider_feuille():
        nonlocal courant
        if courant:
            pile[-1].enfants.append(Noeud(tuple(courant)))
            courant = []

    for t in toks:
        g = t[0]
        if g == "OPEN":
            n = Noeud(tuple(courant) or ("BLOC",))
            courant = []
            pile[-1].enfants.append(n)
            pile.append(n)
        elif g == "CLOSE":
            vider_feuille()
            if len(pile) > 1:
                pile.pop()
        elif g == "END":
            vider_feuille()
        else:
            courant.append(abstrait(t))
    vider_feuille()
    return racine


def taille_arbre(n):
    return 1 + sum(taille_arbre(c) for c in n.enfants)


def profondeur(n):
    return 0 if not n.enfants else 1 + max(profondeur(c) for c in n.enfants)


def distance_arbres(t1, t2):
    """Distance d'édition d'arbres ordonnés (Zhang-Shasha). Coût d'insertion et de suppression : 1.
    Coût de changement d'étiquette : distance de Levenshtein normalisée entre les deux étiquettes (0 à 1)."""
    cache = {}

    def rel(a, b):
        if a == b:
            return 0.0
        k = (a, b)
        if k not in cache:
            cache[k] = lev_norm(a, b)
        return cache[k]

    def preparer(racine):
        noeuds, gauche = [], []

        def dfs(n):
            premier = None
            for c in n.enfants:
                lc = dfs(c)
                if premier is None:
                    premier = lc
            idx = len(noeuds)
            noeuds.append(n.etiquette)
            gauche.append(idx if premier is None else premier)
            return gauche[idx]

        dfs(racine)
        cles = {}
        for i, g in enumerate(gauche):
            cles[g] = i
        return noeuds, gauche, sorted(cles.values())

    n1, l1, k1 = preparer(t1)
    n2, l2, k2 = preparer(t2)
    td = [[0.0] * len(n2) for _ in n1]
    for i in k1:
        for j in k2:
            li, lj = l1[i], l2[j]
            m, n = i - li + 2, j - lj + 2
            fd = [[0.0] * n for _ in range(m)]
            for x in range(1, m):
                fd[x][0] = fd[x - 1][0] + 1
            for y in range(1, n):
                fd[0][y] = fd[0][y - 1] + 1
            for x in range(1, m):
                for y in range(1, n):
                    i1, j1 = li + x - 1, lj + y - 1
                    if l1[i1] == li and l2[j1] == lj:
                        fd[x][y] = min(fd[x - 1][y] + 1, fd[x][y - 1] + 1, fd[x - 1][y - 1] + rel(n1[i1], n2[j1]))
                        td[i1][j1] = fd[x][y]
                    else:
                        p, q = l1[i1] - li, l2[j1] - lj
                        fd[x][y] = min(fd[x - 1][y] + 1, fd[x][y - 1] + 1, fd[p][q] + td[i1][j1])
    return td[-1][-1]


# --------------------------------------------------------------------------- indicateurs de structure
def indicateurs(src):
    lignes = lignes_utiles(src, "calcul")
    toks = tokenize(lignes)
    arbre = construire_arbre(toks)
    ids = {t for g, t in toks if g in ("ID",)} | {re.sub(r"\W", "", t) for g, t in toks if g in ("INC", "DEC", "NID")}
    genres = Counter(g for g, _ in toks)
    ops = {t for g, t in toks if g == "OP"}
    texte = " ".join(lignes)
    return {
        "lignes (calcul)": len(lignes),
        "tokens (calcul)": len(toks),
        "instructions (~)": genres["END"],
        "variables distinctes": len(ids),
        "boucles": genres["LOOP"],
        "si / sinon": f"{genres['IF']} / {genres['ELSE']}",
        "fonction définie": "oui" if genres["FUNC"] else "non",
        "récursion": "oui" if genres["CALL"] and genres["FUNC"] else "non",
        "profondeur max": profondeur(arbre) - 1,
        "opérateurs binaires": " ".join(sorted(o for o in ops if o in ("&", "|", ">>", "<<"))) or "—",
        "arithmétique": " ".join(sorted(o for o in ops if o in ("-", "+", "♡", "💔", "!"))
                                   + (["+ (juxtaposition)"] if re.search(r"><\w+> ><\w+>", texte) else [])
                                   + (["− (nage à gauche)"] if genres["NID"] or genres["NLIT"] else [])) or "—",
    }


# --------------------------------------------------------------------------- mesures
MESURES = [
    # clé, libellé, fonction (a, b) -> distance entre 0 (identiques) et 1 (très différents)
    ("lev_tok", "Levenshtein tokens (bruts)"),
    ("lev_abs", "Levenshtein tokens (abstraits)"),
    ("lev_car", "Levenshtein caractères"),
    ("lignes", "diff par lignes"),
    ("jac3", "Jaccard 3-grammes (abstraits)"),
    ("cos", "cosinus sac de tokens (abstraits)"),
    ("ncd", "NCD zlib (tokens abstraits)"),
    ("squel", "Levenshtein squelette de contrôle"),
    ("arbre", "édition d'arbres (normalisée)"),
]


def preparer_programme(src, zone):
    lignes = lignes_utiles(src, zone)
    toks = tokenize(lignes)
    abst = [abstrait(t) for t in toks]
    arbre = construire_arbre(toks)
    return {
        "lignes": lignes,
        "toks": [t for _, t in toks],
        "abst": abst,
        "car": "".join(t for _, t in toks),
        "squel": squelette(toks),
        "arbre": arbre,
        "taille_arbre": taille_arbre(arbre),
    }


def mesurer(a, b):
    return {
        "lev_tok": lev_norm(a["toks"], b["toks"]),
        "lev_abs": lev_norm(a["abst"], b["abst"]),
        "lev_car": lev_norm(a["car"], b["car"]),
        "lignes": diff_lignes(a["lignes"], b["lignes"]),
        "jac3": jaccard_ngrammes(a["abst"], b["abst"]),
        "cos": cosinus(a["abst"], b["abst"]),
        "ncd": ncd(" ".join(a["abst"]), " ".join(b["abst"])),
        "squel": lev_norm(a["squel"], b["squel"]),
        "arbre": distance_arbres(a["arbre"], b["arbre"]) / max(a["taille_arbre"], b["taille_arbre"]),
    }


def brut_tokens(a, b):
    return lev(a["toks"], b["toks"]), lev(a["abst"], b["abst"])


def calculer(progs, zone):
    prep = {nom: preparer_programme(src, zone) for nom, src in progs.items()}
    noms = list(prep)
    res = {}
    for x, y in itertools.combinations(noms, 2):
        res[(x, y)] = mesurer(prep[x], prep[y])
    return noms, prep, res


def dist(res, x, y, cle):
    if x == y:
        return 0.0
    return res[(x, y)][cle] if (x, y) in res else res[(y, x)][cle]


# --------------------------------------------------------------------------- étalonnage
def variante_renommee(src):
    """p dont on a renommé les variables et la fonction (même programme, autres noms)."""
    for a, b in [("n1", "x"), ("n2", "y"), ("steven", "s"), ("bob", "t"), ("result", "g")]:
        src = src.replace(f"><{a}>", f"><{b}>").replace(f"<{a}><", f"<{b}><")
    return src.replace("(gcd)", "(f)")


def variante_symboles(src):
    """p dont on a échangé les deux écritures équivalentes de l'affectation (≈ et =)."""
    return src.replace(" ≈ ", " @@ ").replace(" = ", " ≈ ").replace(" @@ ", " = ")


# --------------------------------------------------------------------------- sorties
def tableau_md(entetes, lignes):
    s = "| " + " | ".join(entetes) + " |\n|" + "|".join("---" for _ in entetes) + "|\n"
    for l in lignes:
        s += "| " + " | ".join(str(c) for c in l) + " |\n"
    return s


def matrice_md(noms, res, cle):
    lignes = []
    for x in noms:
        lignes.append([x] + [("—" if x == y else f"{dist(res, x, y, cle):.2f}") for y in noms])
    return tableau_md([""] + noms, lignes)


def classement(noms, res, cle):
    """Rang (1 = le plus proche de p) de chaque proposition pour une mesure."""
    autres = noms[1:]
    ordre = sorted(autres, key=lambda n: dist(res, "p (moi)", n, cle))
    return {n: i + 1 for i, n in enumerate(ordre)}


def ecrire_csv(chemin, entetes, lignes):
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(entetes)
        w.writerows(lignes)


def heatmap(noms, res, cle, chemin, titre):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(noms)
    m = [[dist(res, x, y, cle) for y in noms] for x in noms]
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    im = ax.imshow(m, cmap="viridis_r", vmin=0, vmax=1)
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(noms, rotation=40, ha="right"); ax.set_yticklabels(noms)
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{m[i][j]:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if m[i][j] > 0.55 else "black")
    ax.set_title(titre, fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="distance (0 = identiques)")
    fig.tight_layout()
    fig.savefig(chemin, dpi=150)
    plt.close(fig)


def main():
    os.makedirs(SORTIE, exist_ok=True)
    progs = charger()
    md = ["# Résultats des mesures de distance\n",
          "Généré par `analyse/distance.py`. Distances entre 0 (identiques) et 1 (sans rien de commun), "
          "sauf mention contraire. Zone « calcul » = programme sans commentaires, sans les lignes d'entrée, "
          "sans les affichages ni les affectations de chaînes imposés par `SPEC.md`.\n"]

    # ---- indicateurs
    ind = {n: indicateurs(s) for n, s in progs.items()}
    cles = list(next(iter(ind.values())))
    md.append("## 1. Indicateurs de structure (zone « calcul »)\n")
    md.append(tableau_md([""] + list(progs), [[c] + [ind[n][c] for n in progs] for c in cles]))
    ecrire_csv(os.path.join(SORTIE, "indicateurs.csv"), [""] + list(progs), [[c] + [ind[n][c] for n in progs] for c in cles])

    res_par_zone = {}
    for zone, titre in (("calcul", "zone « calcul »"), ("complet", "programme complet (hors commentaires et lignes d'entrée)")):
        noms, prep, res = calculer(progs, zone)
        res_par_zone[zone] = (noms, prep, res)
        lignes_csv = [[x, y] + [round(res[(x, y)][k], 4) for k, _ in MESURES] for (x, y) in res]
        ecrire_csv(os.path.join(SORTIE, f"paires_{zone}.csv"), ["a", "b"] + [k for k, _ in MESURES], lignes_csv)

    # ---- p contre chaque proposition
    for zone, num in (("calcul", 2), ("complet", 3)):
        noms, prep, res = res_par_zone[zone]
        titre = "zone « calcul »" if zone == "calcul" else "programme complet"
        md.append(f"## {num}. Distance de p aux propositions : {titre}\n")
        lignes = []
        for n in noms[1:]:
            l = [n] + [f"{dist(res, 'p (moi)', n, k):.2f}" for k, _ in MESURES]
            lignes.append(l)
        moy = ["**moyenne**"] + [f"{sum(dist(res, 'p (moi)', n, k) for n in noms[1:]) / len(noms[1:]):.2f}" for k, _ in MESURES]
        lignes.append(moy)
        md.append(tableau_md(["proposition"] + [lib for _, lib in MESURES], lignes))
        if zone == "calcul":
            md.append("Distances brutes (nombre d'opérations d'édition) sur la zone « calcul » :\n")
            lb = []
            for n in noms[1:]:
                d_raw, d_abs = brut_tokens(prep["p (moi)"], prep[n])
                lb.append([n, len(prep["p (moi)"]["toks"]), len(prep[n]["toks"]), abs(len(prep["p (moi)"]["toks"]) - len(prep[n]["toks"])), d_raw, d_abs])
            md.append(tableau_md(["proposition", "tokens de p", "tokens de p'", "minimum dû à l'écart de taille", "édition (bruts)", "édition (abstraits)"], lb))

    noms, prep, res = res_par_zone["calcul"]
    # ---- classements
    md.append("## 4. Classement des propositions par proximité à p (zone « calcul »)\n")
    md.append("Rang 1 = la plus proche de p. Un classement stable d'une mesure à l'autre indique que la conclusion ne dépend pas de la mesure.\n")
    rangs = {k: classement(noms, res, k) for k, _ in MESURES}
    md.append(tableau_md(["proposition"] + [k for k, _ in MESURES],
                         [[n] + [rangs[k][n] for k, _ in MESURES] for n in noms[1:]]))
    ecrire_csv(os.path.join(SORTIE, "classement.csv"), ["proposition"] + [k for k, _ in MESURES],
               [[n] + [rangs[k][n] for k, _ in MESURES] for n in noms[1:]])

    # ---- p contre LLM / LLM contre LLM
    md.append("## 5. Les LLM se ressemblent-ils entre eux ? (zone « calcul »)\n")
    md.append("Moyenne des distances p–LLM, puis LLM–LLM (toutes paires de propositions), puis plus proche voisin de chaque proposition.\n")
    llm = noms[1:]
    paires_llm = list(itertools.combinations(llm, 2))
    lignes = []
    for k, lib in MESURES:
        dp = sum(dist(res, "p (moi)", n, k) for n in llm) / len(llm)
        dl = sum(dist(res, a, b, k) for a, b in paires_llm) / len(paires_llm)
        lignes.append([lib, f"{dp:.2f}", f"{dl:.2f}", f"{dl - dp:+.2f}"])
    md.append(tableau_md(["mesure", "moyenne p–LLM", "moyenne LLM–LLM", "écart (LLM–LLM) − (p–LLM)"], lignes))
    md.append("Plus proche voisin (mesure : Levenshtein tokens abstraits ; p inclus parmi les candidats) :\n")
    lignes = []
    for n in noms:
        cand = sorted((x for x in noms if x != n), key=lambda x: dist(res, n, x, "lev_abs"))
        lignes.append([n, cand[0], f"{dist(res, n, cand[0], 'lev_abs'):.2f}"])
    md.append(tableau_md(["programme", "plus proche voisin", "distance"], lignes))

    md.append("LLM–LLM en ne gardant qu'une proposition par modèle (sans glm-1, première tentative de glm-2) :\n")
    sans = [n for n in llm if n != "glm-1"]
    paires_sans = list(itertools.combinations(sans, 2))
    lignes = []
    for k, lib in MESURES:
        dp = sum(dist(res, "p (moi)", n, k) for n in sans) / len(sans)
        dl = sum(dist(res, a, b, k) for a, b in paires_sans) / len(paires_sans)
        lignes.append([lib, f"{dp:.2f}", f"{dl:.2f}", f"{dl - dp:+.2f}"])
    md.append(tableau_md(["mesure", "moyenne p–LLM", "moyenne LLM–LLM", "écart (LLM–LLM) − (p–LLM)"], lignes))

    # ---- étalonnage
    md.append("## 6. Étalonnage des mesures (zone « calcul »)\n")
    md.append("Distance de p à deux variantes qui ne changent ni l'algorithme ni la structure : "
              "(a) mêmes instructions avec d'autres noms de variables et de fonction ; "
              "(b) affectations réécrites avec l'autre symbole équivalent (`≈` ↔ `=`). "
              "Une bonne mesure structurelle doit donner ≈ 0 pour ces deux cas.\n")
    base = preparer_programme(progs["p (moi)"], "calcul")
    var = {"(a) noms changés": variante_renommee(progs["p (moi)"]),
           "(b) ≈ ↔ =": variante_symboles(progs["p (moi)"])}
    lignes = []
    for nom, src in var.items():
        m = mesurer(base, preparer_programme(src, "calcul"))
        lignes.append([nom] + [f"{m[k]:.2f}" for k, _ in MESURES])
    md.append(tableau_md(["variante de p"] + [lib for _, lib in MESURES], lignes))

    # ---- matrices complètes
    md.append("## 7. Matrices complètes (zone « calcul »)\n")
    for k, lib in MESURES:
        if k in ("lev_tok", "lev_abs", "arbre", "jac3"):
            md.append(f"### {lib}\n")
            md.append(matrice_md(noms, res, k))

    with open(os.path.join(SORTIE, "distances.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))

    if "--heatmap" in sys.argv:
        heatmap(noms, res, "lev_abs", os.path.join(SORTIE, "matrice_lev_abs.png"),
                "Levenshtein sur tokens abstraits (zone « calcul »)")
        heatmap(noms, res, "arbre", os.path.join(SORTIE, "matrice_arbre.png"),
                "Édition d'arbres normalisée (zone « calcul »)")
    print("écrit dans", SORTIE)


if __name__ == "__main__":
    main()
