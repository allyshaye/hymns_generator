import configparser
from datetime import date, timedelta
import random
import smtplib
import os
from email.message import EmailMessage
import sys
from mysql_connection import MySQLConnection
from main.app import App


DEFAULT_CRED_FILE='{}/.config/logins.ini'.format(os.environ['HOME'])
SQL_DIR='./sql'
DATE_FORMAT="%Y-%m-%d"

LOG = App().get_logger()

class RandomHymnGenerator(App):


    def __init__(self):
        self.args = self.add_config_options()


    def add_config_options(self):
        p = self.get_basic_parser()
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
            required=True,
            action='append',
            help='List of emails to send the lineup to')
        args = p.parse_args()
        return args


    def get_all_hymns(self, sql_conn, sql_cursor):
        with open(SQL_DIR+'/select_all.sql', 'r') as f:
            raw_sql = f.read()
        query = raw_sql.format(env=self.args.env.lower())
        hymns = sql_conn.run_query(sql_cursor, query)
        return hymns


    def get_qualifying_hymns(self, hymns_list):
        hymns = []
        x_days_ago_date = date.today() - timedelta(days=self.args.x_days_ago)
        for hymn in hymns_list:
            if hymn['last_practiced'] is None:
                hymns.append(hymn)
            elif hymn['last_practiced'].date() <= x_days_ago_date:
                hymns.append(hymn)
        return hymns


    def get_random_lineup(self, sql_conn, sql_cursor):
        LOG.info("Generating random lineup!")
        num_hymns = self.args.num_hymns
        x_days_ago = self.args.x_days_ago
        all_hymns = self.get_all_hymns(sql_conn, sql_cursor)
        qualified_hymns = self.get_qualifying_hymns(all_hymns)
        if not qualified_hymns:
            LOG.error("All hymns been selected within the last {} days. Lessen the threshold and try again.".format(
                x_days_ago))
            sys.exit()
        elif len(qualified_hymns) <= num_hymns:
            LOG.info("Only {} hymns meet the threshold for last practiced ({} days ago).".format(
                len(qualified_hymns),
                x_days_ago))
            return qualified_hymns
        else:
            LOG.info("{} hymns to choose from".format(len(qualified_hymns)))
            lineup = []
            for i in range(0,num_hymns):
                hymn = random.choice(qualified_hymns)
                lineup.append(hymn)
                qualified_hymns.remove(hymn)
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
            sys.exit()


    def generate_email_body(self, lineup):
        body = "Here are the hymns to practice today, {}:\n\n".format(
            date.today().strftime(DATE_FORMAT))
        for hymn in lineup:
            body += "\t{}: {}\n".format(
                str(hymn['hymn_num']),
                hymn['title'])

        body += "\n\nHave fun!\nAlly"
        LOG.info("Email body:\n{}".format(body))
        return body


    def generate_emails(self, body, email_creds):
        LOG.info("Generating email objects.")
        msgs = []
        for r in self.args.email_recipients:
            msg = EmailMessage()
            msg['From'] = email_creds[0] + '@gmail.com'
            msg['To'] = r
            msg['Subject'] = "Practice Lineup {}".format(
                date.today().strftime(DATE_FORMAT))
            msg.set_content(body)
            msgs.append(msg)
        return msgs


    def send_emails(self, lineup):
        LOG.info("Sending {} e-mails".format(len(self.args.email_recipients)))
        email_body = self.generate_email_body(lineup)
        gmail_creds = self.get_gmail_creds()
        email_messages = self.generate_emails(email_body, gmail_creds)
        host = self.args.smtp_gmail_host
        with smtplib.SMTP(host) as server:
            server.ehlo()
            server.starttls()
            server.login(gmail_creds[0],gmail_creds[1])
            for msg in email_messages:
                LOG.info("Sending e-mail to {}".format(msg['To']))
                server.send_message(msg)


    def update_last_practice(self, lineup, sql_conn, sql_cursor):
        LOG.info("Updating last practice dates for selected hymns in MySQL control tables")
        for hymn in lineup:
            hymn_num = hymn['hymn_num']
            today = date.today().strftime(DATE_FORMAT)
            with open(SQL_DIR+'/update.sql', 'r') as f:
                raw_sql = f.read()
            query = raw_sql.format(
                env=self.args.env.lower(),
                today=today,
                hymn_num=hymn_num)
            sql_conn.run_query(sql_cursor, query)


    def close_sql(self, sql_conn, sql_cursor):
        LOG.info("Closing MySQL connection")
        sql_conn.close_cursor(sql_cursor)
        sql_conn.close_connection()


    def _run(self):
        LOG.info(self.args)
        sql_conn = MySQLConnection()
        sql_cursor = sql_conn.cursor("DictCursor")
        lineup = self.get_random_lineup(sql_conn, sql_cursor)
        if lineup:
            self.send_emails(lineup)
        self.update_last_practice(lineup,sql_conn,sql_cursor)
        self.close_sql(sql_conn, sql_cursor)


if __name__=="__main__":
    RandomHymnGenerator().start()