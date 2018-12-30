DROP TABLE IF EXISTS paths;

CREATE TABLE paths(
	path_source INTEGER,
	path_target INTEGER,
	path_length INTEGER,
	npaths INTEGER,
	example_path INTEGER[],
	UNIQUE(path_source, path_length)
);