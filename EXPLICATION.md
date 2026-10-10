# EXPLICATION — fonctionnement de `p.fysh`

`p.fysh` calcule le PGCD de deux entiers (ici 45 et 36) avec l'**algorithme de Stein**, aussi appelé
PGCD binaire. Il n'utilise ni division euclidienne ni modulo : seulement des tests de parité, des
décalages de bits, des soustractions et des comparaisons.

## 1. L'algorithme

Pour deux entiers naturels `n1` et `n2`, l'algorithme repose sur les règles suivantes, testées dans cet
ordre :

| Règle | Condition | Résultat |
|-------|-----------|----------|
| 1 | `n1 = n2` | `n1` |
| 2 | `n1 = 0` | `n2` |
| 3 | `n2 = 0` | `n1` |
| 4 | `n1` et `n2` pairs | `2 × PGCD(n1/2, n2/2)` |
| 5 | `n1` pair, `n2` impair | `PGCD(n1/2, n2)` |
| 6 | `n1` impair, `n2` pair | `PGCD(n1, n2/2)` |
| 7 | `n1` et `n2` impairs, `n1 > n2` | `PGCD((n1 − n2)/2, n2)` |
| 8 | `n1` et `n2` impairs, `n1 < n2` | `PGCD(n1, (n2 − n1)/2)` |

Pourquoi ces règles sont correctes :

- Si `n2` est impair, il n'a aucun facteur 2 en commun avec `n1` : quand `n1` est pair,
  `PGCD(n1, n2) = PGCD(n1/2, n2)` (règle 5, et symétriquement règle 6). Si les deux nombres sont pairs,
  2 est un diviseur commun et `PGCD(n1, n2) = 2 × PGCD(n1/2, n2/2)` (règle 4).
- Pour deux nombres impairs, `PGCD(n1, n2) = PGCD(n1 − n2, n2)`, et `n1 − n2` est pair. On peut diviser
  cette différence par 2 sans changer le PGCD, car `n2` est impair (règles 7 et 8).
