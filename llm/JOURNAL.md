# Journal de la confrontation au LLM

Ce journal retrace les essais où des LLM ont tenté d'écrire un programme Fysh à partir de `SPEC.md`, sans jamais voir `p.fysh`.

## 1. Résumé

| Essai | Outil / modèle | Effort | Prompt | Proposition | Tests réussis |
|-------|----------------|--------|--------|-------------|---------------|
| 1 | Claude Haiku 5.5 | faible | Prompt 1 | `llm/p_claude-haiku-5-5-faible_1.fysh` | 18/18 |
| 2 | Claude Sonnet 5.5 | moyen | Prompt 1 | `llm/p_claude-sonnet-5-5-moyen_1.fysh` | 18/18 |
| 3 | Gemini 3.5 Flash-Lite | moyen | Prompt 1 | `llm/p_gemini-moyen_1.fysh` | 0/18 |
| 4 | Gemini 2.5 Flash | max | Prompt 1 | `llm/p_gemini-max_1.fysh` | 0/18 |
| 5 | Mistral Le Chat, modèle GLM (`glm-5-latest-short`) | par défaut | Prompt 1 | `llm/p_glm_1.fysh` | 0/18 |
| 6 | Mistral Le Chat, modèle GLM (`glm-5-latest-short`) | par défaut | Prompt 2 (relance après l'essai 5) | `llm/p_glm_2.fysh` | 18/18 |

- 6 essais avec 5 configurations de modèle ; une seule relance (essai 6, après l'échec de l'essai 5).
- 3 propositions sur 6 passent les 18 tests : essais 1, 2 et 6.
- Essais 5 et 6 : interface https://chat.mistral.ai/work avec le modèle par défaut. Le modèle actif dans la conversation est GLM (`glm-5-latest-short`), qui alimente Vibe, l'agent construit par Mistral, d'où le nom des fichiers `p_glm_*.fysh`.

## 2. Conditions de la confrontation

**Fourni au LLM**

- le nom du langage et le lien vers sa page Esolang (https://esolangs.org/wiki/Fysh) ;
- `SPEC.md` (qui contient les exemples 45 et 36, 17 et 5, 0 et 12) ;
- pour l'essai 6 seulement, en plus : l'accès au manuel du site officiel
  https://fysh-fyve.github.io/docs/category/-fyshing-manual et à ses sous-pages (Prompt 2).

**Interdit au LLM** (consignes du prompt)

- toute recherche autre que la page Esolang (essais 1 à 5), l'accès à la page Git et le téléchargement du langage ;
- l'exécution de code : je teste moi-même les fichiers rendus.

**Non fourni** : `p.fysh`, interpréteur, cas de test (hors les 3 exemples de `SPEC.md`). Les tests 04 à 18 n'ont jamais été vus par les LLM.

**Test des propositions** : chaque proposition est exécutée avec `./run.sh` sur les 18 cas de `tests/`, avec le même interpréteur que `p.fysh` (`fysh` v0.0.5).

**Relances** : aucune, sauf l'essai 6 (Prompt 2, dans la même conversation que l'essai 5, après son échec : « Ce code ne fonctionne pas »). Les essais 3 et 4 (0/18) n'ont pas été relancés.

**Cadre des essais**

- Date : tous les essais ont eu lieu le 10 octobre 2026.
- Outil : les interfaces web des fournisseurs (Mistral : https://chat.mistral.ai/work), sans API.
- Mémoire : désactivée entre les essais. Aucune donnée issue de la session de rédaction des livrables n'était accessible aux LLM.
- Interpréteur des tests : `fysh` v0.0.5.

Les outils étaient manuellement désactivés dans chaque interface (recherche web, exécution de code, agent), en plus de la consigne du prompt les interdisant.

## 3. Prompts exacts

### Prompt 1 (essais 1 à 5)

```text
Je veux que tu écrives un programme dans le langage ésotérique **Fysh** (https://esolangs.org/wiki/Fysh). Toutes les indications sont données dans le fichier SPEC.md .

Ce programme sera nommé "p_<nom du modèle>_<numéro de l'essai>.fysh.

Pour cet essai, tu as juste accès à la page Esolang du langage (donnée précédemment), tu ne peux faire aucune autre recherche, ni accéder à la page git, ni télécharger le langage ni éxecuter du code.
Je m'occuperai moi-même de tester le fichier que tu me rendras.
Explique moi concisément ton mode de pensée et les points sur lesquels tu as des doutes.
```

### Prompt 2 (essai 6)

```text
Ce code ne fonctionne pas. Tu as maintenant le droit d'accéder au site web suivant https://fysh-fyve.github.io/docs/category/-fyshing-manual ainsi qu'à ses sous-pages. 
Il contient également de la documentation qui peut t'aider à corriger ton code.
Pour le moment, tu n'as toujours pas le droit de tester ton code.
```

## 4. Détail des essais

Les réponses des modèles sont reproduites telles quelles textuellement et mises en forme par moi-même pour la lisibilité, dans des blocs repliables. Les programmes sont dans `llm/`, non modifiés.

### Essai 1 : Claude Haiku 5.5, effort faible

- Prompt : Prompt 1
- Proposition : `llm/p_claude-haiku-5-5-faible_1.fysh`
- Résultat : **18/18 tests réussis**

<details>
<summary>Réponse du modèle</summary>

```text
Mode de pensée :

Fysh n'a pas d'opérateur modulo, et la soustraction n'est documentée que de façon ambiguë. J'ai donc construit le programme avec les seules briques que la doc montre clairement :

    - Euclide : tant que y > 0, on remplace (x, y) par (y, x mod y).
    - Modulo : sans division ni modulo, je calcule x mod y par décalages. On double y jusqu'au plus grand y·2^k ≤ x, puis on redescend en retranchant chaque palier quand r ≥ t. Cela ne demande que ~31 itérations par modulo, ce qui évite le coût de la soustraction répétée (qui serait de l'ordre de 2³¹ pour certains couples).
    - Soustraction : r − t s'écrit r + (¬t + 1), avec ! (NOT bit à bit), puis l'incrément >>. On n'utilise donc aucun nombre négatif littéral.
    - Entrées : number1 et number2 ne sont lues qu'une fois, pour initialiser les copies x et y. Les deux lignes d'entrée sont les deux premières du fichier, comme l'exige le SPEC.
    - Sortie : six (+o dans l'ordre demandé, a et b étant les valeurs d'origine.

Points de doute:

    1. Décalage gauche : la doc montre ><steven> << ><(({°> pour le décalage, mais <steven><< pour le décrément. Je suppose que << avec espaces est le décalage. C'est le point le plus fragile.
    2.Chaînes : j'ai choisi les bulles 🫧…🫧 plutôt que *…*, pour éviter la confusion avec le séparateur * des tableaux.
    3. Imbrication des blocs : 🌀, ><(((^> et les ><>…<>< imbriqués ne sont montrés dans la doc que séparément. Je suppose que l'imbrication est permise.
    4. Entiers signés : je suppose que ! et l'addition donnent le complément à deux attendu sur 32 bits. Cela n'a d'importance que si t dépasse 2³⁰, ce que mon test t ≤ x/2 évite normalement.
    5.Affichage : je suppose que (+o imprime en décimal et termine la ligne, comme le SPEC le suppose.
```

</details>

### Essai 2 : Claude Sonnet 5.5, effort moyen

- Prompt : Prompt 1
- Proposition : `llm/p_claude-sonnet-5-5-moyen_1.fysh`
- Résultat : **18/18 tests réussis**

<details>
<summary>Réponse du modèle</summary>

```text
Mon raisonnement :

    - Fysh n'a ni modulo, ni opérateur d'égalité, et la division entière n'est pas garantie par la doc. J'ai donc écarté l'algorithme d'Euclide classique.
    - La soustraction répétée est trop lente pour des valeurs jusqu'à 2³¹−1, par exemple (2147483647, 1).
    - J'ai choisi le PGCD binaire (Stein), qui n'utilise que &, |, >>, la soustraction et les comparaisons ~o / o~. Il fait environ 60 itérations au maximum.
    - number1 et number2 ne sont jamais modifiées. Je travaille sur les copies left et right, car les originaux sont affichés à la fin.
    - Zéros : si left vaut 0, left prend la valeur de right. Ensuite, si right vaut 0, right prend la valeur de left. Si les deux restent nuls, le bloc principal est sauté et le résultat est 0 ♡ 1 = 0. Cela évite une boucle infinie sur (0, 0).
    - Facteurs 2 communs : au lieu d'un décalage par un nombre variable, je double scale à chaque facteur 2 commun. Le résultat final est left ♡ scale.
    - Tests de parité : je calcule x & 1 dans une variable, puis je teste < 1. Je n'ai pas supposé qu'un résultat de & puisse servir directement de condition.
    - Zéro et condition d'arrêt : je compare à un littéral zéro ou un avec ~o et o~, faute d'opérateur d'égalité.
    - Les lignes 1 et 2 sont exactement les affectations imposées, sans commentaire sur la ligne, pour que le remplacement automatique fonctionne.

Points sur lesquels j'ai des doutes :

    1. Soustraction de variable ><right> <left>< : je l'ai déduite des exemples de la doc (<°)})>< pour un littéral, <n><-like pour fib). La doc ne donne pas d'exemple explicite pour une variable. C'est le point le plus fragile, à cause d'une ambiguïté possible avec le décrément <x><<.
    2. Sortie : je suppose que (+o 🫧texte🫧 ~ affiche la chaîne sans guillemets, avec un saut de ligne, et que (+o affiche un entier en décimal.
    3. else if : je ne l'utilise pas. Je n'ai que des if successifs, pour réduire le risque.
    4. Précédence et expressions : je n'ai écrit qu'une seule opération par instruction, sauf l'addition scale scale par juxtaposition, pour doubler scale.
    5. Littéraux : j'utilise ><(({°> pour 1 (exemple de la doc) et ><(°> pour 0 (donné dans la SPEC).
    6. Entiers 32 bits : scale ♡ left ne dépasse jamais le résultat, qui est ≤ 2³¹−1. Je ne sais pas si les entiers sont signés sur 32 bits, mais on reste dans la limite.
    7. Commentaires : ><//> sur ligne dédiée uniquement, car je ne sais pas comment le lexer réagit à un commentaire après du code.
```

</details>

### Essai 3 : Gemini 3.5 Flash-Lite, effort moyen

- Prompt : Prompt 1
- Proposition : `llm/p_gemini-moyen_1.fysh`
- Résultat : **0/18 tests réussis**

<details>
<summary>Réponse du modèle</summary>

```text

Mode de pensée :
    1. Analyse des entrées et contraintes : Le programme reçoit deux entiers number1 et number2 définis au tout début du fichier source par le banc de test. Le corps du programme ne doit faire aucune hypothèse sur leurs valeurs initiales.

    2. Algorithme du PGCD : L'algorithme d'Euclide repose sur la division euclidienne répétée (ou modulo) jusqu'à ce que le second terme devienne nul. Le modulo est exprimé algébriquement par a - (a / b) * b.

    3. Structure en Fysh :
        - Définition d'une fonction sous-marine >(gcd) prenant deux paramètres.
        - Utilisation d'une boucle 🌀 (whirlpool) pour répéter l'opération tant que b > 0.
        - Retour du résultat avec le calmar <~.
        - Utilisation de l'ancre d'affichage (+o combinée avec des chaînes de caractères entre bulles 🫧...🫧 et des variables pour respecter exactement les 6 lignes de sortie exigées.

Points de doute :
    - Syntaxe exacte des paramètres multiples et des fonctions : Bien que la documentation de Fysh décrive la syntaxe des sous-marins >(nom) et des appels via les aquariums [>(nom) - arg1 - arg2], la gestion précise du passage de plusieurs paramètres et de leur portée locale (variables minuscules vs globales) dans les versions actuelles du langage peut être sujette à interprétation subtile.
    - Évaluation des expressions arithmétiques complexes : L'imbrication d'opérations arithmétiques comme a - (a / b) * b dépend de la priorité des opérateurs et de l'utilisation correcte des bols (...) dans Fysh.
    - Comportement des sauts de ligne à l'affichage : L'instruction d'affichage (+o est supposée insérer un saut de ligne automatique par impression, mais la gestion fine des types (affichage d'une variable numérique vs chaîne de caractères) dépend de l'interpréteur officiel.
```

</details>

### Essai 4 : Gemini 2.5 Flash, effort max

- Prompt : Prompt 1
- Proposition : `llm/p_gemini-max_1.fysh`
- Résultat : **0/18 tests réussis**

<details>
<summary>Réponse du modèle</summary>

```text
1. Mode de pensée et conception
Pour écrire un algorithme de calcul de PGCD (plus grand commun diviseur) en Fysh sans pouvoir l'exécuter :

    - Entrées : Le programme doit commencer par les deux lignes obligatoires :

Extrait de code
><number1> ≈ <littéral entier> ~
><number2> ≈ <littéral entier> ~

    - Algorithme d'Euclide : Le moyen le plus robuste de calculer le PGCD est d'utiliser l'algorithme d'Euclide par soustractions successives (ou divisions si l'opérateur modulo/division entière est bien géré, mais les boucles while (🌀) et les conditions (><(((^>, ><(((*>) permettent d'implémenter facilement une boucle while (b != 0) ou while (a != b)).

    - Structure de contrôle :
        - Utilisation de boucles 🌀 avec des conditions de comparaison (> o~ ou >= o≈).
        - Affectations, opérations arithmétiques (soustractions avec des fysh nagant vers la gauche <°)})>< ou division/modulo par cœur brisé 💔).

    - Affichage (Sortie) :
        - La sortie doit respecter strictement le format en 6 lignes requis par la section 3 de SPEC.md :

The GCD of
<a>
and
<b>
is
<g>

        - En Fysh, pour afficher la valeur d'une variable, on utilise l'ancre (+o ou ⚓.

2. Points de doute (incertitudes sur le langage Fysh) :
Étant donné que Fysh est un langage ésotérique très récent (2024) et que je n'ai pas accès à un environnement d'exécution pour tester :

    1. Gestion exacte du modulo et de la division entière : La documentation mentionne le symbole de cœur brisé 💔 pour la division, mais la gestion précise des restes (modulo) pour implémenter l'algorithme d'Euclide rapide (modulo) est incertaine. Par conséquent, il est plus sûr d'utiliser une méthode par soustractions successives (si a > b, a = a - b, sinon b = b - a jusqu'à ce que a == b), ce qui évite les pièges de division.

    2. Syntaxe exacte des blocs conditionnels imbriqués : Bien que la syntaxe des if / else if / else et des boucles 🌀 soit décrite dans le wiki, la portée des variables et l'imbrication des blocs ><> ... <>< peuvent présenter des subtilités syntaxiques non documentées en cas de structures complexes.

    3. Conversion et affichage des variables : L'affichage direct de variables entières en décimal via (+o dépend de l'implémantation de l'interpréteur officiel, en espérant qu'il convertit bien la valeur binaire/interne en décimal lisible tel qu'attendu par le format de sortie (<a>, <b>, <g>).
```

</details>

### Essai 5 : Mistral Le Chat (GLM `glm-5-latest-short`), réglage par défaut

- Prompt : Prompt 1
- Proposition : `llm/p_glm_1.fysh`
- Résultat : **0/18 tests réussis**

<details>
<summary>Réponse du modèle</summary>

```text
Mon mode de pensée :
    - Algorithme — Euclide classique : tant que y > 0 : (x, y) ← (y, x mod y). Comme Fysh n'a pas d'opérateur modulo, je calcule x mod y par soustraction doublante : je retire de r le plus grand y × 2^k qui tient dans r (chaque passage divise r par au moins 2). Complexité ~O(log² n) : environ 2 000 instructions au pire cas (2³¹−1), donc rapide même en interprété. Les cas (0,0), (0,b) et (a,a) tombent juste avec cette boucle.
    - Choisis de syntaxe (uniquement des formes vérifiées par des exemples complets de la doc) :
        - Comparaisons : uniquement o~ (>) et o≈ (>=), toutes deux démontrées dans des exemples de while ;
        - @ [cond] + ><> … <>< pour les boucles ;
        - Addition = banc de fysh (r + neg → ><r> ><neg> ~) ;
        - Chaînes *…* affectées d'abord à des variables (><m1> ≈ *The GCD of* ~), motif exact de la doc, puis 6 (+o.

Mes doutes :
    1. La doc wiki contient une incohérence : elle écrit « 1 » sous la forme (((+œil, ce qui vaut 0 en lecture standard (MSB à gauche, {/}=1). Le SPEC (45→{({{({, 36→{(({(() confirme la lecture standard, donc j'ai traité ça comme une coquille de la wiki — et j'ai conçu le programme pour n'avoir jamais besoin du littéral 1. Je n'utilise que 0 (><(°>, approuvé par le SPEC).
    2. Soustraction d'une variable : la doc ne montre que des littéraux nageant à gauche (<°)})><), jamais une variable. Syntaxe d'une variable inversée = non vérifiable → je contourne : r − t devient r + ((−1) × t), avec −1 écrit en littéral négatif documenté (<°(({><), multiplié par ♡.
    3. Division évitée volontairement : </3 existe mais la sémantique int/float est inconnue (et un float fuiterait dans le résultat). C'est le principal risque que j'ai écarté.
    4. Pas d'opérateur d'égalité dans le langage : j'ai structuré les conditions pour n'utiliser que > et >=.
    5. Boucles imbriquées : aucun exemple imbriqué dans la doc ; je suppose que ><>/<>< se marquent récursivement (comportement standard d'un parseur).
    6. (+o d'une chaîne : jamais montré directement → passe par une variable d'abord (motif documenté).
```

</details>

### Essai 6 : Mistral Le Chat (GLM `glm-5-latest-short`), réglage par défaut

- Prompt : Prompt 2 (relance après l'essai 5)
- Proposition : `llm/p_glm_2.fysh`
- Résultat : **18/18 tests réussis**

<details>
<summary>Réponse du modèle</summary>

```text
Ce que la doc officielle m'a appris :
    1. Chaînes : le site ne documente que 🫧…🫧 pour les bulles ; la forme *…* de la page wiki n'y figure plus (et le séparateur de tableaux a changé de * à -, signe que la doc a été révisée). Mes *The GCD of* de l'essai 1 étaient probablement rejetés → passage à 🫧The GCD of🫧.
    2. Têtards >=/<= : le wiki montrait o≈ / =o, le site montre o= / ≈o. Les deux docs se contredisent sur l'orthographe exacte acceptée par le parseur. Plutôt que de parier, j'ai éliminé >= et <= entièrement : r >= y devient r > y−1 (je décrémente une copie ym = y−1 avec l'instruction documentée <ym><< ~, et je compare avec o~ seul). Idem pour r >= tt via ttm = tt−1 recalculé à chaque tour.
    3. Multiplication avec littéral négatif : ≈ <°(({>< ♡ ><t> (littéral négatif en tête d'expression, écailles ouvrantes) n'est testé nulle part. Je l'ai réécrit en deux motifs exactement vérifiés par les exemples : ><minusOne> ≈ ><(°> <°))}>< ~ (école « fysh à droite + fysh négatif », copie conforme de la soustraction documentée, écailles fermantes comme dans leurs exemples), puis ><neg> ≈ ><t> ♡ ><minusOne> ~ (variable ♡ variable, comme la factorielle officielle).

L'algorithme est inchangé (Euclide + modulo par soustraction doublante, O(log²), rapide jusqu'à 2³¹−1). J'ai aussi remplacé @ par 🌀 et gardé [ ], la forme exacte de l'exemple officiel de factorielle, et je n'utilise plus que des opérateurs présents dans des exemples complets du site : o~, ♡, banc de fysh, <nom><<, (+o, ≈, commentaires ><//>.

Doutes restants :
    - Addition de deux variables (><r> ><neg>) : le site ne montre que littéral+littéral ; la forme variable+variable n'apparaît que dans l'exemple Fibonacci de la vieille page wiki. Syntaxe très probable, mais c'est le point suivant à surveiller.
    - Affichage d'une variable chaîne ((+o ><m1> ~) : la doc montre l'affichage d'entiers seulement.
    - La doc du site reproduit toujours la coquille ((( pour « 1 » (qui vaut 0 en lecture standard) — mes programmes évitent le littéral 1, donc sans impact, mais ça confirme que leurs exemples contiennent des erreurs.
```

</details>
