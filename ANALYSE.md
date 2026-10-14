# Analyse

## 1. Sémantique : p' calcule-t-il la même chose que p ?

| Essai | Modèle | Proposition | Tests réussis | Remarque |
|-------|--------|-------------|---------------|----------|
| 1 | Claude Haiku 5.5 (effort faible) | `p_claude-haiku-5-5-faible_1.fysh` | 18/18 | |
| 2 | Claude Sonnet 5.5 (effort moyen) | `p_claude-sonnet-5-5-moyen_1.fysh` | 18/18 | |
| 3 | Gemini 3.5 Flash-Lite (effort moyen) | `p_gemini-moyen_1.fysh` | 0/18 | sortie vide : syntaxe qui n'existe pas en Fysh (`> a ≈ number1 ~`, commentaires `#`) |
| 4 | Gemini 2.5 Flash (effort max) | `p_gemini-max_1.fysh` | 0/18 | erreur d'analyse (`expected fysh {, got INVALID`) |
| 5 | Mistral Le Chat, modèle GLM | `p_glm_1.fysh` | 0/18 | plantage de l'interpréteur sur les chaînes `*and*` et `*is*` (forme donnée par la page Esolang, refusée par la v0.0.5) |
| 6 | idem, 2e essai (manuel officiel fourni) | `p_glm_2.fysh` | 18/18 | chaînes `🫧…🫧` et boucle `🌀` |

Les 18 tests (3 visibles dans `SPEC.md`, 15 jamais vus par les LLM) couvrent les zéros, l'égalité, l'ordre inversé,
les puissances de 2, deux nombres pairs, des nombres de Fibonacci consécutifs et la borne 2 147 483 647. Pour aller
au-delà, on s'appuie sur la nature des algorithmes : les trois programmes valides suivent Euclide ou Stein, des
méthodes classiques dont la correction est connue. Cela donne une bonne confiance, pas une preuve.

Ce qui rend la tâche difficile :