- Les tests de zéro (règles 2 et 3) doivent venir **avant** les tests de parité : 0 est pair et
  `0 / 2 = 0`, donc sans eux `PGCD(0, n2)` avec `n2` impair retomberait indéfiniment sur le même couple
  par la règle 5 (vérifié : l'interpréteur finit par planter sur un débordement de pile).
- La règle 1 est un raccourci (deux nombres égaux donnent immédiatement leur valeur). Elle règle aussi
  `PGCD(0, 0) = 0`.

## 2. Lire les écailles

Un entier s'écrit avec les écailles d'un poisson : `{` et `}` valent 1, `(` et `)` valent 0, et les yeux
(`o` ou `°`) sont décoratifs. On lit les écailles de gauche à droite, bit de poids fort en premier.

| Littéral dans `p.fysh` | Écailles | Binaire | Valeur |
|------------------------|----------|---------|--------|
| `><})}}({°>` (`number1`) | `}` `)` `}` `}` `(` `{` | 101101 | 45 |
| `><{((}))°>` (`number2`) | `{` `(` `(` `}` `)` `)` | 100100 | 36 |
| `><{°>` | `{` | 1 | 1 |
| `><{)°>` | `{` `)` | 10 | 2 |

Les constantes 1 et 2 servent dans le programme : 1 sert de masque pour tester la parité et de nombre
de positions à décaler, 2 sert de facteur à la règle 4.

## 3. Organisation de la mémoire

Il n'y a ni tableau ni boucle : l'algorithme est écrit en **récursion**, et la mémoire de travail est la
pile d'appels.

| Variable | Portée | Rôle |
|----------|--------|------|
| `number1`, `number2` | globale | les deux opérandes (45 et 36) |
| `result` | globale | le PGCD retourné par le premier appel de `gcd` |
| `gcd` | globale (fonction) | PGCD récursif de ses deux paramètres |
| `n1`, `n2` | locale à chaque appel | paramètres de `gcd` |
| `steven`, `bob` | locale à chaque appel | résultat d'un décalage (`steven` = nombre divisé par 2 ou différence divisée par 2, `bob` = second nombre divisé par 2 dans la règle 4) |

Chaque appel de fonction reçoit son propre environnement : une affectation à `steven` ou `bob` crée une
variable dans l'appel en cours et ne touche pas aux appels précédents. On peut donc réutiliser le nom
`steven` pour des rôles différents sans risque d'écrasement.

La profondeur de récursion reste petite. À chaque appel, l'un des deux nombres au moins est (au plus)
divisé par 2 et aucun ne grandit : le nombre d'appels est borné par environ `log2(n1) + log2(n2) + 2`,
soit une soixantaine au plus pour des entiers de 31 bits.

## 4. Les instructions, une par une

| Syntaxe Fysh | Sens | Où dans `p.fysh` |
|--------------|------|------------------|
| `><//> …` | commentaire jusqu'à la fin de la ligne | partout |
| `~` | fin d'instruction | fin de chaque ligne de code |
| `><x> ≈ …` ou `><x> = …` | affectation (`≈` et `=` sont équivalents) | `number1`, `number2`, `steven`, `bob`, `result` |
| `><{((}))°>` | littéral entier en écailles | `number1`, `number2`, constantes 1 et 2 |
| `>(gcd) ><n1> ><n2>` puis `><> … <><` | définition d'une fonction à deux paramètres, corps entre `><>` et `<><` | ligne 11 |
| `[>(gcd) a - b]` | appel de `gcd` avec les arguments `a` et `b` (séparés par `-`) | toutes les récursions et ligne 75 |
| `<~ valeur ~` | retour de la fonction avec une valeur | à la fin de chaque règle |
| `><(((^> [cond]` | `if` | règle 1, et règle 4 (`if` imbriqué dans le test « `n1` pair ») |
| `><(((*>` | `else` | règle 5 (rattaché au `if` imbriqué de la règle 4), règle 8 |
| `><(((*> ><(((^> [cond]` | `else if` | règles 2, 3, 6, 7, et test « `n1` pair » qui ouvre les règles 4 et 5 |
| `o≈` | « supérieur ou égal » | règle 1 |
| `≈o` | « inférieur ou égal » | règle 1 |
| `o~` | « strictement supérieur » | règle 7 |
| `&&` | ET logique | règle 1 |
| `!!` | NON logique (1 si la valeur est 0, sinon 0) | règles 2 à 6 (tests de zéro et de parité) |
| `&` | ET bit à bit | test de parité `n & 1` |
| `>>` | décalage à droite | division par 2 |
| `<3` | multiplication (le cœur) | règle 4 : résultat × 2 |
| `<n2><` | `n2` avec un poisson qui nage vers la gauche : valeur négative | soustraction `n1 − n2` |
| `( … )` | « bocal » : regroupe une expression pour l'évaluer d'abord | conditions, `(n1 − n2) >> 1` |
| `(+o x ~` | affiche `x` suivi d'un saut de ligne | affichage du résultat (et des messages de debug, en commentaire) |
| `🫧texte🫧` | chaîne de caractères | libellés du résultat (et messages de debug) |

Deux idiomes reviennent souvent :

- **Test de parité** : `!!(><n1> & ><{°>)` est vrai quand `n1 & 1 = 0`, c'est-à-dire quand `n1` est pair.
- **Zéro** : `!!><n1>` est vrai quand `n1 = 0`.

## 5. Parcours du programme

1. Lignes 4 et 6 : `number1 = 45` et `number2 = 36`.
2. Lignes 11 à 73 : définition de `gcd` (elle ne s'exécute pas encore).
3. Ligne 75 : `result` reçoit `gcd(number1, number2)`.
4. Lignes 80 à 85 : affichage du résultat, `The GCD of`, `45`, `and`, `36`, `is`, `9`, chacun sur sa
   ligne.

Chaque règle contenait à l'origine un `(+o 🫧…🫧 ~` qui affichait le message de la règle appliquée
(`Both are equals`, `n1 is nul`, `Only n1 is even`, …). Ces lignes ne servent qu'au débogage : elles sont
laissées en commentaire dans `p.fysh` et ne s'exécutent pas quand on lance réellement le programme. Pour
suivre le chemin de l'algorithme, il suffit de retirer le marqueur de commentaire `><//>` en début de ces
lignes.

## 6. Trace sur 45 et 36

| Appel | Règle appliquée | Message de debug (en commentaire) | Appel suivant |
|-------|-----------------|-----------------------------------|---------------|
| `gcd(45, 36)` | 6 : `n1` impair, `n2` pair | `Only n2 is even` | `gcd(45, 18)` |
| `gcd(45, 18)` | 6 | `Only n2 is even` | `gcd(45, 9)` |
| `gcd(45, 9)` | 7 : deux impairs, `45 > 9` | (aucun) | `gcd((45 − 9) >> 1, 9) = gcd(18, 9)` |
| `gcd(18, 9)` | 5 : `n1` pair, `n2` impair | `Only n1 is even` | `gcd(9, 9)` |
| `gcd(9, 9)` | 1 : égalité | `Both are equals` | retourne 9 |

Les retours remontent la pile sans transformation (aucune règle ne modifie le résultat sauf la règle 4,
qui n'intervient pas ici), et `result` vaut 9. Avec les messages de debug réactivés, `fysh p.fysh`
affiche ces quatre messages, dans cet ordre, avant le résultat.

## 7. Le script `run.sh`

`run.sh` exécute un programme Fysh (`p.fysh` ou une proposition du LLM) sur tous les cas de test de
`tests/` et dit s'ils réussissent. Il sert à vérifier mon programme, et le même script servira à juger
les propositions du LLM dans les mêmes conditions.

Comme le Fysh ne sait pas lire d'entrée, le script procède ainsi pour chaque test `tests/NN.in` (deux
entiers décimaux `A B`) :

1. il convertit `A` et `B` en littéraux Fysh (bit 1 → `{`, bit 0 → `(`) ;
2. il recopie le programme dans `build/<programme>_NN.fysh` en remplaçant les deux lignes qui définissent
   `number1` et `number2` par ces littéraux ;
3. il exécute cette copie avec l'interpréteur (commande `fysh`, ou celle donnée par la variable `FYSH`) ;
4. il compare la sortie à `tests/NN.out`, sans tenir compte des espaces en fin de ligne ni des lignes
   vides au début et à la fin, puis affiche `[OK]` ou `[KO]` (avec la différence).

Utilisation :

```bash
./run.sh p.fysh
FYSH=/chemin/vers/fysh ./run.sh llm/p1.fysh
```

Le script termine par le nombre de tests réussis et retourne un code de sortie non nul si un test
échoue. Chaque copie de `build/` peut être relancée à la main avec `fysh build/p_01.fysh`.
