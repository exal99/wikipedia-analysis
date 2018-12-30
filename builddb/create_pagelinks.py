#! /usr/bin/env python3

import argparse
import gzip
from DefaultOrderedDict import DefaultOrderedDict
from argparse_helper import *

class GroupLinks:

	def __init__(self):
		self.mapping = DefaultOrderedDict(lambda : [None, None])

	def add_incoming(self, to, incoming_list):
		self.mapping[to][0] = incoming_list

		while self.first_page_id() < to and self.first_value()[0] is None:
			_, outgoing_list = self.first_value()
			print(format_values(self.first_page_id(), [], outgoing_list))
			del self.mapping[self.first_page_id()]

		self._cleanup(to)

	def add_outgoing(self, from_page, outgoing_list):
		self.mapping[from_page][1] = outgoing_list

		while self.first_page_id() < from_page and self.first_value()[1] is None:
			incoming_list, _ = self.first_value()
			print(format_values(self.first_page_id(), incoming_list, []))
			del self.mapping[self.first_page_id()]

		self._cleanup(from_page)
	
	def _cleanup(self, page_id):
		if None not in self.mapping[page_id]:
			print(format_values(page_id, *self.mapping[page_id]))
			del self.mapping[page_id]

	def dump_rest(self):
		for (page_id, [incoming_list, outgoing_list]) in self.mapping.items():
			incoming_list = incoming_list if incoming_list is not None else []
			outgoing_list = outgoing_list if outgoing_list is not None else []
			print(format_values(page_id, incoming_list, outgoing_list))

	def first_page_id(self):
		return next(iter(self.mapping))

	def first_value(self):
		return self.mapping[self.first_page_id()]




def format_values(page_id, incoming_list, outgoing_list):
	return f"{page_id}\t{len(incoming_list)}\t{len(outgoing_list)}\t'{{{repr(incoming_list)[1:-1]}}}'\t'{{{repr(outgoing_list)[1:-1]}}}'"

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("sorted_from", metavar="<outgoing links>",
						help="the ziped outgoing links file")
	parser.add_argument("sorted_to", metavar="<incoming links>",
						help="the ziped incoming links file")
	
	args = parser.parse_args()
	args = (args.sorted_from, args.sorted_to)
	for arg in args:
		valid_zip_checker(parser, arg)
	return args

def links_iterator(links):
	for line in map(bytes.decode, links):
		line = line[:-1]
		yield tuple(map(int, line.split('\t')))

def get_links_group(l_iterator, group_by, last_link):
	if last_link:
		current = last_link[group_by]
		result_list = [last_link[(group_by + 1) % 2]]
	else:
		current = -1
		result_list = []

	next_link = ()
	for link in l_iterator:
		if current == -1:
			current = link[group_by]
		if link[group_by] != current:
			next_link = (link[0], link[1])
			break
		result_list.append(link[(group_by + 1) % 2])
	return current, result_list, next_link

def merge_links(sorted_from, sorted_to):
	with gzip.open(sorted_from) as outgoing, gzip.open(sorted_to) as incoming:
		
		links = GroupLinks()

		outgoing_iterator = links_iterator(outgoing)
		incoming_iterator = links_iterator(incoming)

		current_outgoing = 0
		current_incoming = 0
		
		outgoing_list = []
		incoming_list = []

		next_outgoing = tuple(next(outgoing_iterator))
		next_incoming = tuple(next(incoming_iterator))


		while next_outgoing and next_incoming:

			if next_outgoing[0] < next_incoming[1]:
				current_outgoing, outgoing_list, next_outgoing = get_links_group(outgoing_iterator, 0, next_outgoing)
				links.add_outgoing(current_outgoing, outgoing_list)

			else:
				current_incoming, incoming_list, next_incoming = get_links_group(incoming_iterator, 1, next_incoming)
				links.add_incoming(current_incoming, incoming_list)


		while next_outgoing:
			current_outgoing, outgoing_list, next_outgoing = get_links_group(outgoing_iterator, 0, next_outgoing)
			links.add_outgoing(current_outgoing, outgoing_list)

		while next_incoming:
			current_incoming, incoming_list, next_incoming = get_links_group(incoming_iterator, 1, next_incoming)
			links.add_incoming(current_incoming, incoming_list)

		links.dump_rest()

		

def main():
	sorted_from, sorted_to = get_arguments()
	merge_links(sorted_from, sorted_to)


if __name__ == '__main__':
	main()
