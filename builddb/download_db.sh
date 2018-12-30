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
	echo
}

function check_sha1sum() {
	echo "[Info] Checking SHA-Checksum"
	cd "$OUT_DIR"
	sha1sum -c --ignore-missing $1wiki-$2-sha1sums.txt
	if [ $? -ne 0 ]; then 
		echo "[Warning] Checksum failed"
	fi
	cd ..
	echo "[Info] SHA-Checksum Compleat"
	echo

}

if [ "$#" -eq 2 ]; then
	download_file $1 $2 "sha1sums"
	download_file $1 $2 "pagelinks"
	download_file $1 $2 "page"
	download_file $1 $2 "redirect"
	check_sha1sum $1 $2
elif [ "$#" -eq 3 ]; then 
	download_file $1 $2 $3
	check_sha1sum $1 $2
elif [ "$#" -eq 1 ]; then 
	download_file $1 "latest" "sha1sums"
	DATE=`sed -rn "s/^.* enwiki-([0-9]+)-.*$/\1/p" "database/$1wiki-latest-sha1sums.txt" | head -n 1 -q` 
	download_file $1 $DATE "pagelinks"
	download_file $1 $DATE "page"
	download_file $1 $DATE "redirect"
	check_sha1sum $1 "latest"
else 
	echo "[Error] Invalid number of arguments"
	exit 1
fi

