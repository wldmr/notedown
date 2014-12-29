.PHONY: test

tags: *.py
	find . -name "*.py" | ctags -L -

test:
	python3 -m doctest `find . -name "*.py"`

rm_pycache:
	find . -name __pycache__ -exec rm -rf "{}" \;
