CREATE TABLE IF NOT EXISTS regular_hymns (
	`hymn_num` int NOT NULL,
	`name` varchar(256) NOT NULL,
	`revision_date` timestamp NOT NULL,
	`last_practiced` timestamp NOT NULL,
	`created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
	`updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (hymn_num)
)


