CREATE TABLE redirect(
	rd_from UNSIGNED int(10) UNIQUE NOT NULL,
	rd_target UNSIGNED int(10) NOT NULL
);