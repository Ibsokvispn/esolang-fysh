# Programmer dans un langage ésotérique : PGCD en Fysh

Exercice DSL · INFO5 · 2026-2027. Le programme `p.fysh` calcule le PGCD de deux entiers.

## 1. Langage choisi

**Fysh**, un langage ésotérique à thème aquatique créé en 2024 par Pointless et PinesLover69.

- Page Esolang : https://esolangs.org/wiki/Fysh (révision consultée : `oldid=196650`, dernière modification
  le 30 septembre 2026)
- Dépôt officiel et documentation : https://github.com/Fysh-Fyve/fysh (voir `pkg/go-fysh/README.md`)

## 2. Interpréteur utilisé

Le Fysh dispose d'une implémentation de référence en Go. Je l'ai utilisée de deux façons :

| Moyen | Lien | Version |
|-------|------|---------|
| Compilateur en ligne (playground) | https://fysh-fyve.github.io/playground/ | — |
| Extension VSCode `Fysh-Fyve.fysh` | https://marketplace.visualstudio.com/items?itemName=Fysh-Fyve.fysh | v1.2.1 |

J'ai téléchargé le binaire `fysh` depuis les releases GitHub du projet (https://github.com/Fysh-Fyve/fysh,
dossier `pkg/go-fysh`). Le bouton « run » de l'extension sur VSCode se contente ensuite de lancer
`fysh <fichier>` dans un terminal. Le binaire est rangé dans le dossier de stockage de l'extension et
n'est pas dans le `PATH`.

On peut également compiler l'interpréteur avec la commande `go install github.com/Fysh-Fyve/fysh/pkg/go-fysh/cmd@latest`
(le binaire obtenu s'appelle `cmd` et correspond au dernier commit du dépôt, plus récent que la release v0.0.5 ;
nécessite `go` d'installé - `sudo snap install go --classic `).


- Version de `fysh` (release GitHub) : v0.0.5
- Chemin du binaire : ~/.config/Code/User/globalStorage/fysh-fyve.fysh/bin
- Système d'exploitation : Linux

## 3. Lancer le programme

Avec le bouton « run » de l'extension VSCode, ou directement avec l'interpréteur :

```bash
fysh p.fysh
```

(remplacer `fysh` par le chemin complet du binaire s'il n'est pas dans le `PATH`, voir la section
précédente). Sortie obtenue :

```
The GCD of
45
and
36
is
9
```

Sur toute la suite de tests :

```bash
./run.sh p.fysh                          # utilise la commande "fysh" du PATH
FYSH=/chemin/vers/fysh ./run.sh p.fysh   # interpréteur à un autre endroit
./run.sh llm/p_claude-sonnet-5-5-moyen_1.fysh   # une proposition d'un LLM
```

Le script affiche `[OK]` ou `[KO]` pour chaque test, puis le nombre de tests réussis, et retourne un code
de sortie non nul si un test échoue.

## 4. Tests

Le Fysh ne sait pas lire d'entrée. Chaque test `tests/NN.in` contient donc deux entiers décimaux
(`A B`), et `run.sh` fabrique, pour chaque test, une copie du programme où les deux lignes
`><number1> ≈ … ~` et `><number2> ≈ … ~` sont remplacées par les littéraux binaires de `A` et `B`.
Cette copie est écrite dans `build/<programme>_NN.fysh` (dossier ignoré par Git) : on peut la relancer
à la main avec `fysh build/p_01.fysh`.

- `tests/NN.out` contient les 6 lignes attendues (voir `SPEC.md`). Elles ont été calculées avec
  `math.gcd` de Python, pas avec `p.fysh`.
- La comparaison porte sur la sortie complète du programme, sans les espaces en fin de ligne ni les
  lignes vides au début et à la fin.
- Les tests 01 à 03 figurent dans `SPEC.md` (le LLM les voit). Les tests 04 à 18 sont cachés au LLM. Ils
  couvrent notamment : opérandes échangés, zéros, égalité, puissances de 2, deux nombres pairs, nombres
  de Fibonacci consécutifs (cas le plus long), et le maximum du domaine (2 147 483 647).
- Les propositions du LLM doivent respecter le contrat d'entrée de `SPEC.md` (section « Entrée » : variables `number1` et
  `number2` sur deux lignes), sans quoi `run.sh` ne peut pas injecter les valeurs de test.

