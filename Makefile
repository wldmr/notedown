.PHONY: test

tags: *.py
	find . -name "*.py" | ctags -L -

test:
	python3 -m doctest `find . -name "*.py"`
	python3 -m unittest `find . -name "*_tests.py" | sed "s#\./##"`

rm_pycache:
	find . -name __pycache__ -exec rm -rf "{}" \;
