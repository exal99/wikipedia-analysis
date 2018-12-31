#! /usr/bin/env bash

createdb wikidb

echo "[Info] Creating page table"
psql -f "sql/page_definition.sql" wikidb

pigz -dc < "database/$1wiki-$2-page.sql.gz" \
    | psql -c "COPY page FROM STDIN WITH DELIMITER E'\t' QUOTE '''' ESCAPE '\' CSV;" wikidb

echo "Done"
echo


echo "[Info] Creating redirect table"
psql -f "sql/redirect_definition.sql" wikidb
pigz -dc < "database/$1wiki-$2-redirect.sql.gz" \
    | psql -c "COPY redirect FROM STDIN WITH DELIMITER E'\t' QUOTE '''' ESCAPE '\' CSV;" wikidb

echo "Done"
echo


echo "[Info] Creating links table"
psql -f "sql/links_definition.sql" wikidb
./create_pagelinks.py "database/$1wiki-$2-pagelinks_f_id.sql.gz" "database/$1wiki-$2-pagelinks_t_id.sql.gz" \
    | psql -c "COPY links FROM STDIN WITH DELIMITER E'\t' QUOTE '''' ESCAPE '\' CSV;" wikidb

psql -f "sql/paths_definition.sql" wikidb