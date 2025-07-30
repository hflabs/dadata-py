build:
	uv build

lint:
	uv run ruff check 
	uv run ruff format

test:
	uv run pytest -ra
