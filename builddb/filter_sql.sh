#! /usr/bin/env bash


if [ "$#" -ne 2 ]; then
	echo "[Error] Requires a language code and a date"
	exit 1
fi


echo "[Info] Formatting 'pagelinks' file"

pigz -dc < "database/$1wiki-$2-pagelinks.sql.gz" \
	| sed -n 's/^INSERT INTO `pagelinks` VALUES (//p' \
	| sed -e 's/),(/\n/g' \
	| egrep "^[0-9]+,0,'(\\\\'|[^'])*',0" \
	| sed -re "s/^([0-9]+),0,('(\\\'|[^'])*').*/\1\t\2/" \
	| pigz -c --fast > "database/$1wiki-$2-pagelinks.sql.gz.tmp"

mv "database/$1wiki-$2-pagelinks.sql.gz.tmp" "database/$1wiki-$2-pagelinks.sql.gz"
echo "Done"
echo

echo "[Info] Formatting 'redirect' file"

pigz -dc < "database/$1wiki-$2-redirect.sql.gz" \
	| sed -n 's/^INSERT INTO `redirect` VALUES (//p' \
	| sed -e 's/),(/\n/g' \
	| egrep "^[0-9]+,0," \
	| sed -re "s/^([0-9]+),0,('(\\\'|[^'])*').*/\1\t\2/" \
	| gzip -c --fast > "database/$1wiki-$2-redirect.sql.gz.tmp"

mv "database/$1wiki-$2-redirect.sql.gz.tmp" "database/$1wiki-$2-redirect.sql.gz"
echo "Done"
echo

echo "[Info] Formating 'page' file"

pigz -dc < "database/$1wiki-$2-page.sql.gz" \
	| sed -n 's/^INSERT INTO `page` VALUES (//p' \
	| sed -e 's/),(/\n/g' \
	| egrep "^[0-9]+,0," \
	| sed -re "s/^([0-9]+),0,('(\\\'|[^'])*'),'[^']*',[0-9]+,([01]).*/\1\t\2\t\4/" \
	| pigz -c --fast > "database/$1wiki-$2-page.sql.gz.tmp"

mv "database/$1wiki-$2-page.sql.gz.tmp" "database/$1wiki-$2-page.sql.gz"
echo "Done"
echo

./filter_redirects.py "database/$1wiki-$2-page.sql.gz" "database/$1wiki-$2-redirect.sql.gz"
mv "database/$1wiki-$2-redirect.sql.gz.tmp" "database/$1wiki-$2-redirect.sql.gz"
mv "database/$1wiki-$2-page.sql.gz.tmp" "database/$1wiki-$2-redirect.sql.gz"

./filter_pagelinks.py "database/$1wiki-$2-page.sql.gz" "database/$1wiki-$2-redirect.sql.gz" "database/$1wiki-$2-pagelinks.sql.gz"
mv "database/$1wiki-$2-pagelinks.sql.gz.tmp" "database/$1wiki-$2-redirect.sql.gz"