## 5. Points laissés ouverts par la spécification du langage

La page Esolang ne tranche pas plusieurs points. Pour chacun, voici le comportement observé dans
l'implémentation de référence, vérifié par des expériences avec `fysh` v0.0.5 (et lecture du code source).

| Point | Documentation | Comportement observé |
|-------|---------------|----------------------|
| Saut de ligne après `(+o` | non précisé | chaque `(+o` écrit sa valeur suivie d'un saut de ligne |
| Séparateur des arguments d'un appel | le texte dit « fish food `-` », l'exemple utilise `*` | `-` fonctionne ; `*` provoque une erreur. `p.fysh` utilise `-` |
| Taille des entiers | non précisé | entiers signés 64 bits ; un littéral binaire accepte au plus 63 bits (2⁶³ − 1 passe, 2⁶³ donne une erreur d'analyse) |
| Débordement | non précisé | aucune détection : 2⁶² + 2⁶² donne −2⁶³ |
| Littéral zéro | exemple `><(((°>` dans la page | `><(°>` et `><(((°>` valent tous deux 0 |
| Valeur de vérité | non précisé | 0 est faux, tout autre entier est vrai ; `!!` renvoie 1 pour 0 et 0 pour un entier non nul |
| Portée des variables | non précisé | chaque appel de fonction a son environnement local ; une affectation crée la variable dans l'appel en cours, une lecture remonte aux environnements englobants |
| Espaces dans une bulle (chaîne) | non précisé | conservés tels quels (d'où `The GCD of ` avec une espace finale) |
| Entrée | aucune instruction de lecture | impossible de lire stdin ni des arguments |
| Erreur d'exécution | non précisé | message `ERROR: …` écrit sur la sortie standard, exécution arrêtée, code retour 1 |
| Sens des écailles et yeux | sans effet (documenté) | confirmé : `{` et `}` valent 1, `(` et `)` valent 0, `o` et `°` sont décoratifs |

## 6. Contenu du dépôt

| Fichier | Rôle |
|---------|------|
| `p.fysh` | le programme (PGCD par l'algorithme de Stein, commenté) |
| `EXPLICATION.md` | fonctionnement de `p.fysh` : mémoire, récursion, instructions, trace |
| `SPEC.md` | description en langue naturelle de ce que calcule `p.fysh` (reçue par le LLM) |
| `tests/` | cas de test `NN.in` / `NN.out` |
| `run.sh` | exécute un programme sur tous les tests |
| `llm/JOURNAL.md` | journal de la confrontation au LLM |
| `llm/p_<modèle>_<n>.fysh` | propositions des LLM, telles quelles |
| `ANALYSE.md` | analyse du résultat (à remplir) |

Le bonus `interpreteur/` n'est pas réalisé.

## 7. Usage d'outils d'IA

- `p.fysh` a été écrit entièrement par moi, sans LLM ni agent de code.
- J'ai utilisé **Claude (Anthropic, modèle Claude Sonnet 5.5, interface claude.ai)** pour m'aider à produire les autres livrables : brouillons de `README.md`, `EXPLICATION.md` et
  `SPEC.md`, script `run.sh`, génération des fichiers de `tests/` et recherche des comportements de
  l'interpréteur listés dans la section « Points laissés ouverts ». Ces textes ont été relus par moi.
- Pour rédiger `EXPLICATION.md`, Claude a lu `p.fysh`. La confrontation décrite dans `llm/JOURNAL.md`
  a été menée avec plusieurs LLM (dont Claude Haiku 5.5 et Claude Sonnet 5.5), dans des sessions
  distinctes de celle-ci ; les conditions de chaque essai sont décrites dans ce journal.