- **Pas de modulo documenté** (ni d'opérateur d'égalité, d'après Sonnet). Les LLM reconstruisent Euclide par décalages
  ou par soustractions (Haiku, GLM), ou changent d'algorithme (Sonnet, Stein) : le code est plus long et plus risqué.
- **Une documentation incohérente.** Le séparateur d'arguments d'un appel est `-` dans le texte du wiki et `*` dans son
  exemple, les chaînes s'écrivent `*…*` sur le wiki et `🫧…🫧` sur le site officiel, et les comparaisons `≥` et `≤`
  n'ont pas la même orthographe d'une source à l'autre. GLM a suivi le wiki au premier essai et a fait planter
  l'interpréteur ; il a corrigé après lecture du manuel.
- **Une syntaxe peu illustrée, sans pouvoir tester.** La soustraction d'une variable et l'imbrication des blocs
  reviennent dans les doutes de Haiku, de Sonnet et de GLM. Les LLM n'avaient pas le droit d'exécuter leur code : les
  erreurs de syntaxe des deux Gemini n'ont pas pu être détectées.

## 2. Syntaxe : p' ressemble-t-il à p ?

Un `diff` ne convient pas ici : le Fysh est de format libre, donc un diff par lignes dépend de la mise en page et des
noms de variables (renommer seulement les variables de `p` donne 0,51), et il distingue à peine les propositions
(entre 0,72 et 0,93 pour les six).

### 2.1 Mesures

Chaque programme est découpé en tokens Fysh (littéraux, variables, mots-clés comme `><(((^>` ou `<~`, opérateurs).
Les commentaires, les espaces et les deux lignes d'entrée sont ignorés. La comparaison porte sur la **zone « calcul »** :
sans les affichages ni les affectations de chaînes imposés par `SPEC.md`, presque identiques dans tous les programmes et
qui rapprocheraient artificiellement les propositions de `p`. Les distances sont normalisées par la taille du plus long
des deux programmes : 0 pour deux programmes identiques, 1 s'ils n'ont rien en commun.

| Mesure | Définition | Pourquoi ce choix | Limite |
|--------|------------|-------------------|--------|
| Distance d'édition sur les tokens (bruts) | nombre minimal d'insertions, de suppressions et de remplacements de tokens pour passer de `p` à `p'` | c'est la mesure suggérée par l'énoncé | sensible au choix des noms de variables |
| Distance d'édition sur les tokens (abstraits) | même calcul, après avoir remplacé les noms de variables par `ID`, les valeurs de littéraux par `LIT` et unifié les écritures équivalentes (`≈`/`=`, `🌀`/`@`) | **mesure principale** : elle reflète la structure et l'ordre des instructions, pas le vocabulaire | ignore les noms et les valeurs |
| Distance sur le squelette de contrôle | même calcul sur la seule suite des mots-clés de contrôle (`if`, `else`, boucles, blocs, appels, retours) | isole la forme du programme, par exemple récursion ou boucles | ne voit pas le calcul à l'intérieur des blocs |

Étalonnage : renommer les variables et la fonction de `p` (le même programme) donne 0,26 en tokens bruts, mais 0,00 en
tokens abstraits et en squelette. Six autres mesures (caractères, diff par lignes, Jaccard sur 3-grammes, cosinus,
compression, édition d'arbres) ont été calculées comme vérifications croisées (`analyse/resultats/distances.md`) : elles
donnent la même conclusion.

### 2.2 Résultats

**Algorithme utilisé**

| Programme | Algorithme | Structure |
|-----------|------------|-----------|
| p | Stein (PGCD binaire) : parité avec `& 1`, décalages `>> 1`, soustractions | récursion, aucune boucle |
| haiku | Euclide, modulo reconstruit par décalages | boucles |
| sonnet | Stein | itératif : boucles et copies des opérandes |
| gemini-1 | Euclide par soustractions successives (d'après sa réponse) | boucle, programme invalide |
| gemini-2 | Euclide avec modulo `a − (a/b)·b` (d'après sa réponse) | fonction et boucle, programme invalide |
| glm-1, glm-2 | Euclide, modulo par soustraction doublante | boucles |

Cinq propositions sur six prennent Euclide, l'algorithme « spontané ». Seul Sonnet choisit Stein, comme `p`.

**Indicateurs de structure (zone « calcul »)**

| | p | haiku | sonnet | gemini-1 | gemini-2 | glm-1 | glm-2 |
|---|---|---|---|---|---|---|---|
| lignes | 45 | 24 | 54 | 14 | 11 | 20 | 27 |
| tokens | 183 | 86 | 194 | 46 | 59 | 73 | 96 |
| instructions | 15 | 12 | 27 | 5 | 7 | 11 | 18 |
| variables | 9 | 9 | 10 | 0 | 4 | 8 | 13 |
| boucles | 0 | 3 | 3 | 1 | 1 | 3 | 3 |
| si / sinon | 7 / 7 | 1 / 0 | 4 / 3 | 1 / 1 | 0 / 0 | 0 / 0 | 0 / 0 |
| fonction définie / récursive | oui / oui | non / non | non / non | non / non | oui / non | non / non | non / non |
| profondeur max d'imbrication | 3 | 3 | 4 | 2 | 2 | 3 | 3 |

`gemini-1` et `gemini-2` ne sont pas des programmes Fysh valides : leurs indicateurs décrivent un texte invalide
(`gemini-1` compte 0 variable parce qu'il écrit des identifiants nus).

**Distance de `p` aux propositions, et des LLM entre eux**

| Proposition | Tokens bruts | Tokens abstraits | Squelette de contrôle |
|-------------|--------------|------------------|-----------------------|
| haiku | 0,86 | 0,66 | 0,82 |
| sonnet | 0,84 | 0,63 | 0,57 |
| gemini-1 | 0,91 | 0,82 | 0,84 |
| gemini-2 | 0,89 | 0,77 | 0,86 |
| glm-1 | 0,87 | 0,71 | 0,88 |
| glm-2 | 0,86 | 0,67 | 0,88 |
| **moyenne `p` – LLM** | 0,87 | 0,71 | 0,81 |
| **moyenne LLM – LLM** | 0,73 | 0,59 | 0,50 |

Le plus proche de `p` est Sonnet (0,63 en tokens abstraits). Chaque LLM a au contraire un voisin plus proche parmi les
autres LLM (de 0,27 à 0,59) : `p` est plus isolé qu'aucune proposition. L'écart le plus net porte sur le squelette de
contrôle (0,81 contre 0,50). Les LLM se rapprochent entre eux en partie parce que `glm-1` et `glm-2` viennent de la
même conversation (0,27).

### 2.3 Qu'est-ce qui éloigne p de ce qu'un LLM écrit spontanément ?

- **L'algorithme** : Stein, alors que cinq propositions sur six écrivent Euclide.
- **La structure** : une récursion et une chaîne de 7 `if` et 7 `else`, où les LLM écrivent des boucles (3 pour chaque
  proposition valide) et au plus 4 `if`. Chaque règle de Stein est un bloc séparé, là où un LLM regroupe le calcul
  dans une boucle.
- **La taille** : 183 tokens contre 86 pour Haiku et 96 pour glm-2 (Sonnet, avec 194, est comparable).

### 2.4 Lequel des programmes préférez-vous, et pourquoi ?

Je préfère la version de Sonnet.

- Stein n'utilise ni division ni modulo, seulement des décalages et des soustractions, ce qui convient bien au Fysh, qui n'a pas d'opérateur modulo documenté.
- Sonnet utilise des boucles là où `p` utilise une fonction récursive. Cela évite en principe de surcharger la mémoire (la pile
  d'appels) pour des entiers très grands.
- En contrepartie, ma version est plus lisible et plus facile à comprendre.

### 2.5 Le défi est-il relevé ?

Oui. La proposition la plus proche, Sonnet, est à 0,63 en tokens abstraits (122 opérations d'édition pour 183 et 194
tokens), et même elle, qui choisit aussi Stein, a une autre structure : 3 boucles contre aucune, squelette de contrôle à
0,57. Il n'y a donc pas lieu de changer de couple (`p`, `SPEC.md`). Limites de cette conclusion :

- 6 propositions, un tirage par configuration (deux pour GLM), dont 3 seulement sont valides ;
- un modèle plus fort, ou un agent qui exécute du code, pourrait s'approcher davantage ;
- le découpage en tokens est un choix de ce travail, pas un lexeur officiel.

## 3. Conclusion

Il faut choisir le langage en fonction de la tâche à réaliser, car tous les langages ne sont pas faits pour les mêmes
usages. De plus, un langage qui a peu d'exemples et peu de documentation, comme le Fysh, met les LLM en difficulté :
ils ont du mal à générer du code cohérent et valide.
Dans l'exemple du Fysh, le même calcul (PGCD) s'écrit de manière très différente, notamment parce que le langage ne fournit pas de véritable opérateur de modulo. 
