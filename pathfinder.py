"""
This module contains all the tools for finding the shortes path
between two articles and constructing the path between them.
"""

import database
import collections
import itertools

from typing import List, Tuple, DefaultDict, Set


def bidirectional_BFS(db : database.WikiDatabase, source : int, target : int) -> List[Tuple[int, ...]]: 
	"""
	Finds all the shortest paths between the given 'source' and 'target'.
	This function uses a bidirectional breath first search (BFS).

	Params:
	db 			The WikiDatabase object used for the search
	source 		The id of the article to start from
	target 		The id of the target article

	Return:
	All shortest path with the same length from 'source' to 'target'. Each element
	of the returned list contains one path. The path is a tuple of all the article ids.
	"""
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
				if target not in neighbours: # if an article has no links continue
					continue
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
				if source not in neighbours:
					continue
				for neighbour in neighbours[source]:
					if neighbour not in source_visited:
						source_parent[neighbour].add(source)
						source_visited[neighbour] = source_visited[source] + 1
						new_queue.append(neighbour)
					elif source_visited[neighbour] == source_visited[source] + 1:
						source_parent[neighbour].add(source)
			source_queue = tuple(new_queue)

		intersections = source_visited.keys() & target_visited.keys()
	if intersections:
		return construct_path(source_parent, target_parent, intersections)
	else:
		return None


def construct_path(source_parent: DefaultDict[int, Set[int]], target_parent: DefaultDict[int, Set[int]],
	               intersections: Set[int]) -> List[Tuple[int, ...]]:
	"""
	Constructs all paths given the parrent nodes from the forward search, the
	backward search and all the intersection points of the two searches. The
	parrent mapping is a mapping between a node and all possible ways to reach
	that node.

	Arguments:
	source_parent 		A mapping between each node and all possible ways to reach it from
						the forward search.
	target_parent 		A mapping between each node and all possible ways to reach it from
	 					the backwards search.
	intersections 		All the intersection points of the two searches.

	Return:
	All the shortes paths between the start and the end
	"""
	paths = []

	for intersection in intersections:
		from_source_to_inter = construct_path_from_to(source_parent, intersection)
		from_inter_to_target = construct_path_from_to(target_parent, intersection, reverse=True)
		for path in itertools.product(from_source_to_inter, from_inter_to_target):
			paths.append(tuple(path[0] + path[1][1:]))
	return paths
		
def construct_path_from_to(parrent: DefaultDict[int, Set[int]], start: Set[int],
	                       reverse: bool=False) -> List[List[int]]:
	"""
	Constructs all the paths from the 'start' list given the parrent mapping
	recursivly. If 'reverse' is True the result is reversed.

	Arguments:
	parrent 		The parrent mapping
	start 			A list of all start locations
	reverse 		Reverse flag

	Return:
	All paths from each node in the 'start' list to the end in the parrent,
	i.e. the node wich have 'None' as parrent.
	"""
	if None in parrent[start]:
		return [[start]]

	paths = []
	for parent in parrent[start]:
		for path in construct_path_from_to(parrent, parent, reverse):
			if reverse:
				path.insert(0, start)
			else:
				path.append(start)
			paths.append(path)

	return paths