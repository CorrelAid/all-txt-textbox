api-start:
	cd ./backend/src && poetry run uvicorn api:app --reload && cd ..
alembic-revision:
	cd ./backend/src && poetry run python -m alembic revision -m "$(m)" --autogenerate --rev-id "$(rev-id)" && cd ../..
alembic-upgrade:
	cd ./backend/src && poetry run python -m alembic upgrade head && cd ../..
alembic-downgrade:
	cd ./backend/src && poetry run python -m alembic downgrade -1 && cd ../..
