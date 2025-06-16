.PHONY: db-up

db-up:
alembic upgrade head
