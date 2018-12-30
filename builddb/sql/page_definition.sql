DROP TABLE IF EXISTS page;

CREATE TABLE page(
	page_id int PRIMARY KEY,
	page_title varchar(255) NOT NULL,
	page_is_redirect BOOLEAN NOT NULL
);

CREATE INDEX page_title_index ON page (page_title); 