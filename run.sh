#!/usr/bin/env bash
# Usage : ./run.sh <programme.fysh>        (ex. ./run.sh p.fysh, ./run.sh llm/p1.fysh)
#
# Le Fysh ne sait pas lire d'entrée : pour chaque test tests/NN.in ("A B"), on fabrique
# une copie du programme où les deux lignes `><number1> ≈ ... ~` et `><number2> ≈ ... ~`
# sont remplacées par les littéraux binaires de A et B (build/<programme>_NN.fysh),
# puis on exécute cette copie et on compare avec tests/NN.out.
#
# Comparaison : sortie complète du programme, sans les espaces en fin de ligne ni les lignes
# vides au début et à la fin.
#
# Variables d'environnement : FYSH (commande de l'interpréteur, défaut "fysh"),
#                             TIMEOUT (secondes par test, défaut 10).
set -u

PROG="${1:-}"
[ -n "$PROG" ] && [ -f "$PROG" ] || { echo "Usage : $0 <programme.fysh>" >&2; exit 2; }
FYSH="${FYSH:-fysh}"
TIMEOUT="${TIMEOUT:-10}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$DIR/build"
NAME="$(basename "$PROG" .fysh)"
mkdir -p "$BUILD"

command -v "$FYSH" >/dev/null 2>&1 || { echo "Interpréteur introuvable : $FYSH (voir README.md)" >&2; exit 2; }
if command -v timeout >/dev/null 2>&1; then RUN=(timeout "$TIMEOUT" "$FYSH"); else RUN=("$FYSH"); fi

# n (décimal) -> littéral Fysh : 1 -> '{', 0 -> '(' ; ex. 5 -> ><{({°>
to_fysh() {
  local n=$1 bits=""
  if [ "$n" -eq 0 ]; then bits=0; fi
  while [ "$n" -gt 0 ]; do bits="$((n % 2))$bits"; n=$((n / 2)); done
  printf '><%s°>' "$(printf '%s' "$bits" | sed 'y/10/{(/')"
}

# Remplace la 1re ligne d'affectation de number1 et de number2 (voir la section « Entrée » de SPEC.md).
inject() { # $1=fichier source, $2=littéral1, $3=littéral2
  awk -v l1="$2" -v l2="$3" '
    !d1 && /^[ \t]*><number1>[ \t]*(≈|=)/ { print "><number1> ≈ " l1 " ~"; d1=1; next }
    !d2 && /^[ \t]*><number2>[ \t]*(≈|=)/ { print "><number2> ≈ " l2 " ~"; d2=1; next }
    { print }
    END { exit (d1 && d2) ? 0 : 3 }
  ' "$1"
}

# CR supprimés, espaces finaux supprimés, lignes vides du début et de la fin supprimées.
normalize() {
  tr -d '\r' | sed 's/[[:space:]]*$//' | awk '
    { l[NR] = $0 }
    END { a = 1; n = NR
          while (a <= n && l[a] == "") a++
          while (n >= a && l[n] == "") n--
          for (i = a; i <= n; i++) print l[i] }'
}

pass=0; total=0
for infile in "$DIR"/tests/*.in; do
  id="$(basename "$infile" .in)"
  expected="$DIR/tests/$id.out"
  read -r A B < "$infile"
  total=$((total + 1))
  gen="$BUILD/${NAME}_$id.fysh"

  if ! inject "$PROG" "$(to_fysh "$A")" "$(to_fysh "$B")" > "$gen"; then
    echo "[KO] $id  ($A $B)  lignes number1/number2 introuvables dans $PROG (voir la section « Entrée » de SPEC.md)"
    continue
  fi
  raw="$("${RUN[@]}" "$gen" 2>&1)"; rc=$?
  got="$(printf '%s\n' "$raw" | normalize)"
  want="$(normalize < "$expected")"

  if [ "$got" = "$want" ]; then
    pass=$((pass + 1)); echo "[OK] $id  ($A $B)"
  else
    echo "[KO] $id  ($A $B)  code retour = $rc"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/       /'
  fi
done

echo "Résultat : $pass/$total tests réussis ($PROG)"
[ "$pass" -eq "$total" ]
