.PHONY: test

tags: *.py
	find . -name "*.py" | ctags -L -

test:
	python3 -m unittest

rm_pycache:
	find . -name __pycache__ -exec rm -rf "{}" \;
