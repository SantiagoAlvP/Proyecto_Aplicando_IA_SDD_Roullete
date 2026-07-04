# Project Jackpot


run tests

	uv run pytest -v
	uv run ruff format
	uv run ruff check --fix
	uv run ruff check

	uv run ty check 


	docker compose up api postgres