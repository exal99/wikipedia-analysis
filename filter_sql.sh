#! /usr/bin/env bash

gunzip --stdout < "database/$1wiki-$2-page.sql.gz" \
	| sed -n 's/^INSERT INTO `page` VALUES (//p' \
	| sed -e 's/),(/\n/g' \
	| egrep "^[0-9]+,0," \
	| sed -re "s/^([0-9]+),0,('(\\\'|[^'])*'),'[^']*',[0-9]+,([01]).*/\1,\2,\4/" \
	| tee >(perl -ne 'print STDERR "\rCurrent id: $1       " if /^(\d+)/') \
	| gzip -c --fast > "database/$1wiki-$2-page.sql.gz.tmp"

		
#	| gzip -c > "database/$1wiki-$2-page.sql.gz.tmp"
	


# 30668,0,'The_Lord\'s_Supper','',331,1,0,0.586246820712692,'20180722160246',NULL,565580949,23,'wikitext',NULL

# 27306,0,'Seychelles_People\'s_Defence_Force','',58,0,0,0.435548723149624,'20180727203721','20180727203721',852281365,4701,'wikitext',NULL
