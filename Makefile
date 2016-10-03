.PHONY: check, tcheck, pep8, pyflakes, lint, wc, clean, update-prosite, perf

# If you are on OS X, you'll need the GNU version of find. If you're using
# brew, run brew install findutils (which installs gfind in /usr/local/bin).
FIND := $(shell which gfind || which find)

XARGS := xargs $(shell test $$(uname) = Linux && echo -r)


check:
	python -m discover -v

tcheck:
	trial --rterrors test

pep8:
	$(FIND) . -name '*.py' -print0 | $(XARGS) -0 pep8

pyflakes:
	$(FIND) . -name '*.py' -print0 | $(XARGS) -0 pyflakes

lint: pep8 pyflakes

wc:
	$(FIND) . -name '*.py' -print0 | $(XARGS) -0 wc -l

clean:
	$(FIND) . \( -name '*.pyc' -o -name '*~' \) -print0 | $(XARGS) -0 rm
	$(FIND) . -name __pycache__ -type d -print0 | $(XARGS) -0 rmdir
	$(FIND) . -name _trial_temp -type d -print0 | $(XARGS) -0 rm -r
	rm -fr build
