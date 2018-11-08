#! /usr/bin/env python3

import argparse
import gzip
from argparse_helper import *

# REDIRECTS
# FROM_ID,TO_TITLE

# PAGE
# ID,TITLE,IS_REDIRECT

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
	print(page, redirects)


def filter_redirects(page, redirects):
	page_dict = {}
	last_len=0
	with gzip.open(page) as p:
		for line in p:
			line = line.decode()
			page_id = int(line.split(',')[0])
			page_title = line[line.index(',') + 1:-2]
			#input(page_id + " " + page_title + " " + str(page_dict))
			print(" " * last_len, end="\r")
			print(f"{page_id}: {page_title}"[0:40], end="\r")
			last_len = len(f"{page_id}: {page_title}"[0:40])
			if page_title not in page_dict:
				page_dict[page_title] = page_id
			else:
				raise RuntimeError(f"ERROR: {page_title} {page_dict[page_title]} {page_id}")
	

if __name__ == '__main__':
	main()
