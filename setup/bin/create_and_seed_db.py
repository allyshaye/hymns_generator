from main.app import App
from mysql_connection import MySQLConnection
from data_generator import DataGenerator

LOG = App().get_logger()

class CreateAndSeedDevDb(App):

	def __init__(self):
		self.args = self.add_config_options()

	def add_config_options(self):
		p = self.get_basic_parser()
		g = p.add_argument_group(
			description='app specific options')
		g.add_argument('--num_records',
			required=True,
			type=int,
			help='Num of fake hymns to insert into table')
		g.add_argument('--create_sql_file',
			required=True,
			type=str,
			help='Path to sql file to create tables')
		g.add_argument('--insert_sql_file',
			required=True,
			type=str,
			help='Path to sql file to insert values')
		args = p.parse_args()
		return args


	def get_raw_sql(self, sql_file):
		with open(sql_file, 'r') as f:
			query = f.read()
		return query


	def create_hymns_table(self, sql_conn, sql_cursor):
		LOG.info("Creating hymns table")
		create_sql = self.get_raw_sql(self.args.create_sql_file)
		sql_conn.run_query(sql_cursor, create_sql)


	def seed_hymns_table(self, sql_conn, sql_cursor):
		LOG.info("Seeding hymns table")
		raw_sql = self.get_raw_sql(self.args.insert_sql_file)
		dg = DataGenerator()
		num_records = self.args.num_records
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
			sql_conn.run_query(sql_cursor,query)


	def close_sql(self, sql_conn, sql_cursor):
		LOG.info("Closing MySQL connection")
		sql_conn.close_cursor(sql_cursor)
		sql_conn.close_connection()


	def _run(self):
		LOG.info(self.args)
		mysql_conn = MySQLConnection()
		mysql_cursor = mysql_conn.cursor('DictCursor')
		self.create_hymns_table(mysql_conn, mysql_cursor)
		self.seed_hymns_table(mysql_conn, mysql_cursor)
		self.close_sql(mysql_conn, mysql_cursor)


if __name__=="__main__":
	CreateAndSeedDevDb().start()