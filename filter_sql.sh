#! /usr/bin/env bash


echo "[Info] Formatting 'pagelinks' file"

gunzip --stdout < "database/$1wiki-$2-pagelinks.sql.gz" \
	| sed -n 's/^INSERT INTO `pagelinks` VALUES (//p' \
	| sed -e 's/),(/\n/g' \
	| egrep "^[0-9]+,0,'(\\\\'|[^'])*',0" \
	| sed -re "s/^([0-9]+),0,('(\\\'|[^'])*').*/\1,\2/" \
	| perl -pe 'print STDERR "\r[Info] Current target: " . substr($1, 0, 30) . "                " if /^\d+,(.*)/' \
	| gzip -c --fast > "database/$1wiki-$2-pagelinks.sql.gz.tmp"

mv "database/$1wiki-$2-pagelinks.sql.gz.tmp" "database/$1wiki-$2-pagelinks.sql.gz"
echo "Done"
echo

echo "[Info] Formatting 'redirect' file"

gunzip --stdout < "database/$1wiki-$2-redirect.sql.gz" \
	| sed -n 's/^INSERT INTO `redirect` VALUES (//p' \
	| sed -e 's/),(/\n/g' \
	| egrep "^[0-9]+,0," \
	| sed -re "s/^([0-9]+),0,('(\\\'|[^'])*').*/\1,\2/" \
	| perl -pe 'print STDERR "\r[Info] Current id: $1       " if /^(\d+)/' \
	| gzip -c --fast > "database/$1wiki-$2-redirect.sql.gz.tmp"

mv "database/$1wiki-$2-redirect.sql.gz.tmp" "database/$1wiki-$2-redirect.sql.gz"
echo "Done"
echo

echo "[Info] Formating 'page' file"

gunzip --stdout < "database/$1wiki-$2-page.sql.gz" \
	| sed -n 's/^INSERT INTO `page` VALUES (//p' \
	| sed -e 's/),(/\n/g' \
	| egrep "^[0-9]+,0," \
	| sed -re "s/^([0-9]+),0,('(\\\'|[^'])*'),'[^']*',[0-9]+,([01]).*/\1,\2,\4/" \
	| perl -pe 'print STDERR "\r[Info] Current id: $1       " if /^(\d+)/' \
	| gzip -c --fast > "database/$1wiki-$2-page.sql.gz.tmp"

mv "database/$1wiki-$2-page.sql.gz.tmp" "database/$1wiki-$2-page.sql.gz"
echo "Done"
echo


