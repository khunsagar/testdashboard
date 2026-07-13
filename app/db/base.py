"""
Declarative base that all SQLAlchemy models inherit from.

Alembic's env.py imports Base.metadata from here to autogenerate migrations,
so every new model file must be imported into app/db/base_models.py
(created in Step 4) to be picked up.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
