#! /usr/bin/env python3

import graph_tool as gt
import graph_tool.draw as draw
import graph_tool.stats as stats

import numpy as np


from terminal import Terminal, Options
from database import WikiDatabase
from wikipedia_analyzer import  get_available_databases
from pathfinder import bidirectional_BFS


class PathfinderTerminal(Terminal):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.db = None
		self.last_res = None
		try:
			PathfinderTerminal.command_selectdb.__doc__ = PathfinderTerminal.command_selectdb.__doc__.format({database for database in get_available_databases()})
		except KeyError:
			pass

	def command_selectdb(self, db:Options(get_available_databases())):
		"""
		Selects a database to search in.

		Usage:
		selectdb <database>

		<database> can be one of the following:
		{}
		"""
		self.db = WikiDatabase(db + 'wikidb')
		self.prompt = db + " > "
		self.last_res = None
		return f"Current database updated to '{db}'"

	def format_path(self, path):
		return ' -> '.join([title.replace('_', ' ') for title in self.db.get_titles_of_ids(path)])

	def command_path(self, source:str, target:str):
		"""
		Searches for a path between a pair of atricles.
		Given a start ('source') and an end ('target') article all paths between the two
		will be found (assuming that there are paths between them). Both 'source' and 'target'
		needs to be sanetized, i.e. the spaces needs to be replaced by underscores ('_'). To
		retrive more paths than the one given use the 'list' command.

		Usage:
		path <source> <target>

		Use underscore ('_') instead of spaces in <source> and <target>.
		"""
		if self.db is None:
			return "No database selected. Select a database with 'selectdb'"
		source_id = self.db.get_id_of_title(source)
		target_id = self.db.get_id_of_title(target)
		if source_id is None:
			return f"No article named: '{source}'"
		if target_id is None:
			return f"No article named: '{target}'"
		self.last_res = bidirectional_BFS(self.db, source_id, target_id)

		if self.last_res is not None:
			ret_str  = f"\nSearch compleated!\nLength: {len(self.last_res[0]) - 1}\n"
			ret_str += f"Number of Paths: {len(self.last_res)}\nSample Path: {{ {self.format_path(self.last_res[0])} }}\n"
		else:
			ret_str = "\nSearch compleated!\nLength: 0\nNumber of Paths: 0\nSample Path: - "
			self.last_res = []
		return ret_str


	def command_list(self):
		"""
		Lists the resulting paths found by the last search.

		Usage:
		list                      - lists all paths
		list <number of paths>    - lists the given number of paths
		list <from> <to>          - lists all paths between the <from>:th
		                            path to the <to>:th path.
		"""
		res_str = ""
		if self.last_res is None:
			return "No saved paths. Do a search before you try to list them."
		if len(self.last_res) == 0:
			return "No available paths."
		for path in self.last_res:
			res_str += self.format_path(path)
		return res_str

	def command_list(self, npaths:int):
		ret_str = ""
		if self.last_res is None:
			return "No saved paths. Do a search before you try to list them."
		if len(self.last_res) == 0:
			return "No available paths."
		for path in self.last_res[:npaths]:
			ret_str += self.format_path(path) + "\n"
		return ret_str

	def command_list(self, from_line:int, to_line:int):
		ret_str = ""
		if self.last_res is None:
			return "No saved paths. Do a search before you try to list them."
		if len(self.last_res) == 0:
			return "No available paths."
		for path in self.last_res[from_line - 1:to_line]:
			ret_str += self.format_path(path) + "\n"
		return ret_str

	def command_npaths(self):
		"""
		Prints the number of paths found by the last search.

		Usage:
		npaths
		"""
		if self.last_res is None:
			return "No saved paths. Do a search before you try to list them."

		return f"Number of Paths: {len(self.last_res)}"

	def command_draw(self):
		if self.last_res is None:
			return "No saved paths. Do a search before you try to draw them."

		edge_list = [[t.replace('_', ' ') for t in self.db.get_titles_of_ids((val, path[ind+1]))] for path in self.last_res for ind, val in enumerate(path[:-1])]

		graph = gt.Graph()
		strings = graph.add_edge_list(edge_list, string_vals=True, hashed=True)

		stats.remove_parallel_edges(graph)

		fill_color = graph.new_vertex_property('vector<float>', val=[0, 0, 0.640625, 0.9])
		fill_color[graph.vertex(0)] = [0, 0.640625, 0, 0.9]
		fill_color[graph.vertex(len(self.last_res[0]) - 1)] = [0.640625, 0, 0, 0.9]


		draw.interactive_window(graph, vertex_fill_color=fill_color, vertex_text=strings,
								vertex_text_position=graph.new_vertex_property('float', val=0),
			                    vertex_anchor=graph.new_vertex_property('int', val=0),
			                    geometry=(1200,1600),vertex_font_size=graph.new_vertex_property('float', val=20))

		




def main():
	terminal = PathfinderTerminal()
	terminal.run()

if __name__ == '__main__':
	main()
