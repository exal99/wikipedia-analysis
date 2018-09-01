import gzip
import sqlite3
import functools
import re
import time

def compile_regex(nargs):
	return re.compile(r"\(([^,]*,){%d}[^,]*\)" %(nargs - 1))

PAGE_TABLE_REGEX = compile_regex(14)

def print_same(value, **kwargs):
	print(f"\r{' ': >60}", end = "", **kwargs)
	print(f"\r{value}", end = "", **kwargs)

def pprint_time(seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)
	format_str = lambda v1, v2, p: f"{v1:0>2}{p[0]}{v2:0>2}{p[1]}"
	if d > 0:
		return format_str(d, h, ("d","h"))
	elif h > 0:
		return format_str(h, m, ("h","m"))
	elif m > 0:
		return format_str(m, s, ("m","s"))
	else:
		return f" {s:0>2}sec"

def get_insert_statements(line, nargs): 
	regex = {
			  14:PAGE_TABLE_REGEX
			}
	res = regex[nargs].match(line) if nargs in regex else compile_regex(nargs).match(line)
	return res.span() if res else None

def calc_process_speed(iterator):
	last_time = time.time()
	start_time = round(last_time)
	lines_per_min = 0
	avrage_over = 15
	update_animation = 20
	animation = "/-\\|"
	animation_count = 0
	animation_time = time.time()
	for ind, val in enumerate(iterator):
		if ind % avrage_over == 0 and ind != 0:
			lines_per_min = round((avrage_over / (time.time() - last_time)) * 60)
			last_time = time.time()
		print_same(f"Current Line: {ind: >5}{lines_per_min: >8} lines/min " + 
				   f"{pprint_time(round(time.time()) - start_time): >8} " +
				   f"{animation[animation_count]}")
		if time.time() - animation_time > 0.2:
			animation_count = (animation_count + 1) % len(animation)
			animation_time = time.time()
		yield val
				
def insert_statement_iterator(lang, date, filename):
	full_name = get_file_path(lang, date, filename)
	with gzip.open(full_name) as original:
		print("STARTING")
		for line in calc_process_speed(original):
			line = line.decode()
			if line.startswith("INSERT"):
				yield from individual_statement_iterator(line)
			yield
			
				
def individual_statement_iterator(line):
	line = line[line.index("("):]
	res = get_insert_statements(line, 14)
	while res:
		row = line[slice(*res)]
		(namespace,) = get_values(row, (1,))
		if namespace == "0":
			yield row
		line = line[res[1] + 1:]
		res = get_insert_statements(line, 14)

def get_values(insert_values, args):
	values = insert_values[1:-1].split(",")
	return tuple([values[arg] for arg in args])

def get_file_path(lang, date, filename):
	return f"database/{lang}wiki-{date}-{filename}.sql.gz"

def process_page_table(lang, date):
	full_name = get_file_path(lang, date, "page") + ".tmp"
	with gzip.open(full_name, "wb") as output:
		line = "INSERT INTO page VALUES "
		for insert_row in insert_statement_iterator(lang, date, "page"):
			if insert_row:
				page_id, title, is_redirect = get_values(insert_row, (0,2,5))
				line += f"({page_id},{title},{is_redirect}),"
			elif insert_row is None and line.endswith(","):
				line = line[:-1] + ";\n"
				output.write(line.encode())
				line = "INSERT INTO page VALUES "
		
