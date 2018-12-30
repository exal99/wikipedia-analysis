import argparse
import gzip


def valid_zip_checker(parser, path):
	try:
		with gzip.open(path) as f:
			pass
	except (IOError, OSError):
		parser.error(f"'{path}' is not a valid zip file")
	if not path.endswith(".gz"):
		parser.error(f"'{path}' is not a valid zip file")
