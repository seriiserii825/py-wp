#!/usr/bin/env bash
set -euo pipefail

JSON="${1:?Usage: ./json-acf-delete-single-group.sh path/to/file.json}"

# 1) Достаём post_name группы, чтобы найти её пост в БД
group_key="$(jq -r '(if type=="array" then . else [.] end) | .[0].key' "$JSON")"

group_id="$(wp post list --post_type=acf-field-group --name="$group_key" --field=ID --posts_per_page=1)"

if [ -z "$group_id" ]; then
  echo "No existing group '$group_key' in WordPress, nothing to delete."
  exit 0
fi

# 2) Собираем всё дерево acf-field постов группы. sub_fields (group/repeater/tab)
#    вложены через post_parent на несколько уровней, поэтому идём уровень за
#    уровнем от группы вниз, а не одним запросом по post_parent=group_id.
all_ids=("$group_id")
frontier=("$group_id")

while [ "${#frontier[@]}" -gt 0 ]; do
  next_frontier=()
  for parent_id in "${frontier[@]}"; do
    while IFS= read -r child_id; do
      [ -n "$child_id" ] && next_frontier+=("$child_id")
    done < <(wp post list --post_type=acf-field --post_parent="$parent_id" --field=ID)
  done
  if [ "${#next_frontier[@]}" -eq 0 ]; then
    break
  fi
  all_ids+=("${next_frontier[@]}")
  frontier=("${next_frontier[@]}")
done

wp post delete "${all_ids[@]}" --force
echo "Deleted group '$group_key' (${#all_ids[@]} posts)."
