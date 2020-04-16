# takes in a configurable # of hymns x
# takes count of hymns in table
# no. of hymns times, selects random hymn
	# checks that the hymn has not already been selected
	# checks for last_practiced date and compares it to a configurable threshold
	# if it's been greater than threshold days since practicing:
		# add the hymn to list of hymns to return
# does an execute many to update the last practiced dates for all the hymns that have been selected
# sends an e-mail with the hymns and also logs the hymns
# if e-mail is sent successfully: updates ctrl table for random_hymn_generator with last run (need to create this table) with SUCCESS, else FAILURE

import configargparse
import logging
from datetime import date


from mysql_connection import MySQLConnection

logging.basicConfig(
	format='%(asctime)s %(filename)s %(funcName)s %(levelname)s:  %(message)s', 
	level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_args():
	parser = configargparse.ArgParser(
		description='app-specific options: Random Hymn Generator')
	parser.add_argument('--config', '-c',
		required=False,
		help='path to config file',
		is_config_file=True)
	parser.add_argument('--num_hymns',
		type=int,
		default=10,
		help='Number of hymns to return')
	parser.add_argument('--x_days_ago',
		type=int,
		default=15,
		help="Returns hymns that haven't been selected within last x days")
	args = parser.parse_args()
	return args


def get_all_hymns(sql_conn, sql_cursor):
	query = "SELECT distinct(hymn_num) FROM regular_hymns;"
	results = sql_conn.run_query(sql_cursor, query)
	hymns = [r['hymn_num'] for r in results]
	return hymns




if __name__=="__main__":
	args = get_args()
	sql_conn = MySQLConnection()
	sql_cursor = sql_conn.cursor("DictCursor")
	print(args)
	hymns = get_all_hymns(sql_conn, sql_cursor)
	print(hymns)
	logger.warning('hello')



