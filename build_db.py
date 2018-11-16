import sqlite3
import gzip
import time
from functools import wraps

def measure_speed(iterator):
	"""
	Speed measurement decorator
	"""
	@wraps(iterator)
	def wrapper(*args, **kwargs):
		num_items = 0
		last_time = time.time()
		for item in iterator(*args, **kwargs):
			if time.time() - last_time > 1:
				print(f'\r[Info] Inserts per second: {round(num_items/(time.time() - last_time)): <7}', end='')
				last_time = time.time()
				num_items = 0
			yield item
			num_items += 1
		print("   [Done]")
	return wrapper

def create_database(language_code):
	connection = sqlite3.connect(f'database/{language_code}wiki.db')
	cursor = connection.cursor()
	for table in ('page', 'pagelinks', 'redirect'):
		with open(f'sql/{table}_definition.sql') as table_definition:
			statements = '\n'.join(table_definition.readlines()).split(';')
			for statement in statements:
				cursor.execute(statement.strip())
	connection.commit()
	return connection

@measure_speed
def redirect_iterator(redirect_file):
	for rd_from, rd_target in map(lambda x: x[:-1].split(','), map(bytes.decode, redirect_file)):
		yield (rd_from, rd_target)

def insert_into_redirect(connection, language_code, date):
	#cursor = connection.cursor()
	print('[Info] Building \'redirect\' table')
	with gzip.open(f'database/{language_code}wiki-{date}-redirect.sql.gz') as redirect:
		connection.executemany('INSERT INTO redirect VALUES (?,?);', redirect_iterator(redirect))
		#for rd_from, rd_target in map(lambda x: x[:-1].split(','), map(bytes.decode, redirect)):
		#	try:
		#		cursor.execute('INSERT INTO redirect VALUES (?,?);', (rd_from, rd_target))
		#	except sqlite3.IntegrityError:
		#		cursor.execute('UPDATE redirect SET rd_target = ? WHERE rd_from = ?;', (rd_target, rd_from))
		#	if int(rd_from) % 1009 == 0:
		#		print(f'\r[Info] Current id: {rd_from}', end='')
	connection.commit()

@measure_speed
def pagelinks_iterator(pagelinks_file):
	for pl_from, pl_target in map(lambda x: x[:-1].split(','), map(bytes.decode, pagelinks_file)):
		yield (pl_from, pl_target)

def insert_into_pagelinks(connection, language_code, date):
	#cursor = connection.cursor()
	print('[Info] Building \'pagelinks\' table')
	with gzip.open(f'database/{language_code}wiki-{date}-pagelinks.sql.gz') as pagelinks:
		connection.executemany('INSERT INTO pagelinks VALUES (?,?);', pagelinks_iterator(pagelinks))

		#for ind, [pl_from, pl_target] in enumerate(map(lambda x: x[:-1].split(','), map(bytes.decode, pagelinks))):
		#	try:
		#		cursor.execute('INSERT INTO pagelinks VALUES (?,?);', (pl_from, pl_target))
		#	except sqlite3.IntegrityError:
		#		cursor.execute('UPDATE pagelinks SET pl_target = ? WHERE pl_from = ?;', (pl_target, pl_from))
		#	if ind % 50077 == 0:
		#		print(f'\r[Info] Current target: {pl_target}', end='')
	print("[Info] Creating index", end='')
	connection.commit()
	connection.execute("CREATE INDEX pl_from_index on pagelinks (pl_from);")
	connection.execute("CREATE INDEX pl_target_index on pagelinks (pl_target);")
	print("    Done")

def _split_page_line(line):
	page_id          = line.split(',')[0]
	page_title       = line[line.index(',') + 1:-3]
	page_is_redirect = line[-2:-1]
	return page_id, page_title, page_is_redirect


@measure_speed
def page_iterator(page_file):
	for page_id, page_title, page_is_redirect in map(_split_page_line, map(bytes.decode, page_file)):
		yield (page_id, page_title, page_is_redirect)

def insert_into_page(connection, language_code, date):
	cursor = connection.cursor()
	print('[Info] Building \'page\' table')
	with gzip.open(f'database/{language_code}wiki-{date}-page.sql.gz') as page:
		connection.executemany('INSERT INTO page VALUES (?,?,?);', page_iterator(page))
		#for page_id, page_title, page_is_redirect in map(_split_page_line, map(bytes.decode, page)):
		#	try:
		#		cursor.execute('INSERT INTO page VALUES (?,?,?);', (page_id, page_title, page_is_redirect))
		#	except sqlite3.IntegrityError:
		#		cursor.execute('UPDATE page SET page_title = ?, page_is_redirect = ? WHERE page_id = ?;',
		#			           (page_title, page_is_redirect, page_id))

		#	if int(page_id) % 1009 == 0:
		#		print(f'\r[Info] Current id: {page_id}', end='')
	connection.commit()


def main():
	language_code = 'en'
	date = '20180801'
	connection = create_database(language_code)
	insert_into_redirect(connection, language_code, date)
	insert_into_pagelinks(connection, language_code, date)
	insert_into_page(connection, language_code, date)