from mysql_connection import MySQLConnection
from data_generator import DataGenerator


def get_raw_sql(sql_file):
	with open(sql_file, 'r') as f:
		query = f.read()
	return query

def create_hymns_table(create_sql_file, sql_conn, sql_cursor):
	create_sql = get_raw_sql(create_sql_file)
	sql_conn.run_query(sql_cursor, create_sql)

def seed_hymns_table(insert_sql_file, num_records, sql_conn, sql_cursor):
	raw_sql = get_raw_sql(insert_sql_file)
	dg = DataGenerator()
	titles = dg.get_random_titles(num_records)
	dates = dg.get_fake_past_dates(num_records)
	for i in range(0,num_records):
		hymn = str(i+1)
		t = titles[i]
		revision = dates[i].strftime('%Y-%m-%d')
		query = raw_sql.format(
			hymn_num = hymn,
			title = t,
			revision_date = revision)
		print(query)		
		r = sql_conn.run_query(sql_cursor,query)
		print(r)



if __name__=="__main__":
	mysql_conn = MySQLConnection()
	mysql_cursor = mysql_conn.cursor('DictCursor')
	create_hymns_table(
		create_sql_file = '../sql/create_tables.sql',
		sql_conn = mysql_conn,
		sql_cursor = mysql_cursor)
	seed_hymns_table(
		insert_sql_file='../sql/insert.sql',
		num_records=100,
		sql_conn = mysql_conn,
		sql_cursor=mysql_cursor)
	mysql_conn.close_cursor(mysql_cursor)
	mysql_conn.close_connection()