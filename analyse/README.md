# Mesures pour ANALYSE.md

Un script Python (bibliothèque standard, plus `matplotlib` pour les graphiques) mesure l'écart syntaxique entre
`p.fysh` et les propositions de `llm/`.

| Script | Question de l'énoncé | Sortie |
|--------|----------------------|--------|
| `distance.py` | Syntaxe : p' ressemble-t-il à p ? | `resultats/distances.md`, `resultats/*.csv`, `resultats/matrice_*.png` |

```bash
python3 analyse/distance.py --heatmap
```

## Pré-traitement (`distance.py`)

1. Les commentaires (`><//> …`, et `# …` que certains LLM ont utilisés) et les lignes vides sont supprimés.
2. Les deux lignes d'entrée (`number1`, `number2`) sont supprimées : `run.sh` les remplace, elles ne font
   pas partie du programme comparé.
3. **Zone « calcul »** (mesure principale) : on retire aussi les zones imposées par `SPEC.md`, c'est-à-dire
   toute ligne d'affichage `(+o …` et toute affectation d'une chaîne à une variable. Ces lignes sont presque
   identiques dans tous les programmes par contrat, et les garder rapprocherait artificiellement toutes les
   propositions de `p`. **Zone « complet »** : on les garde (résultats donnés en complément).
4. Le texte est découpé en tokens Fysh : littéraux (`><{(({°>`), variables (`><x>`), mots-clés (`><(((^>`,
   `><(((*>`, `><>`, `<><`, `<~`, `🌀`, `@`), appels (`[>(gcd)`), chaînes, opérateurs, comparaisons.
   Ce découpage est écrit pour cet exercice, d'après la page du langage et le comportement de l'interpréteur ;
   ce n'est pas le lexeur officiel.

Pour les mesures « abstraites », on remplace les noms de variables par `ID`, les littéraux par `LIT`, les
chaînes par `STR`, et on unifie les écritures équivalentes (`≈`/`=`, `🌀`/`@`).

## Les mesures et pourquoi

| Mesure | Ce qu'elle regarde | Pourquoi / limite |
|--------|--------------------|-------------------|
| Levenshtein sur les tokens (bruts) | le texte des instructions | c'est la mesure proposée par l'énoncé ; très sensible au choix des noms (renommer les variables de `p` suffit à la faire monter à 0,26) |
| **Levenshtein sur les tokens (abstraits)** | la suite d'instructions, sans les noms | **mesure principale** : égale à 0 pour un simple renommage, donc elle reflète la structure |
| Levenshtein sur les caractères | le texte compacté | témoin textuel, plus bruité |
| diff par lignes (`difflib`) | les lignes entières | proche de l'outil `diff`, mais dépend de la mise en page (une instruction par ligne ou non) |
| Jaccard sur les 3-grammes de tokens abstraits | les séquences locales de 3 tokens | robuste si on déplace des blocs entiers |
| cosinus sur le sac de tokens abstraits | le vocabulaire, sans l'ordre | valeurs naturellement basses (tous les programmes utilisent `ID`, `~`, `><>`…) : ne se compare qu'entre propositions |
| NCD (compression zlib) | la redondance commune | indépendant du découpage, mais bruité sur de si petits textes (0,07 même pour deux programmes identiques) |
| Levenshtein sur le squelette de contrôle | la suite des seuls `if`, `else`, boucles, blocs, appels, retours | isole la forme du flot de contrôle (récursion contre boucles) |
| Édition d'arbres (Zhang-Shasha) | l'arbre des blocs imbriqués, instructions aux feuilles | coût d'insertion et de suppression 1, coût de changement d'étiquette = distance entre les deux instructions (0 à 1) ; normalisée par la taille du plus grand arbre |

Toutes les distances normalisées valent 0 pour deux programmes identiques et tendent vers 1 pour deux
programmes sans rien de commun. La normalisation se fait par la taille du plus grand des deux
programmes : un petit programme ne peut donc pas être très proche d'un grand. La table des distances
brutes donne, pour chaque proposition, le minimum imposé par le seul écart de taille.

## Précautions de lecture

- **Étalonnage** (`distances.md`, section 6) : deux variantes de `p` qui ne changent pas la structure (autres noms,
  `≈` à la place de `=`) donnent 0,00 pour les mesures abstraites et pour le squelette. Les mesures « brutes »
  et le diff par lignes réagissent aux noms et à la mise en page.
- **Peu de données** : 6 propositions, dont 2 (`glm-1`, `glm-2`) viennent de la même conversation. La
  comparaison « LLM entre eux » est donnée avec et sans `glm-1`.
- **Programmes invalides** : `gemini-1` et `gemini-2` ne passent pas l'analyse syntaxique ou n'affichent rien.
  Leurs mesures structurelles décrivent un texte qui n'est pas un programme Fysh valide : l'arbre et le
  squelette sont à interpréter avec prudence pour eux.
- **Aucune mesure ne fixe de seuil** « trop proche de p » : la comparaison se fait avec la distance entre les
  LLM eux-mêmes et avec les valeurs d'étalonnage.
