import sqlite3
import gzip
import time
import sys
from functools import wraps

def measure_speed(iterator):
	"""
	Iterator speed measurement decorator
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
	print('[Info] Building \'redirect\' table')
	with gzip.open(f'database/{language_code}wiki-{date}-redirect.sql.gz') as redirect:
		connection.executemany('INSERT INTO redirect VALUES (?,?);', redirect_iterator(redirect))
	connection.commit()

@measure_speed
def pagelinks_iterator(pagelinks_file):
	for pl_from, pl_target in map(lambda x: x[:-1].split(','), map(bytes.decode, pagelinks_file)):
		yield (pl_from, pl_target)

def insert_into_pagelinks(connection, language_code, date):
	print('[Info] Building \'pagelinks\' table')
	with gzip.open(f'database/{language_code}wiki-{date}-pagelinks.sql.gz') as pagelinks:
		connection.executemany('INSERT INTO pagelinks VALUES (?,?);', pagelinks_iterator(pagelinks))
	print("[Info] Creating index", end='')
	sys.stdout.flush()
	connection.commit()
	connection.execute("CREATE INDEX pl_from_index on pagelinks (pl_from);") # creates index after insert for faster build time
	connection.execute("CREATE INDEX pl_target_index on pagelinks (pl_target);")
	print("    Done")
	sys.stdout.flush()

def _split_page_line(line):
	page_id          = line.split(',')[0]
	page_title       = line[line.index(',') + 2:-4]
	page_is_redirect = line[-2:-1]
	return page_id, page_title, page_is_redirect


@measure_speed
def page_iterator(page_file):
	for page_id, page_title, page_is_redirect in map(_split_page_line, map(bytes.decode, page_file)):
		yield (page_id, page_title, page_is_redirect)

def insert_into_page(connection, language_code, date):
	print('[Info] Building \'page\' table')
	with gzip.open(f'database/{language_code}wiki-{date}-page.sql.gz') as page:
		connection.executemany('INSERT INTO page VALUES (?,?,?);', page_iterator(page))
	connection.commit()


def main():
	language_code = 'en'
	date = '20180801'
	connection = create_database(language_code)
	insert_into_redirect(connection, language_code, date)
	insert_into_pagelinks(connection, language_code, date)
	insert_into_page(connection, language_code, date)