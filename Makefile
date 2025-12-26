.PHONY: .uv  ## Check that uv is installed
.uv:
	@uv -V || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: format
format: .uv
	uv run ruff check --fix
	uv run ruff format

.PHONY: lint
lint: .uv
	uv run ruff check
	uv run ruff format --check
	uv run ty check
