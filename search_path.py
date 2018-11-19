import sqlite3
import queue
import collections

def BFS(connection, from_article, to_article):
	to_visit = queue.Queue()
	visited  = set()

	to_visit.put(from_article)
	visited.add(from_article)

	path = collections.defaultdict(list)
	path[from_article].append((None,0))

	max_distance = -1

	current_article = None

	while not to_visit.empty() and (max_distance == -1 or path[current_article][0][1] <= max_distance):

		current_article = to_visit.get()

		if current_article == to_article:
			max_distance = path[to_article][0][1]

		for (linked_article,) in connection.execute('SELECT pl_target FROM pagelinks WHERE pl_from=?;', (current_article,)):
			#print(linked_article)
			if linked_article not in visited:
				to_visit.put(linked_article)
				visited.add(linked_article)
				path[linked_article].append((current_article, path[current_article][0][1] + 1))
				#print(linked_article)
	return path