lint:
	python3 -m isort .
	python3 -m black .
	python3 -m pylama .
	python3 -m pydocstyle .

test:
	python -m pytest \
	tests/

cov:
	python -m pytest \
	--cov=backtrack \
	--cov-report html \
	--cov-report term \
	tests/

