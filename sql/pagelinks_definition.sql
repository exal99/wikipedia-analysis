CREATE TABLE pagelinks(
	pl_from UNSIGNED int(10) NOT NULL,
	pl_target UNSIGNED int(10) NOT NULL
);

-- CREATE INDEX pl_from_index ON pagelinks (pl_from);
-- CREATE INDEX pl_target_index ON pagelinks (pl_target); 