.PHONY: test

tags: *.py
	ctags -R *.py

test:
	python3 -m unittest
