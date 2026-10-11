# Résultats des mesures de distance

Généré par `analyse/distance.py`. Distances entre 0 (identiques) et 1 (sans rien de commun), sauf mention contraire. Zone « calcul » = programme sans commentaires, sans les lignes d'entrée, sans les affichages ni les affectations de chaînes imposés par `SPEC.md`.

## 1. Indicateurs de structure (zone « calcul »)

|  | p (moi) | haiku | sonnet | gemini-1 | gemini-2 | glm-1 | glm-2 |
|---|---|---|---|---|---|---|---|
| lignes (calcul) | 45 | 24 | 54 | 14 | 11 | 20 | 27 |
| tokens (calcul) | 183 | 86 | 194 | 46 | 59 | 73 | 96 |
| instructions (~) | 15 | 12 | 27 | 5 | 7 | 11 | 18 |
| variables distinctes | 9 | 9 | 10 | 0 | 4 | 8 | 13 |
| boucles | 0 | 3 | 3 | 1 | 1 | 3 | 3 |
| si / sinon | 7 / 7 | 1 / 0 | 4 / 3 | 1 / 1 | 0 / 0 | 0 / 0 | 0 / 0 |
| fonction définie | oui | non | non | non | oui | non | non |
| récursion | oui | non | non | non | oui | non | non |
| profondeur max | 3 | 3 | 4 | 2 | 2 | 3 | 3 |
| opérateurs binaires | & >> | << >> | & << >> | | — | — | — | — |
| arithmétique | - + (juxtaposition) − (nage à gauche) | ! + (juxtaposition) | − (nage à gauche) | 💔 | - | ♡ + (juxtaposition) − (nage à gauche) | ♡ + (juxtaposition) − (nage à gauche) |

## 2. Distance de p aux propositions : zone « calcul »

| proposition | Levenshtein tokens (bruts) | Levenshtein tokens (abstraits) | Levenshtein caractères | diff par lignes | Jaccard 3-grammes (abstraits) | cosinus sac de tokens (abstraits) | NCD zlib (tokens abstraits) | Levenshtein squelette de contrôle | édition d'arbres (normalisée) |
|---|---|---|---|---|---|---|---|---|---|
| haiku | 0.86 | 0.66 | 0.72 | 0.80 | 0.84 | 0.11 | 0.73 | 0.82 | 0.82 |
| sonnet | 0.84 | 0.63 | 0.64 | 0.72 | 0.81 | 0.11 | 0.69 | 0.57 | 0.84 |
| gemini-1 | 0.91 | 0.82 | 0.90 | 0.76 | 0.91 | 0.19 | 0.74 | 0.84 | 0.83 |
| gemini-2 | 0.89 | 0.77 | 0.85 | 0.93 | 0.89 | 0.13 | 0.70 | 0.86 | 0.81 |
| glm-1 | 0.87 | 0.71 | 0.77 | 0.85 | 0.90 | 0.14 | 0.79 | 0.88 | 0.84 |
| glm-2 | 0.86 | 0.67 | 0.72 | 0.86 | 0.89 | 0.15 | 0.81 | 0.88 | 0.92 |
| **moyenne** | 0.87 | 0.71 | 0.77 | 0.82 | 0.87 | 0.14 | 0.74 | 0.81 | 0.84 |

Distances brutes (nombre d'opérations d'édition) sur la zone « calcul » :

| proposition | tokens de p | tokens de p' | minimum dû à l'écart de taille | édition (bruts) | édition (abstraits) |
|---|---|---|---|---|---|
| haiku | 183 | 86 | 97 | 157 | 121 |
| sonnet | 183 | 194 | 11 | 163 | 122 |
| gemini-1 | 183 | 46 | 137 | 166 | 150 |
| gemini-2 | 183 | 59 | 124 | 162 | 140 |
| glm-1 | 183 | 73 | 110 | 160 | 130 |
| glm-2 | 183 | 96 | 87 | 158 | 123 |

## 3. Distance de p aux propositions : programme complet

