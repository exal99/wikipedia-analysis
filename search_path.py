import sqlite3
import collections

def BFS(connection, from_article, to_article):
	to_visit = collections.deque()
	visited  = {}

	to_visit.append(from_article)
	visited[from_article] = 0

	path = collections.defaultdict(set)
	path[from_article].add(None)

	max_distance = 0
	total_visited = 0
	current_article = None

	while to_visit:

		current_article = to_visit.popleft()
		total_visited += 1
		#print(f"\r{visited[current_article]} {total_visited}", end='')
		if current_article == to_article:
			return path

		for (linked_article,) in connection.execute('SELECT pl_target FROM pagelinks WHERE pl_from=?;', (current_article,)):
			if linked_article not in visited:
				to_visit.append(linked_article)
				visited[linked_article] = visited[current_article] + 1
				path[linked_article].add(current_article)

			elif visited[current_article] + 1 == visited[linked_article]:
				path[linked_article].add(current_article)

			if visited[linked_article] > max_distance:
				max_distance = visited[linked_article]

		
	return path

def main():
	c=sqlite3.connect('database/enwiki.db')
	b=BFS(c, 37817,20127)

main()