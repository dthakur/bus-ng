all:
	appcfg.py --oauth2 update .
clean:
	find . -name "*.pyc" | xargs rm -f
serve:
	dev_appserver.py --use_sqlite --clear_datastore --high_replication .
check:
	pylint -E -iy *.py controllers/*.py models/*.py utils/*.py
