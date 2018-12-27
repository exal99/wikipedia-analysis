#! /usr/bin/env python3

"""
Filters the redirect table, removing broken redirects and changing the target to refer
to id and not title.

------------------------------------
PAGE FILE FORMAT
  PAGE_ID,'TITLE',IS_REDIRECT[0|1]\\n

------------------------------------
REDIRECT FILE FORMAT BEFORE
  FROM_ID,'TARGET_TITLE'\\n

REDIRECT FILE FORMAT AFTER
  FROM_ID,TARGET_ID\\n

"""

import argparse
import gzip
from argparse_helper import *


def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("page", metavar="<page table>",
						help="the ziped page sql file")
	parser.add_argument("redirect", metavar="<redirect table>",
						help="the ziped redirects sql file")
	
	args = parser.parse_args()
	args = (args.page, args.redirect)
	for arg in args:
		valid_zip_checker(parser, arg)
	return args

def main():
	page, redirects = get_arguments()
	filter_redirects(page, redirects)


def parse_page_file(page):
	title_to_id = {}
	page_ids = set()
	print("[Info] Reading page file")
	with gzip.open(page) as p:
		for line in p:
			line = line.decode()
			[page_id, page_title, _] = line.split('\t')
			page_id = int(page_id)
			# page_id = int(line.split(',')[0])
			# page_title = line[line.index(',') + 1:-3]
			if page_id % 61 == 0:
				print(f"\r[Info] Current id: {page_id: <10}", end = "")
			if page_title not in title_to_id:
				title_to_id[page_title] = page_id
				page_ids.add(page_id)
			else:
				raise RuntimeError(f"[ERROR] Name Colition: {page_title} {title_to_id[page_title]} {page_id}")
	print("     [Done]")
	return title_to_id, page_ids

def parse_redirect_file(title_to_id, page_ids, redirect):
	print("[Info] Reading redirect file")
	removed = 0
	added = 0
	redirect_from_id_to_id = {}
	with gzip.open(redirect) as r:
		for line in r:
			line = line.decode()
			[from_id, to_title] = line[:-1].split("\t") # ignores the last character since it's a newline (\n)
			from_id = int(from_id)
			# from_id  = int(line.split(',')[0])
			# to_title = line[line.index(',') + 1:-1]
			if from_id in page_ids and to_title in title_to_id:
				redirect_from_id_to_id[from_id] = title_to_id[to_title]
				added += 1
			else:
				removed += 1
			if added % 61 == 0 or removed % 61 == 0:
				print(f"\r[Info] Filterd (added/removed): {added: >10}/{removed: <10}", end="")
	print(f"\r[Info] Filterd (added/removed): {added: >10}/{removed: <10}        [Done]")
	return redirect_from_id_to_id

def filter_redirects(page, redirect):
	title_to_id, page_ids  = parse_page_file(page)
	redirect_from_id_to_id = parse_redirect_file(title_to_id, page_ids, redirect)

	del title_to_id
	del page_ids

	print(f"[Info] Writing to output")
	written = 0
	discarded = 0
	with gzip.open(redirect + ".tmp", 'wb') as redir_out: 
		for from_id in redirect_from_id_to_id:
			target_id = redirect_from_id_to_id[from_id]

			deapth = 0
			while target_id in redirect_from_id_to_id:
				target_id = redirect_from_id_to_id[target_id]
				deapth += 1
				if deapth == 100:
					target_id = None
					discarded += 1

			if target_id is not None:
				redir_out.write(str(from_id).encode() + b'\t' + str(target_id).encode() + b'\n')
				written += 1
			if written % 61 == 0 or discarded % 61 == 0:
				print(f"\r[Info] Lines written (written/discarded): {written: >10}/{discarded: <10}", end="")
	print("    [Done]")



if __name__ == '__main__':
	main()