| proposition | Levenshtein tokens (bruts) | Levenshtein tokens (abstraits) | Levenshtein caractères | diff par lignes | Jaccard 3-grammes (abstraits) | cosinus sac de tokens (abstraits) | NCD zlib (tokens abstraits) | Levenshtein squelette de contrôle | édition d'arbres (normalisée) |
|---|---|---|---|---|---|---|---|---|---|
| haiku | 0.80 | 0.60 | 0.66 | 0.78 | 0.79 | 0.09 | 0.67 | 0.82 | 0.67 |
| sonnet | 0.79 | 0.58 | 0.59 | 0.71 | 0.77 | 0.09 | 0.64 | 0.57 | 0.74 |
| gemini-1 | 0.89 | 0.78 | 0.84 | 0.81 | 0.92 | 0.17 | 0.72 | 0.84 | 0.86 |
| gemini-2 | 0.84 | 0.70 | 0.78 | 0.94 | 0.83 | 0.11 | 0.65 | 0.86 | 0.67 |
| glm-1 | 0.81 | 0.64 | 0.71 | 0.83 | 0.87 | 0.12 | 0.78 | 0.88 | 0.73 |
| glm-2 | 0.81 | 0.62 | 0.67 | 0.84 | 0.87 | 0.13 | 0.79 | 0.88 | 0.85 |
| **moyenne** | 0.82 | 0.65 | 0.71 | 0.82 | 0.84 | 0.12 | 0.71 | 0.81 | 0.76 |

## 4. Classement des propositions par proximité à p (zone « calcul »)

Rang 1 = la plus proche de p. Un classement stable d'une mesure à l'autre indique que la conclusion ne dépend pas de la mesure.

| proposition | lev_tok | lev_abs | lev_car | lignes | jac3 | cos | ncd | squel | arbre |
|---|---|---|---|---|---|---|---|---|---|
| haiku | 2 | 2 | 3 | 3 | 2 | 2 | 3 | 2 | 2 |
| sonnet | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 4 |
| gemini-1 | 6 | 6 | 6 | 2 | 6 | 6 | 4 | 3 | 3 |
| gemini-2 | 5 | 5 | 5 | 6 | 3 | 3 | 2 | 4 | 1 |
| glm-1 | 4 | 4 | 4 | 4 | 5 | 4 | 5 | 5 | 5 |
| glm-2 | 3 | 3 | 2 | 5 | 4 | 5 | 6 | 6 | 6 |

## 5. Les LLM se ressemblent-ils entre eux ? (zone « calcul »)

Moyenne des distances p–LLM, puis LLM–LLM (toutes paires de propositions), puis plus proche voisin de chaque proposition.

| mesure | moyenne p–LLM | moyenne LLM–LLM | écart (LLM–LLM) − (p–LLM) |
|---|---|---|---|
| Levenshtein tokens (bruts) | 0.87 | 0.73 | -0.14 |
| Levenshtein tokens (abstraits) | 0.71 | 0.59 | -0.12 |
| Levenshtein caractères | 0.77 | 0.68 | -0.09 |
| diff par lignes | 0.82 | 0.75 | -0.07 |
| Jaccard 3-grammes (abstraits) | 0.87 | 0.77 | -0.10 |
| cosinus sac de tokens (abstraits) | 0.14 | 0.06 | -0.08 |
| NCD zlib (tokens abstraits) | 0.74 | 0.60 | -0.15 |
| Levenshtein squelette de contrôle | 0.81 | 0.50 | -0.31 |
| édition d'arbres (normalisée) | 0.84 | 0.69 | -0.15 |

Plus proche voisin (mesure : Levenshtein tokens abstraits ; p inclus parmi les candidats) :

| programme | plus proche voisin | distance |
|---|---|---|
| p (moi) | sonnet | 0.63 |
| haiku | glm-1 | 0.34 |
| sonnet | glm-2 | 0.56 |
| gemini-1 | glm-1 | 0.59 |
| gemini-2 | glm-1 | 0.55 |
| glm-1 | glm-2 | 0.27 |
| glm-2 | glm-1 | 0.27 |

LLM–LLM en ne gardant qu'une proposition par modèle (sans glm-1, première tentative de glm-2) :

| mesure | moyenne p–LLM | moyenne LLM–LLM | écart (LLM–LLM) − (p–LLM) |
|---|---|---|---|
| Levenshtein tokens (bruts) | 0.87 | 0.78 | -0.09 |
| Levenshtein tokens (abstraits) | 0.71 | 0.64 | -0.07 |
| Levenshtein caractères | 0.77 | 0.73 | -0.04 |
| diff par lignes | 0.81 | 0.80 | -0.01 |
| Jaccard 3-grammes (abstraits) | 0.87 | 0.81 | -0.05 |
| cosinus sac de tokens (abstraits) | 0.14 | 0.07 | -0.07 |
| NCD zlib (tokens abstraits) | 0.73 | 0.63 | -0.11 |
| Levenshtein squelette de contrôle | 0.79 | 0.56 | -0.24 |
| édition d'arbres (normalisée) | 0.84 | 0.76 | -0.09 |

## 6. Étalonnage des mesures (zone « calcul »)

Distance de p à deux variantes qui ne changent ni l'algorithme ni la structure : (a) mêmes instructions avec d'autres noms de variables et de fonction ; (b) affectations réécrites avec l'autre symbole équivalent (`≈` ↔ `=`). Une bonne mesure structurelle doit donner ≈ 0 pour ces deux cas.

