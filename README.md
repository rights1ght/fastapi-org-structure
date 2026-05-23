# Company Structure API

REST API для управления древовидной структурой компании.

Стек: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker.

## Быстрый старт

```bash
docker compose up --build
```

Документация Swagger: http://localhost:8000/docs

## Локальный запуск

```bash
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/company_db
alembic upgrade head
uvicorn app.main:app --reload
```

## Тесты

```bash
pytest tests/ -v
```
