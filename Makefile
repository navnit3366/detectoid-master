all: test flake

go-dev:
	ln -sf dev.cfg buildout.cfg

env:go-dev
	python bootstrap-buildout.py
	bin/buildout

test:
	@echo "==== Running nosetests ===="
	@bin/test detectoid

flake:
	@echo "==== Running Flake8 ===="
	@bin/flake8 detectoid/*.py

clean:
	rm -r bin/ eggs/ detectoid.egg-info/
	rm .installed.cfg .coverage coverage.xml nosetests.xml
	rm -r docs/html/ docs/doctrees/ docs/Makefile docs/make.bat
	find . -name "*.pyc" -delete

serve:
	bin/pserve pyramid.ini

doc:
	$(MAKE) -C docs html
