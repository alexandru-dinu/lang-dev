SRC := $(shell find . -name "*.py")

format:
	@autoflake --remove-all-unused-imports -i $(SRC) \
		&& isort $(SRC) \
		&& black $(SRC)

test:
	python3 memory.py

clean:
	@find . -name "__pycache__" -print0 | xargs -0 rm -rfv
	@find . -name ".pytest_cache" -print0 | xargs -0 rm -rfv