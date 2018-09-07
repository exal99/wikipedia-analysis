#! /usr/bin/env bash

gunzip --stdout < "database/$1wiki-$2-page.sql.gz" \
	| sed -n 's/^INSERT INTO `page` VALUES (//p' \
	| sed -e 's/),(/\n/g' \
	| egrep "^[0-9]+,0," \
	| sed -re "s/^([0-9]+),0,('(\\\'|[^'])*'),'[^']*',[0-9]+,([01]).*/\1,\2,\4/" \
	| tee >(perl -ne 'print STDERR "\rCurrent id: $1       " if /^(\d+)/') \
	| gzip -c --fast > "database/$1wiki-$2-page.sql.gz.tmp"

echo
