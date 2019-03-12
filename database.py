import psycopg2
import random

class WikiDatabase():
	def __init__(self, database, **kwargs):
		self.conn = psycopg2.connect(dbname=database, **kwargs)
		self.cur = self.conn.cursor()
		self.cur.execute('SELECT MIN(page_id) FROM page;')
		self.min_id = self.cur.fetchone()[0]
		self.cur.execute('SELECT MAX(page_id) FROM page;')
		self.max_id = self.cur.fetchone()[0]
		self.last_starts_with = ()

	def get_outgoing_count(self, outgoing):
		outgoing_str = format_tuple(outgoing)
		self.cur.execute("SELECT SUM(outgoing_count) FROM links WHERE id IN %s;" % outgoing_str)
		res = self.cur.fetchone()[0]
		return res if res is not None else 0

	def get_incoming_count(self, incoming):
		incoming_str = format_tuple(incoming)
		self.cur.execute("SELECT SUM(incoming_count) FROM links WHERE id IN %s;" % incoming_str)
		res = self.cur.fetchone()[0]
		return res if res is not None else 0

	def get_incoming_links(self, incoming):
		incoming_str = format_tuple(incoming)
		self.cur.execute("SELECT id, incoming_links FROM links WHERE id IN %s;" % incoming_str)
		return dict(self.cur.fetchall())

	def get_outgoing_links(self, outgoing):
		outgoing_str = format_tuple(outgoing)
		self.cur.execute("SELECT id, outgoing_links FROM links WHERE id IN %s;" % outgoing_str)
		return dict(self.cur.fetchall())

	def get_id_of_title(self, title):
		self.cur.execute("SELECT page_id FROM page WHERE page_title='%s';" % title)
		res = self.cur.fetchone()
		return res[0] if res else None

	def get_titles_of_ids(self, ids):
		ids_str = format_tuple(ids)
		when_clause = "WHEN {} THEN {} " * len(ids) + "END"
		when_clause = when_clause.format(*[f(x) for x in enumerate(ids) for f in (lambda x:x[1], lambda x:x[0])]) # see: https://stackoverflow.com/a/11869360/4820676
		self.cur.execute("SELECT page_title FROM page WHERE page_id IN %s ORDER BY CASE page_id %s;" % (ids_str, when_clause))
		return [result[0] for result in self.cur]

	def get_random_page(self):
		page_id = 0
		while page_id == 0:
			page_id = random.randint(self.min_id, self.max_id)
			if self.get_titles_of_ids((page_id,)):
				self.cur.execute('SELECT page_is_redirect FROM page WHERE page_id=%d;' %(page_id))
				if not self.cur.fetchone()[0]:
					return page_id
			page_id = 0

	def dump_statistics(self, sources, targets, all_paths):
		values = ""
		for source, target, paths in zip(sources, targets, all_paths):
			if paths is not None:
				values += f"({source}, {target}, {len(paths[0]) - 1}, {len(paths)}, '{{{str(paths[0])[1:-1]}}}'),"
			else:
				values += f"({source}, {target}, 0, 0, '{{}}'),"
		if values:
			self.cur.execute("INSERT INTO paths VALUES %s;" %values[:-1]) #removes the last comma
			self.conn.commit()

	def get_all_starts_with(self, text):
		number_to_fetch = 50
		if self.last_starts_with:
			if text == self.last_starts_with[0]:
				return self.last_starts_with[1] #[:10] + (['...'] if len(self.last_starts_with[1]) > 10 else [])
			if text.startswith(self.last_starts_with[0]) and len(self.last_starts_with[1]) <= 50:
				return [result for result in self.last_starts_with[1] if result.startswith(text)] #[:10] + (['...'] if len(self.last_starts_with[1]) > 10 else [])
		text += '%'
		self.cur.execute("SELECT page_title FROM page WHERE page_title LIKE %s LIMIT {};".format(number_to_fetch + 1), (text,))
		res = [result[0] for result in self.cur.fetchall()]
		self.cur.execute("SELECT page_title FROM page WHERE page_title=%s;", (text[:-1],))
		res += [result[0] for result in self.cur.fetchall()]
		self.last_starts_with = (text[:-1], res)
		return res #[:10] + (['...'] if len(res) > 10 else [])



def format_tuple(tup):
	return str(tup).replace(',)', ')')