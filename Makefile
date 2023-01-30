build: clean test
	python3 -m build

clean:
	rm -rf dist

test:
	python3 -m unittest discover

release: clean test build
	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*