| variante de p | Levenshtein tokens (bruts) | Levenshtein tokens (abstraits) | Levenshtein caractères | diff par lignes | Jaccard 3-grammes (abstraits) | cosinus sac de tokens (abstraits) | NCD zlib (tokens abstraits) | Levenshtein squelette de contrôle | édition d'arbres (normalisée) |
|---|---|---|---|---|---|---|---|---|---|
| (a) noms changés | 0.26 | 0.00 | 0.22 | 0.51 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 |
| (b) ≈ ↔ = | 0.04 | 0.00 | 0.01 | 0.16 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 |

## 7. Matrices complètes (zone « calcul »)

### Levenshtein tokens (bruts)

|  | p (moi) | haiku | sonnet | gemini-1 | gemini-2 | glm-1 | glm-2 |
|---|---|---|---|---|---|---|---|
| p (moi) | — | 0.86 | 0.84 | 0.91 | 0.89 | 0.87 | 0.86 |
| haiku | 0.86 | — | 0.76 | 0.78 | 0.84 | 0.49 | 0.51 |
| sonnet | 0.84 | 0.76 | — | 0.89 | 0.91 | 0.78 | 0.74 |
| gemini-1 | 0.91 | 0.78 | 0.89 | — | 0.80 | 0.77 | 0.78 |
| gemini-2 | 0.89 | 0.84 | 0.91 | 0.80 | — | 0.81 | 0.83 |
| glm-1 | 0.87 | 0.49 | 0.78 | 0.77 | 0.81 | — | 0.33 |
| glm-2 | 0.86 | 0.51 | 0.74 | 0.78 | 0.83 | 0.33 | — |

### Levenshtein tokens (abstraits)

|  | p (moi) | haiku | sonnet | gemini-1 | gemini-2 | glm-1 | glm-2 |
|---|---|---|---|---|---|---|---|
| p (moi) | — | 0.66 | 0.63 | 0.82 | 0.77 | 0.71 | 0.67 |
| haiku | 0.66 | — | 0.64 | 0.64 | 0.62 | 0.34 | 0.39 |
| sonnet | 0.63 | 0.64 | — | 0.82 | 0.80 | 0.66 | 0.56 |
| gemini-1 | 0.82 | 0.64 | 0.82 | — | 0.68 | 0.59 | 0.66 |
| gemini-2 | 0.77 | 0.62 | 0.80 | 0.68 | — | 0.55 | 0.61 |
| glm-1 | 0.71 | 0.34 | 0.66 | 0.59 | 0.55 | — | 0.27 |
| glm-2 | 0.67 | 0.39 | 0.56 | 0.66 | 0.61 | 0.27 | — |

### Jaccard 3-grammes (abstraits)

|  | p (moi) | haiku | sonnet | gemini-1 | gemini-2 | glm-1 | glm-2 |
|---|---|---|---|---|---|---|---|
| p (moi) | — | 0.84 | 0.81 | 0.91 | 0.89 | 0.90 | 0.89 |
| haiku | 0.84 | — | 0.64 | 0.86 | 0.87 | 0.51 | 0.67 |
| sonnet | 0.81 | 0.64 | — | 0.86 | 0.89 | 0.74 | 0.72 |
| gemini-1 | 0.91 | 0.86 | 0.86 | — | 0.89 | 0.87 | 0.88 |
| gemini-2 | 0.89 | 0.87 | 0.89 | 0.89 | — | 0.84 | 0.85 |
| glm-1 | 0.90 | 0.51 | 0.74 | 0.87 | 0.84 | — | 0.50 |
| glm-2 | 0.89 | 0.67 | 0.72 | 0.88 | 0.85 | 0.50 | — |

### édition d'arbres (normalisée)

|  | p (moi) | haiku | sonnet | gemini-1 | gemini-2 | glm-1 | glm-2 |
|---|---|---|---|---|---|---|---|
| p (moi) | — | 0.82 | 0.84 | 0.83 | 0.81 | 0.84 | 0.92 |
| haiku | 0.82 | — | 0.73 | 0.70 | 0.82 | 0.42 | 0.55 |
| sonnet | 0.84 | 0.73 | — | 0.84 | 0.90 | 0.74 | 0.69 |
| gemini-1 | 0.83 | 0.70 | 0.84 | — | 0.84 | 0.61 | 0.73 |
| gemini-2 | 0.81 | 0.82 | 0.90 | 0.84 | — | 0.69 | 0.79 |
| glm-1 | 0.84 | 0.42 | 0.74 | 0.61 | 0.69 | — | 0.34 |
| glm-2 | 0.92 | 0.55 | 0.69 | 0.73 | 0.79 | 0.34 | — |
