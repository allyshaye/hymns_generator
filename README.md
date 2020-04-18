# hymns_generator

## Environment Setup
- Python Version: 3.7.7
- export PYTHONPATH=../ally-libs/python

## Run

`nohup python bin/random_hymn_generator.py -c cfg/random_hymn_generator.DEV.cfg >> /var/ally/log/random_hymn_generator/$(date +\%Y-\%m-%\d).log 2>&1`

## Successful Run

	04/18/2020 11:42:05AM - app.py - start (INFO):  APP START
	04/18/2020 11:42:05AM - random_hymn_generator.py - _run (INFO):  Namespace(config='cfg/random_hymn_generator.DEV.cfg', email_recipients=['allisonshaye@gmail.com'], env='dev', loglevel='INFO', num_hymns=5, smtp_gmail_host='smtp.gmail.com:587', x_days_ago=0)
	04/18/2020 11:42:05AM - random_hymn_generator.py - get_random_lineup (INFO):  Generating random lineup!
	04/18/2020 11:42:05AM - random_hymn_generator.py - get_random_lineup (INFO):  100 hymns to choose from
	04/18/2020 11:42:05AM - random_hymn_generator.py - send_emails (INFO):  Sending 1 e-mails
	04/18/2020 11:42:05AM - random_hymn_generator.py - generate_email_body (INFO):  Email body:
	Here are the hymns to practice today, 2020-04-18:

		66: Short Great
		26: Main Particular
		55: Official Heavy Name Oil
		37: Town Up Prepare
		79: Future Kid Avoid Interest Identify


	Have fun!
	Ally
	04/18/2020 11:42:05AM - random_hymn_generator.py - get_gmail_creds (INFO):  Obtaining Gmail credentials.
	04/18/2020 11:42:05AM - random_hymn_generator.py - generate_emails (INFO):  Generating email objects.
	04/18/2020 11:42:06AM - random_hymn_generator.py - send_emails (INFO):  Sending e-mail to allisonshaye@gmail.com
	04/18/2020 11:42:07AM - random_hymn_generator.py - update_last_practice (INFO):  Updating last practice dates for selected hymns in MySQL control tables
	04/18/2020 11:42:07AM - random_hymn_generator.py - close_sql (INFO):  Closing MySQL connection`

