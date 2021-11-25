# run tests via pytest, creates coverage report, and then opens it up
test:
    coverage run -m pytest 
    coverage html --omit=the_well_maintained_test/cli.py--omit=the_well_maintained_test/cli.py
    open htmlcov/index.html

check:
    pre-commit run --all-files

coverage:
    open htmlcov/index.html