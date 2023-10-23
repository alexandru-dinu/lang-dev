SRC := $(shell find . -name "*.py")

.PHONY: format test clean

format:
	@autoflake --remove-all-unused-imports -i $(SRC) \
		&& isort $(SRC) \
		&& black $(SRC)

clean:
	@find . -name "__pycache__" -print0 | xargs -0 rm -rfv
	@find . -name ".pytest_cache" -print0 | xargs -0 rm -rfv
	@find . -name ".hypothesis" -print0 | xargs -0 rm -rfv
