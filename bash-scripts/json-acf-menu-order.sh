#!/usr/bin/env bash
set -euo pipefail

JSON="${1:?Usage: ./fix-order.sh path/to/file.json}"

# 1) Получаем префикс таблиц WP
prefix="$(wp db prefix)"

# 1b) Достаём post_name группы (для проверочного SELECT в конце)
group_name="$(jq -r '(if type=="array" then . else [.] end) | .[0].key' "$JSON")"

# 2) Достаём ключи полей в порядке следования (только верхний уровень .fields)
readarray -t KEYS < <(jq -r '
  (if type=="array" then . else [.] end)
  | .[]
  | select(has("fields") and (.fields|type=="array"))
  | .fields[]
  | select(type=="object" and has("key"))
  | .key
' "$JSON")

[ "${#KEYS[@]}" -gt 0 ] || { echo "No .fields[].key in JSON, skipping menu_order update"; exit 0; }

# 3) Генерим один SQL-пакет и применяем
tmp="$(mktemp)"
{
  echo "START TRANSACTION;"
  i=0
  for key in "${KEYS[@]}"; do
    printf "UPDATE %sposts SET menu_order=%d WHERE post_type='acf-field' AND post_name='%s';\n" "$prefix" "$i" "$key"
    i=$((i+1))
  done
  echo "COMMIT;"
} > "$tmp"

wp db query < "$tmp"
rm -f "$tmp"

# 4) Быстрая проверка (ORDER BY menu_order, ID)
wp db query "SELECT post_title, post_name, menu_order, ID
FROM ${prefix}posts
WHERE post_type='acf-field' AND post_parent=(
  SELECT ID FROM ${prefix}posts
  WHERE post_type='acf-field-group' AND post_name='${group_name}'
)
ORDER BY menu_order, ID;"
