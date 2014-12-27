.PHONY: test

tags: *.py
	find . -name "*.py" | ctags -L -

test:
	python3 -m unittest
