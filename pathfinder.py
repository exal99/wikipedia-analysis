import database
import collections
import itertools


def bidirectional_BFS(db, source, target): 
	source_queue = (source,)
	target_queue = (target,)

	source_visited = {source:0}
	target_visited = {target:0}

	source_parent = collections.defaultdict(set)
	target_parent = collections.defaultdict(set)

	source_parent[source].add(None)
	target_parent[target].add(None)

	intersections = set()

	while source_queue and target_queue:
		if intersections:
			return construct_path(source_parent, target_parent, intersections)

		if db.get_incoming_count(target_queue) < db.get_outgoing_count(source_queue):
			neighbours = db.get_incoming_links(target_queue)
			new_queue = []
			for target in target_queue:
				for neighbour in neighbours[target]:
					if neighbour not in target_visited:
						target_parent[neighbour].add(target)
						target_visited[neighbour] = target_visited[target] + 1
						new_queue.append(neighbour)
					elif target_visited[neighbour] == target_visited[target] + 1:
						target_parent[neighbour].add(target)
			target_queue = tuple(new_queue)

		else:
			neighbours = db.get_outgoing_links(source_queue)
			new_queue = []
			for source in source_queue:
				for neighbour in neighbours[source]:
					if neighbour not in source_visited:
						source_parent[neighbour].add(source)
						source_visited[neighbour] = source_visited[source] + 1
						new_queue.append(neighbour)
					elif source_visited[neighbour] == source_visited[source] + 1:
						source_parent[neighbour].add(source)
			source_queue = tuple(new_queue)

		intersections = source_visited.keys() & target_visited.keys()


def construct_path(source_parent, target_parent, intersections):
	paths = []

	for intersection in intersections:
		from_source_to_inter = construct_path_from_to(source_parent, intersection)
		from_inter_to_target = construct_path_from_to(target_parent, intersection, reverse=True)
		for path in itertools.product(from_source_to_inter, from_inter_to_target):
			paths.append(tuple(path[0] + path[1][1:]))
	return paths
		
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