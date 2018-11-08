#! /usr/bin/env python3

"""
Filters the redirect table, removing broken redirects and changing the target to refer
to id and not title.
"""

import argparse
import gzip
from argparse_helper import *

# REDIRECTS
# FROM_ID,'TO_TITLE'

# PAGE
# ID,'TITLE',IS_REDIRECT [0|1]

#------------------------




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


def filter_redirects(page, redirects):
	page_dict = {}
	last_len=0
	print("[Info] Reading page file")
	with gzip.open(page) as p:
		for line in p:
			line = line.decode()
			page_id = int(line.split(',')[0])
			page_title = line[line.index(',') + 1:-3]
			if page_id % 13 == 0:
				print(f"\r[Info] Current id: {page_id: <10}", end = "")
			last_len = len(f"{page_id}: {page_title}"[0:40])
			if page_title not in page_dict:
				page_dict[page_title] = page_id
			else:
				raise RuntimeError(f"[ERROR] Name Colition: {page_title} {page_dict[page_title]} {page_id}")
	print("     [Done]")
	print("[Info] Reading redirects file")
	removed = 0
	added = 0
	with gzip.open(redirects) as r_in, gzip.open(redirects + ".tmp", "wb") as r_out:
		for line in r_in:
			line = line.decode()
			from_id  = int(line.split(',')[0])
			to_title = line[line.index(',') + 1:-1]
			if to_title in page_dict:
				r_out.write(str(from_id).encode() + b',' + str(page_dict[to_title]).encode() + b'\n')
				added += 1
			else:
				removed += 1
				print(f"\r[Info] Filterd (added/removed): {added: >10}/{removed: <10}", end="")
			if not added % 13:
				print(f"\r[Info] Filterd (added/removed): {added: >10}/{removed: <10}", end="")
	print("     [Done]")


if __name__ == '__main__':
	main()