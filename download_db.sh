#!/usr/bin/env bash

# Usage: download_db.sh LANG DATE FILE




#echo $CUR_DIR
#echo "$CUR_DIR/$OUT_DIR"
#echo $URL

CUR_DIR=`pwd`
OUT_DIR="database"

function download_file() {
	FILE_NAME=""
	if [ "$3" != "sha1sums" ]; then
		FILE_NAME="$1wiki-$2-$3.sql.gz"
	else
		FILE_NAME="$1wiki-$2-$3.txt"
	fi
	URL="https://dumps.wikimedia.your.org/$1wiki/$2"
	echo "Downloading $FILE_NAME"
	time wget -P "$CUR_DIR/$OUT_DIR" "$URL/$FILE_NAME"
}

download_file $1 $2 $3
