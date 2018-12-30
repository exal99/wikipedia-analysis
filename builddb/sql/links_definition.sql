DROP TABLE IF EXISTS links;

CREATE TABLE links(
	id int PRIMARY KEY,
	incoming_count int,
	outgoing_count int,
	incoming_links integer[],
	outgoing_links integer[]
);

-- COPY links FROM STDIN WHERE DELIMITER '\t' CSV;

-- CREATE INDEX pl_from_index ON pagelinks (pl_from);
-- CREATE INDEX pl_target_index ON pagelinks (pl_target); 