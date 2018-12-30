DROP TABLE IF EXISTS redirect;

CREATE TABLE redirect(
	rd_from int PRIMARY KEY,
	rd_target int NOT NULL
);

-- COPY redirect FROM STDIN WHERE DELIMITER '\t' CSV;