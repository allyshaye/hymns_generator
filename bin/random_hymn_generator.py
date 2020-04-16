# takes in a configurable # of hymns
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


from mysql_connection import MySQLConnection



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


if __name__=="__main__":
	args = get_args()
	print(args)