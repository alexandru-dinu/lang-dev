.PHONY: test
test:
	uv run pytest -v src/*.py
