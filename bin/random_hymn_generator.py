import configparser
from datetime import date, timedelta
import random
import smtplib
import os
from email.message import EmailMessage
from mysql_connection import MySQLConnection
from main.app import App
from abc import ABC, abstractmethod 


DEFAULT_CRED_FILE='{}/.config/logins.ini'.format(os.environ['HOME'])


LOG = App().get_logger()

class RandomHymnGenerator(App):

	def add_config_options(self,p):
		g = p.add_argument_group(
			description='app specific options')
		g.add_argument('--num_hymns',
			type=int,
			default=10,
			help='Number of hymns to return')
		g.add_argument('--x_days_ago',
			type=int,
			default=15,
			help="Used to return hymns that haven't been selected within last x days")
		g.add_argument('--smtp_gmail_host',
			type=str,
			default='smtp.gmail.com:587',
			help="SMTP email gmail host")
		g.add_argument('--email_recipients',
			# required=True,
			action='append',
			help='List of emails to send the lineup to')
		super().add_config_options(p)


	def get_all_hymns(self, sql_conn, sql_cursor):
		query = "SELECT * FROM regular_hymns_{};".format(self.args.env.lower())
		hymns = sql_conn.run_query(sql_cursor, query)
		return hymns


	def get_random_lineup(self, hymns_list, sql_conn, sql_cursor):
		# need to handle case when all hymns have been practiced within x_days_ago (infinite loop)
		LOG.info("Generating random lineup!")
		lineup = []
		need_more_hymns = True
		while need_more_hymns:
			hymn = random.choice(hymns_list)
			if hymn not in lineup:
				x_days_ago_date = date.today() - timedelta(days=self.args.x_days_ago)
				if hymn['last_practiced'] is None:
					lineup.append(hymn)
				elif hymn['last_practiced'].date() <= x_days_ago_date:
					lineup.append(hymn)
			if len(lineup) == self.args.num_hymns:
				need_more_hymns = False
		return lineup


	def get_gmail_creds(self):
		LOG.info("Obtaining Gmail credentials.")
		config = configparser.ConfigParser()
		config.read(DEFAULT_CRED_FILE)
		if 'gmail' in config.sections():
			user = config['gmail']['user']
			password = config['gmail']['password']
			return (user,password)
		else:
			LOG.error('missing gmail creds')


	def generate_email_body(self, lineup):
		body = "Here are the hymns to practice today, {}:\n\n".format(
			date.today().strftime("%Y-%m-%d"))
		for hymn in lineup:
			body += "\t{}: {}\n".format(
				str(hymn['hymn_num']),
				hymn['title'])

		body += "\n\nHave fun!\nAlly"
		LOG.info(body)
		return body


	def generate_emails(self, body, email_creds):
		LOG.info("Generating email objects.")
		msgs = []
		for r in self.args.email_recipients:
			msg = EmailMessage()
			msg['From'] = email_creds[0] + '@gmail.com'
			msg['To'] = r
			msg['Subject'] = "Practice Lineup {}".format(
				date.today().strftime("%Y-%m-%d"))
			msg.set_content(body)
			msgs.append(msg)
		return msgs


	def send_emails(self, email_messages, host_creds):
		LOG.info("Sending {} e-mails".format(len(email_messages)))
		host = self.args.smtp_gmail_host
		with smtplib.SMTP(host) as server:
			server.ehlo()
			server.starttls()
			server.login(host_creds[0],host_creds[1])
			for msg in email_messages:
				server.send_message(msg)


	def update_last_practice(self, lineup, sql_conn, sql_cursor):
		LOG.info("Updating last practice dates for selected hymns.")
		for hymn in lineup:
			hymn_num = hymn['hymn_num']
			today = date.today().strftime("%Y-%m-%d")
			query = "UPDATE regular_hymns_{} SET last_practiced = '{}' WHERE hymn_num = {}".format(
				self.args.env.lower(),
				today,
				hymn_num)
			LOG.info(query)
			sql_conn.run_query(sql_cursor, query)


	def _run(self):
		self.add_config_options(self.parser)
		LOG.info(self.args)
		sql_conn = MySQLConnection()
		sql_cursor = sql_conn.cursor("DictCursor")
		hymns = self.get_all_hymns(sql_conn, sql_cursor)
		random_lineup = self.get_random_lineup(hymns, sql_conn, sql_cursor)
		email_body = self.generate_email_body(random_lineup)
		gmail_creds = self.get_gmail_creds()
		emails = self.generate_emails(email_body, gmail_creds)
		self.send_emails(emails, gmail_creds)
		self.update_last_practice(random_lineup, sql_conn, sql_cursor)
		sql_conn.close_cursor(sql_cursor)
		sql_conn.close_connection()


if __name__=="__main__":
	RandomHymnGenerator().start()


