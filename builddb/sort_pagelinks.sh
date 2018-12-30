#! /usr/bin/env bash


echo "[Info] Sorting 'from_id'"
pigz -dc < "database/$1wiki-$2-pagelinks.sql.gz" \
    | sort -n -t $'\t' -S 80% -k 1,1 \
    | pigz -c --fast > "database/$1wiki-$2-pagelinks_f_id.sql.gz.tmp"
mv "database/$1wiki-$2-pagelinks_f_id.sql.gz.tmp" "database/$1wiki-$2-pagelinks_f_id.sql.gz"

echo "Done"
echo

echo "[Info] Sorting 'target_id'"
pigz -dc < "database/$1wiki-$2-pagelinks.sql.gz" \
    | sort -n -t $'\t' -S 80% -k 2,2 \
    | pigz -c --fast > "database/$1wiki-$2-pagelinks_t_id.sql.gz.tmp"
mv "database/$1wiki-$2-pagelinks_t_id.sql.gz.tmp" "database/$1wiki-$2-pagelinks_t_id.sql.gz"

echo "Done"
echo