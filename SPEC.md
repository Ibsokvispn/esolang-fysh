# SPEC — PGCD de deux entiers en Fysh

Langage : **Fysh** (https://esolangs.org/wiki/Fysh).

## 1. Énoncé

Écrire un programme Fysh qui calcule le **plus grand commun diviseur (PGCD)** de deux entiers
naturels `a` et `b`, puis l'affiche au format décrit dans la section « Sortie ».

Le PGCD doit être **calculé par le programme** : la valeur affichée ne peut pas être écrite en dur,
car le même programme sera exécuté avec de nombreux couples `(a, b)` différents. Chaque exécution
doit se terminer en moins de 10 secondes.

## 2. Entrée

Fysh ne possède aucune instruction de lecture : `a` et `b` sont donc fournis **dans le code source**,
selon le contrat suivant.

Le programme commence par deux affectations, chacune **sur une ligne à elle seule**, dans cet ordre,
en dehors de toute fonction, avant le reste du code :

```
><number1> ≈ <littéral entier> ~
><number2> ≈ <littéral entier> ~
```

- `number1` contient `a` et `number2` contient `b`.
- `<littéral entier>` est un entier Fysh écrit avec des écailles binaires (voir la page du langage).
  Exemple : pour `a = 45` (101101 en binaire) et `b = 36` (100100 en binaire) :

  ```
  ><number1> ≈ ><{({{({°> ~
  ><number2> ≈ ><{(({((°> ~
  ```

  L'entier zéro s'écrit par exemple `><(°>`.
- `number1` et `number2` ne sont **jamais réaffectées** ailleurs dans le programme.
- Pour exécuter les tests, ces deux lignes sont **remplacées automatiquement**, en entier, par deux
  autres lignes du même format (les lignes sont repérées par leur début : `><number1>` ou `><number2>`
  suivi de `≈` ou `=`). Le reste du programme ne doit donc dépendre d'aucune valeur particulière de
  `a` ou `b`.

Domaine : `0 ≤ a ≤ 2147483647` et `0 ≤ b ≤ 2147483647` (2³¹ − 1). Les deux entiers peuvent être nuls,
égaux, premiers entre eux, ou donnés dans n'importe quel ordre (`a < b`, `a = b` ou `a > b`).

## 3. Sortie

La sortie standard du programme doit être **exactement les 6 lignes suivantes**, où
`<a>`, `<b>` et `<g>` sont les valeurs de `number1`, `number2` et de leur PGCD, écrites en décimal,
sans signe, sans zéro de tête et sans espace :

```
The GCD of
<a>
and
<b>
is
<g>
```

- `<a>` est la valeur de `number1` et `<b>` celle de `number2`, dans cet ordre (elles ne sont pas
  triées).
- On suppose que chaque instruction d'affichage `(+o` termine sa ligne par un saut de ligne.
- Les espaces en fin de ligne et les lignes vides au début et à la fin de la sortie sont ignorés.

## 4. Définition et cas particuliers

- Pour `a > 0` et `b > 0`, `PGCD(a, b)` est le plus grand entier qui divise à la fois `a` et `b`.
- `PGCD(a, 0) = PGCD(0, a) = a`, pour tout `a ≥ 0`.
- `PGCD(0, 0) = 0`.
- `PGCD(a, a) = a` et `PGCD(a, b) = PGCD(b, a)`.

## 5. Exemples

| `a` | `b` | `PGCD(a, b)` |
|-----|-----|--------------|
| 45 | 36 | 9 |
| 17 | 5 | 1 |
| 0 | 12 | 12 |

Sortie attendue pour `a = 45` et `b = 36` :

```
The GCD of
45
and
36
is
9
```

Sortie attendue pour `a = 17` et `b = 5` :

```
The GCD of
17
and
5
is
1
```

Sortie attendue pour `a = 0` et `b = 12` :

```
The GCD of
0
and
12
is
12
```
