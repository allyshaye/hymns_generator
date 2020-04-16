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
	parser.add_argument('--env',
		required=True,
		type=str,
		choices=['prod','dev'])
	args = parser.parse_args()
	return args


def get_all_hymns(env,sql_conn, sql_cursor):
	query = "SELECT * FROM regular_hymns_{};".format(env)
	hymns = sql_conn.run_query(sql_cursor, query)
	return hymns


def get_random_lineup(num_hymns, x_days_ago, hymns_list, sql_conn, sql_cursor):
	# need to handle case when all hymns have been practiced within x_days_ago (infinite loop)
	LOG.info("Generating random lineup!")
	lineup = []
	need_more_hymns = True
	while need_more_hymns:
		hymn = random.choice(hymns_list)
		if hymn not in lineup:
			x_days_ago_date = date.today() - timedelta(days=x_days_ago)
			if hymn['last_practiced'] is None:
				lineup.append(hymn)
			elif hymn['last_practiced'].date() <= x_days_ago_date:
				lineup.append(hymn)
		if len(lineup) == num_hymns:
			need_more_hymns = False
	return lineup


def get_gmail_creds():
	LOG.info("Obtaining Gmail credentials.")
	config = configparser.ConfigParser()
	config.read(DEFAULT_CRED_FILE)
	if 'gmail' in config.sections():
		user = config['gmail']['user']
		password = config['gmail']['password']
		return (user,password)
	else:
		LOG.error('missing gmail creds')


def generate_email_body(lineup):
	body = "Here are the hymns to practice today, {}:\n\n".format(
		date.today().strftime("%Y-%m-%d"))
	for hymn in lineup:
		body += "\t{}: {}\n".format(
			str(hymn['hymn_num']),
			hymn['title'])

	body += "\n\nHave fun!\nAlly"
	LOG.info(body)
	return body


def generate_emails(body, email_recipients, email_creds):
	LOG.info("Generating email objects.")
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
	LOG.info("Sending {} e-mails".format(len(email_messages)))
	with smtplib.SMTP(host) as server:
		server.ehlo()
		server.starttls()
		server.login(host_creds[0],host_creds[1])
		for msg in email_messages:
			server.send_message(msg)


def update_last_practice(lineup, sql_conn, sql_cursor,env):
	LOG.info("Updating last practice dates for selected hymns.")
	for hymn in lineup:
		hymn_num = hymn['hymn_num']
		today = date.today().strftime("%Y-%m-%d")
		query = "UPDATE regular_hymns_{} SET last_practiced = '{}' WHERE hymn_num = {}".format(env,today,hymn_num)
		LOG.info(query)
		sql_conn.run_query(sql_cursor, query)




if __name__=="__main__":
	args = get_args()
	LOG.info(args)
	sql_conn = MySQLConnection()
	sql_cursor = sql_conn.cursor("DictCursor")
	hymns = get_all_hymns(args.env.lower(),sql_conn, sql_cursor)
	random_lineup = get_random_lineup(
		args.num_hymns,
		args.x_days_ago,
		hymns,
		sql_conn,
		sql_cursor)
	email_body = generate_email_body(random_lineup)
	gmail_creds = get_gmail_creds()
	emails = generate_emails(
		email_body,
		args.email_recipients, 
		gmail_creds)
	send_emails(args.smtp_gmail_host, 
		emails, 
		gmail_creds)
	update_last_practice(random_lineup, sql_conn, sql_cursor,args.env.lower())
	sql_conn.close_cursor(sql_cursor)
	sql_conn.close_connection()



