uvicorn main:app --reload 
docker-compose up -d pg
docker-compose down -v pg 
alembic revision --autogenerate -m "init alembic"