#!/usr/bin/env bash
set -euo pipefail

JSON="${1:?Usage: ./json-acf-delete-single-group.sh path/to/file.json}"

# 1) Достаём post_name группы, чтобы найти её пост в БД
group_key="$(jq -r '(if type=="array" then . else [.] end) | .[0].key' "$JSON")"

echo "  Looking up group '$group_key' in WordPress..."
group_id="$(wp post list --post_type=acf-field-group --name="$group_key" --field=ID --posts_per_page=1)"

if [ -z "$group_id" ]; then
  echo "  No existing group '$group_key' in WordPress, nothing to delete."
  exit 0
fi

# 2) Собираем всё дерево acf-field постов группы. sub_fields (group/repeater/tab)
#    вложены через post_parent на несколько уровней. Раньше это делалось одним
#    `wp post list` НА КАЖДЫЙ узел дерева — на контейнеризированных установках
#    (Local by Flywheel и т.п.) каждый вызов `wp` это отдельный полный бутстрап
#    WordPress (секунды), и на дереве в 70+ полей набегало 70+ вызовов подряд.
#    Вместо этого забираем ID+post_parent ВСЕХ acf-field постов ОДНИМ вызовом
#    и обходим дерево локально в bash — без единого лишнего вызова `wp`.
echo "  Fetching field tree..."
declare -A children
while IFS=$'\t' read -r id parent; do
  [ -n "$id" ] || continue
  children["$parent"]+="$id "
done < <(wp post list --post_type=acf-field --fields=ID,post_parent --format=json \
  | jq -r '.[] | [.ID, .post_parent] | @tsv')

all_ids=("$group_id")
frontier=("$group_id")
level=1

while [ "${#frontier[@]}" -gt 0 ]; do
  next_frontier=()
  for parent_id in "${frontier[@]}"; do
    if [ -n "${children[$parent_id]+x}" ]; then
      for child_id in ${children[$parent_id]}; do
        next_frontier+=("$child_id")
      done
    fi
  done
  if [ "${#next_frontier[@]}" -eq 0 ]; then
    break
  fi
  echo "  Level $level: found ${#next_frontier[@]} field(s)..."
  all_ids+=("${next_frontier[@]}")
  frontier=("${next_frontier[@]}")
  level=$((level + 1))
done

echo "  Deleting ${#all_ids[@]} post(s)..."
wp post delete "${all_ids[@]}" --force
echo "  Deleted group '$group_key' (${#all_ids[@]} posts)."
