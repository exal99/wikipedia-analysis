import sqlite3
import collections
import itertools

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
		if found_path and (source_visited[source_queue[0]] > source_deapth and target_visited[target_queue[0]] > target_deapth):
			intersections = filter_intersections(source_visited, target_visited, intersections)
			return construct_path(source_parent, target_parent, intersections)

		if found_path and source_visited[source_queue[0]] > source_deapth:
			target_added, t_deapth = BFS_target(target_queue, target_visited, target_parent, connection)
			intersections |= target_added & source_visited.keys()
		elif found_path and target_visited[target_queue[0]] > target_deapth:
			source_added, s_deapth = BFS_source(source_queue, source_visited, source_parent, connection)
			intersections |= source_added & target_visited.keys()
		else:
			source_added, s_deapth = BFS_source(source_queue, source_visited, source_parent, connection)
			target_added, t_deapth = BFS_target(target_queue, target_visited, target_parent, connection)

			intersections |= source_added & target_visited.keys()
			intersections |= target_added & source_visited.keys()

		if not found_path and intersections:
			found_path = True
			source_deapth = s_deapth
			target_deapth = t_deapth

	if found_path:
		return construct_path(source_parent, target_parent, intersections)
	else:
		return None

def filter_intersections(source_visited, target_visited, intersections):
	filterd = set()
	shortest = float('inf')
	for intersection in intersections:
		if source_visited[intersection] + target_visited[intersection] < shortest:
			shortest = source_visited[intersection] + target_visited[intersection]
			filterd = {intersection}
		elif source_visited[intersection] + target_visited[intersection] == shortest:
			filterd.add(intersection)
	return filterd

def construct_path(source_parent, target_parent, intersections):
	paths = set()

	for intersection in intersections:
		from_source_to_inter = construct_path_from_to(source_parent, intersection)
		from_inter_to_target = construct_path_from_to(target_parent, intersection, reverse=True)
		for path in itertools.product(from_source_to_inter, from_inter_to_target):
			paths.add(tuple(path[0] + path[1][1:]))
	return list(paths)
		
def construct_path_from_to(source_parent, start, reverse=False):
	if None in source_parent[start]:
		return [[start]]

	paths = []
	for parent in source_parent[start]:
		for path in construct_path_from_to(source_parent, parent, reverse):
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

def get_id_of_title(connection, title):
	page_id, is_redirect = connection.execute(f"SELECT page_id, page_is_redirect FROM page WHERE page_title='''{title}'''").fetchone()
	if is_redirect:
		(page_id,) = connection.execute("SELECT rd_target FROM redirect WHERE rd_from=?", (page_id,)).fetchone()
	return page_id

def get_title_of_id(connection, page_id):
	return connection.execute('SELECT page_title FROM page WHERE page_id=?',(page_id,)).fetchone()


def main():
	c=sqlite3.connect('database/enwiki.db')
	#b=BFS(c, 37817,20127)
	print(bidirectional_BFS(c, 310678,140471)) # Venus flytrap -> Charlie Brown

#main()