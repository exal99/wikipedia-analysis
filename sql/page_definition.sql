CREATE TABLE page(
	page_id UNSIGNED int(10) UNIQUE NOT NULL,
	page_title varchar(255) NOT NULL,
	page_is_redirect UNSIGNED tinyint(3)  NOT NULL
);