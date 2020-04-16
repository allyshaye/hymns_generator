CREATE TABLE IF NOT EXISTS regular_hymns (
	`hymn_num` int NOT NULL,
	`title` varchar(256) NOT NULL,
	`revision_date` date NOT NULL,
	`last_practiced` timestamp DEFAULT NULL,
	`created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
	`updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (hymn_num)
)


