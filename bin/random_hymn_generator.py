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
import configparser
import logging
from datetime import date, timedelta
import random
import smtplib
import os
from email.message import EmailMessage

from mysql_connection import MySQLConnection

DEFAULT_CRED_FILE='{}/.config/logins.ini'.format(os.environ['HOME'])

def get_logger():
	logging.basicConfig(
		format='%(asctime)s %(filename)s %(funcName)s %(levelname)s:  %(message)s',
		level=logging.DEBUG)
	logger = logging.getLogger(__name__)
	return logger


LOG = get_logger()


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
		help="Used to return hymns that haven't been selected within last x days")
	parser.add_argument('--smtp_gmail_host',
		type=str,
		default='smtp.gmail.com:587',
		help="SMTP email gmail host")
	parser.add_argument('--email_recipients',
		required=True,
		action='append',
		help='List of emails to send the lineup to')
	args = parser.parse_args()
	LOG.info(args)
	return args


def get_all_hymns(sql_conn, sql_cursor):
	query = "SELECT * FROM regular_hymns;"
	hymns = sql_conn.run_query(sql_cursor, query)
	return hymns


def get_random_lineup(num_hymns, x_days_ago, hymns_list, sql_conn, sql_cursor):
	lineup = []
	need_more_hymns = True
	while need_more_hymns:
		hymn = random.choice(hymns_list)
		if hymn not in lineup:
			x_days_ago_date = date.today() - timedelta(days=x_days_ago)
			if hymn['last_practiced'] is None:
				lineup.append(hymn)
			elif hymn['last_practiced'] <= x_days_ago_date:
				lineup.append(hymn)
		if len(lineup) == num_hymns:
			need_more_hymns = False
	return lineup


def get_gmail_creds():
	config = configparser.ConfigParser()
	config.read(DEFAULT_CRED_FILE)
	if 'gmail' in config.sections():
		user = config['gmail']['user']
		password = config['gmail']['password']
		LOG.info(user)
		LOG.info(password)
		return (user,password)
	else:
		LOG.error('missing gmail creds')


def generate_email_body(lineup):
	body = "\nHere are the hymns to practice today, {}:\n\n".format(
		date.today().strftime("%Y-%m-%d"))
	for hymn in lineup:
		body += "\t{}: {}\n".format(
			str(hymn['hymn_num']),
			hymn['title'])

	body += "\n\nHave fun!\nAlly"
	LOG.info(body)
	return body



def generate_emails(body, email_recipients, email_creds):
	msgs = []
	for r in email_recipients:
		msg = EmailMessage()
		msg['From'] = email_creds[0] + '@gmail.com'
		msg['To'] = r
		msg['Subject'] = "Practice Lineup {}".format(
			date.today().strftime("%Y-%m-%d"))
		msg.set_content(body)
		msgs.append(msg)
	return msgs


def send_emails(host, email_messages, host_creds):
	with smtplib.SMTP(host) as server:
	# server = smtplib.SMTP(host)
		server.ehlo()
		server.starttls()
		server.login(host_creds[0],host_creds[1])
		for msg in email_messages:
			LOG.info(msg)
			server.send_message(msg)


if __name__=="__main__":
	args = get_args()
	sql_conn = MySQLConnection()
	sql_cursor = sql_conn.cursor("DictCursor")
	hymns = get_all_hymns(sql_conn, sql_cursor)
	random_lineup = get_random_lineup(
		args.num_hymns,
		args.x_days_ago,
		hymns,
		sql_conn,
		sql_cursor)
	for i in random_lineup:
		LOG.info('{}\n'.format(i))
	email_body = generate_email_body(random_lineup)
	gmail_creds = get_gmail_creds()
	emails = generate_emails(email_body,args.email_recipients, gmail_creds)
	send_emails(args.smtp_gmail_host, emails, gmail_creds)



