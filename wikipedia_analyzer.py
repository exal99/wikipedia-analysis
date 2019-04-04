#! /usr/bin/env python3

"""
This module is the main analyzer of the database. It does not provide
a nice user interface instead it only does what it is ment to do: gather 
data! Multiple instances of this program may be launched simultaneously
to increase speed.
"""

import psycopg2
import pathfinder
import database
import sys
import select
import time
import argparse

from typing import List, Tuple

BUFFER_SIZE = 100


def get_available_databases() -> List[str]:
	"""
	Returns all available databases currently downloaded on the computer.

	Return:
	Returns the list of all language codes of the available databases to search in. 
	"""
	cur = psycopg2.connect(dbname='postgres').cursor()
	cur.execute("SELECT datname FROM pg_database WHERE datistemplate=FALSE;")
	return [row[0][:-6] for row in cur if row[0].endswith('wikidb')]

def get_arguments():
	"""
	Gets the command line argument that specifies the database to seach in.
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument('language', choices=get_available_databases(), help='The language code of the wikipedia')
	return parser.parse_args().language

def analyze_path(dbase: database.WikiDatabase) -> Tuple[List[int], List[int], List[List[Tuple[int, ...]]]]:
	"""
	Picks two articles at random and computes the shortest path between them in both directions.

	Arguments:
	dbase 		The database to search in.

	Return:
	Returns the result of the two searches. The first list is the start, the second
	the ends and the last one is the paths.
	"""
	article1 = dbase.get_random_page()
	article2 = dbase.get_random_page()
	paths = pathfinder.bidirectional_BFS(dbase, article1, article2)
	paths_reversed = pathfinder.bidirectional_BFS(dbase, article2, article1)
	return [article1, article2], [article2, article1], [paths, paths_reversed]


def wiki_analyzer(language: str) -> None:
	"""
	Analyzes a single language and prints the speed at which it's currently
	running at. Dumps the result into the database when the buffer fills up
	or when the user exits the program (or if it crashes).

	Arguments:
	language 		The language code for the database.
	"""
	running = True
	dbase = database.WikiDatabase(f'{language}wikidb')

	source_buffer = []
	target_buffer = []
	paths_buffer  = []

	last_time = time.time()
	paths_added = 0

	try:
		while running:
		
			sources, targets, all_paths = analyze_path(dbase)
			source_buffer.extend(sources)
			target_buffer.extend(targets)
			paths_buffer.extend(all_paths)
			paths_added += 2

			if len(source_buffer) >= BUFFER_SIZE:
				dbase.dump_statistics(source_buffer, target_buffer, paths_buffer)
				source_buffer = []
				target_buffer = []
				paths_buffer  = []

			if select.select([sys.stdin], [], [], 0.0)[0]:
				usr_input = input()
				if usr_input.lower() == 'q' or usr_input.lower() == 'quit':
					running = False
					if source_buffer:
						dbase.dump_statistics(source_buffer, target_buffer, paths_buffer)

			if time.time() - last_time > 15:
				d_t = time.time() - last_time
				paths_per_min = round(paths_added/d_t * 60)
				print(f"\r{paths_per_min} paths / min ", end='')
				paths_added = 0
				last_time = time.time()
	finally:
		if running: 
			dbase.dump_statistics(source_buffer, target_buffer, paths_buffer)



def main():
	"""
	The main function. Starts the analyzer.
	"""
	lang = get_arguments()
	wiki_analyzer(lang)

if __name__ == '__main__':
	main()
