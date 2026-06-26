#!/usr/bin/env bash
set -euo pipefail

JSON="${1:?Usage: ./fix-order.sh path/to/file.json}"

# 1) Получаем префикс таблиц WP
prefix="$(wp db prefix)"

# 1b) Достаём post_name группы (для проверочного SELECT в конце)
group_name="$(jq -r '(if type=="array" then . else [.] end) | .[0].key' "$JSON")"

# 2) Рекурсивно обходим все поля (включая sub_fields внутри group/repeater/tab).
#    Каждое поле отдаёт свой ключ + позицию среди СВОИХ сиблингов (= menu_order для этого уровня).
#    to_entries на массиве даёт {key: index, value: field_obj} — .key это и есть порядковый номер.
readarray -t PAIRS < <(jq -r '
  def recurse_fields:
    ((.fields // []) + (.sub_fields // [])) |
    to_entries[] |
    (.key as $i | .value | [.key, ($i | tostring)], recurse_fields);

  (if type=="array" then . else [.] end)[] | recurse_fields | @tsv
' "$JSON")

[ "${#PAIRS[@]}" -gt 0 ] || { echo "No fields in JSON, skipping menu_order update"; exit 0; }

# 3) Генерим один SQL-пакет и применяем
tmp="$(mktemp)"
{
  echo "START TRANSACTION;"
  for pair in "${PAIRS[@]}"; do
    field_key="${pair%%$'\t'*}"
    order="${pair##*$'\t'}"
    printf "UPDATE %sposts SET menu_order=%s WHERE post_type='acf-field' AND post_name='%s';\n" \
      "$prefix" "$order" "$field_key"
  done
  echo "COMMIT;"
} > "$tmp"

wp db query < "$tmp"
rm -f "$tmp"

# 4) Быстрая проверка верхнего уровня (ORDER BY menu_order, ID)
wp db query "SELECT post_title, post_name, menu_order, ID
FROM ${prefix}posts
WHERE post_type='acf-field' AND post_parent=(
  SELECT ID FROM ${prefix}posts
  WHERE post_type='acf-field-group' AND post_name='${group_name}'
)
ORDER BY menu_order, ID;"
