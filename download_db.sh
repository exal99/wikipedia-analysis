#!/usr/bin/env bash

# Usage: download_db.sh LANG DATE FILE


CUR_DIR=`pwd`
OUT_DIR="database"

function download_file() {
	echo "[Info] Downloading $3"
	
	FILE_NAME=""
	if [ "$3" != "sha1sums" ]; then
		FILE_NAME="$1wiki-$2-$3.sql.gz"
	else
		FILE_NAME="$1wiki-$2-$3.txt"
	fi
	URL="https://dumps.wikimedia.your.org/$1wiki/$2"
	echo "Downloading $FILE_NAME"
	wget -q --show-progress -P "$CUR_DIR/$OUT_DIR" "$URL/$FILE_NAME"
	if [ "$3" != "sha1sums" ]; then
		echo "[Info] Checking SHA-Checksum on $FILE_NAME"
		cd "$OUT_DIR"
		grep $FILE_NAME "$1wiki-$2-sha1sums.txt" | sha1sum -c -
		cd ..
		if [ $? -ne 0 ]; then 
			echo "[Warning] Checksum failed for '$3'"
		fi
	fi 
}

if [ "$#" -eq 2 ]; then
	download_file $1 $2 "sha1sums"
	download_file $1 $2 "pagelinks"
	download_file $1 $2 "page"
	download_file $1 $2 "redirect"
elif [ "$#" -eq 3 ]; then 
	download_file $1 $2 $3
elif [ "$#" -eq 1 ]; then 
	echo "[Warrning] To be implemented"
else 
	echo "[Error] Invalid number of arguments"
	exit 1
fi

