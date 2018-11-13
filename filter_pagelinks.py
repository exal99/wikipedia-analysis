#! /usr/bin/env python3

"""
Filters the pagelinks table, removing broken links and changeing the target to refer
to id and not title. 

------------------------------------
PAGE FILE FORMAT
  PAGE_ID,'TITLE',IS_REDIRECT[0|1]\\n

------------------------------------
REDIRECT FILE FORMAT
  FROM_ID,TARGET_ID\\n

------------------------------------
PAGELINK FILE FORMAT BEFORE
  FROM_ID,'TARGET_TITLE'\\n

PAGELINK FILE FORMAT AFTER
  FROM_ID,TARGET_ID\\n

"""	

import argparse_helper
import gzip
from collections import namedtuple

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("page", metavar="<page table>",
						help="the ziped page sql file")
	parser.add_argument("redirect", metavar="<redirect table>",
						help="the ziped redirects sql file")
	parser.add_argument("pagelinks", metavar="<pagelinks table>",
						help="the ziped pagelinks sql file")

	args = parser.parse_args()
	args = (args.page, args.redirect, args.pagelinks)
	for arg in args:
		valid_zip_checker(parser, arg)
	return args

def parse_page_file(page):
	title_to_id = {}
	page_ids = set()
	print("[Info] Reading page file")
	with gzip.open(page) as p:
		for line in p:
			line = line.decode()
			page_id     = int(line.split(",")[0])
			page_title  = line[line.index(',') + 1:-3]
	
			if page_id % 50077 == 0:
				print(f"\r[Info] Current id: {page_id: <10}", end = "")

			if page_title not in title_to_id:
				title_to_id[page_title] = page_id
				page_ids.add(page_id)
			else:
				raise RuntimeError(f"[ERROR] Name Colition: {page_title} {title_to_id[page_title]} {page_id}")
	print(f"\r[Info] Current id: {page_id: <10}", end = "")
	print("    [Done]")
	return title_to_id, page_ids

def parse_redirect_file(redirect):
	print("[Info] Reading redirect file")
	from_id_to_id = {}
	loading = "\\|/-"
	load_ind = 0
	with gzip.open(redirect) as r:
		for ind, line in enumerate(r):
			line = line.decode()
			[from_id, to_id] = line.split(",")
			if from_id not in from_id_to_id:
					from_id_to_id[int(from_id)] = int(to_id[:-1])
			else:
				raise RuntimeError(f"[ERROR] Id Colition: {from_id} {from_id_to_id[from_id]} {to_id}")

			if ind % 100000 == 0:
				print(f"\r[Info] Working ...  {loading[load_ind]}", end="")
				load_ind += 1
				load_ind %= 4
	print("    [Done]")
	return from_id_to_id


def filter_pagelinks(page, redirect, pagelinks):
	title_to_id, page_ids  = parse_page_file(page)
	redirect_from_id_to_id = parse_redirect_file(redirect)

	written = 0
	discarded = 0

	print("[Info] Writing to output")

	with gzip.open(pagelinks) as pl_in, gzip.open(pagelinks + ".tmp", "wb") as pl_out:
		for line in pl_in:
			line = line.decode()
			pl_from      = int(line.split(",")[0])
			target_title = line[line.index(',') + 1:-1]

			if pl_from in page_ids and target_title in title_to_id:
				target_id = title_to_id[target_title]

				if target_id in redirect_from_id_to_id:
					target_id = redirect_from_id_to_id[target_id]

				pl_out.write(str(pl_from).encode() + b',' + str(target_id).encode() + b'\n')
				written += 1

			else:
				discarded += 1

			if written % 50077 == 0 or discarded % 50077 == 0:
				print(f"\r[Info] Lines written (written/discarded): {written: >10}/{discarded: <10} " + \
					  f" {round(100 * written/(written + discarded), 1)} %    ", end="")

	print(f"\r[Info] Lines written (written/discarded): {written: >10}/{discarded: <10} " + \
              f" {round(100 * written/(written + discarded), 1)} %", end="")
	print("    [Done]")
