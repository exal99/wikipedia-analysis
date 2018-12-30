#! /usr/bin/env bash

DATE=""

if [ "$#" -eq 2 ]; then
	DATE=$2
	./download_db.sh $1 $2
elif [ "$#" -eq 1 ]; then
	./download_db.sh $1
	DATE=`ls "database/" | sed -rn "s/^enwiki-([0-9]+)-.*$/\1/p" | head -n 1 -q`
else
	echo "[Error] Invalid number of arguments"
	exit 1
fi

./filter_sql.sh $1 $DATE

./sort_pagelinks.sh $1 $DATE

./build_sql.sh $1 $DATE

rm -r database