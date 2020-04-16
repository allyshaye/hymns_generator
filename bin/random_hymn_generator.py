# takes in a configurable # of hymns
# takes count of hymns in table
# no. of hymns times, selects random hymn
	# checks that the hymn has not already been selected
	# checks for last_practiced date and compares it to a configurable threshold
	# if it's been greater than threshold days since practicing:
		# add the hymn to list of hymns to return
# does an execute many to update the last practiced dates for all the hymns that have been selected
# sends an e-mail with the hymns and also logs the hymns
# updates ctrl table for random_hymn_generator with last run (need to create this table)