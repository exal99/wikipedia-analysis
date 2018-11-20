import sqlite3
import collections
import itertools

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

def bidirectional_BFS(connection, from_article, to_article):
	source_queue = collections.deque((from_article,))
	target_queue = collections.deque((to_article,))

	source_visited = {from_article: 0}
	target_visited = {to_article: 0}

	source_parent = collections.defaultdict(set)
	target_parent = collections.defaultdict(set)

	source_parent[from_article].add(None)
	target_parent[to_article].add(None)

	found_path    = False
	source_deapth = 0
	target_deapth = 0

	intersections = set()

	while source_queue and target_queue:
		if found_path and (source_queue[0] > source_deapth or target_queue[0] > target_deapth):
			return construct_path(source_parent, target_parent, from_article, to_article, intersections)

		source_added, s_deapth = BFS_source(source_queue, source_visited, source_parent, connection)
		target_added, t_deapth = BFS_target(target_queue, target_visited, target_parent, connection)

		intersections |= source_added & target_visited.keys()
		intersections |= target_added & source_visited.keys()

		if not found_path and intersections:
			found_path = True
			source_deapth = s_deapth
			target_deapth = t_deapth

	if found_path:
		return construct_path(source_parent, target_parent, from_article, to_article, intersections)
	else:
		return None

def construct_path(source_parent, target_parent, source, target, intersections):
	paths = []

	for intersection in intersections:
		from_source_to_inter = construct_path_from_to(source_parent, source, intersection)
		from_inter_to_target = construct_path_from_to(target_parent, target, intersection, reverse=True)
		print(from_source_to_inter, from_inter_to_target)
		for path in itertools.product(from_source_to_inter, from_inter_to_target):
			paths.append(path[0] + path[1][1:])
	return paths
		
def construct_path_from_to(source_parent, target, start, reverse=False):
	if start == target:
		return [[target]]

	paths = []
	for parent in source_parent[start]:
		for path in construct_path_from_to(source_parent, target, parent):
			if reverse:
				path.insert(0, start)
			else:
				path.append(start)
			paths.append(path)

	return paths

def BFS_source(queue, visited, parent, connection):
	current = queue.popleft()

	added_articles = set()

	for (linked_article,) in connection.execute('SELECT pl_target FROM pagelinks WHERE pl_from = ?;', (current,)):
		if linked_article not in visited:
			parent[linked_article].add(current)
			visited[linked_article] = visited[current] + 1
			queue.append(linked_article)
			added_articles.add(linked_article)
		elif visited[current] + 1 == visited[linked_article]:
			parent[linked_article].add(current)

	return added_articles, visited[current]

def BFS_target(queue, visited, parent, connection):
	current = queue.popleft()

	added_articles = set()

	for (linked_article,) in connection.execute('SELECT pl_from FROM pagelinks WHERE pl_target = ?;', (current,)):
		if linked_article not in visited:
			parent[linked_article].add(current)
			visited[linked_article] = visited[current] + 1
			queue.append(linked_article)
			added_articles.add(linked_article)
		elif visited[current] + 1 == visited[linked_article]:
			parent[linked_article].add(current)

	return added_articles, visited[current]

def main():
	c=sqlite3.connect('database/enwiki.db')
	b=BFS(c, 37817,20127)

#main()