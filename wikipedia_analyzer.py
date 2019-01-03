#! /usr/bin/env python3

import psycopg2
import pathfinder
import database
import sys
import select
import time

BUFFER_SIZE = 100


def analyze_path(dbase):
	article1 = dbase.get_random_page()
	article2 = dbase.get_random_page()
	paths = pathfinder.bidirectional_BFS(dbase, article1, article2)
	paths_reversed = pathfinder.bidirectional_BFS(dbase, article2, article1)
	return [article1, article2], [article2, article1], [paths, paths_reversed]


def wiki_analyzer():
	running = True
	dbase = database.WikiDatabase('enwikidb')

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
	wiki_analyzer()

if __name__ == '__main__':
	main()
