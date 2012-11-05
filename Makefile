all:
	appcfg.py update .
clean:
	find . -name "*.pyc" | xargs rm -f
check:
	pylint -E -iy *.py controllers/*.py models/*.py utils/*.py
