# Database migrations

The application keeps SQLAlchemy models in `backend/app/models/entities.py`.
Generate and apply migrations with Alembic after reviewing the generated SQL:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Local zero-configuration runs use SQLite. Production configuration points the
same metadata at PostgreSQL 16 with pgvector enabled.

