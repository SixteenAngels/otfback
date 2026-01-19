# Alembic configuration script

"""Alembic configuration"""

from alembic import config
import os

# Initialize alembic configuration
alembic_config = config.Config("alembic.ini")

# Commands:
# alembic revision --autogenerate -m "message"  - Generate migration
# alembic upgrade head                          - Apply all pending migrations
# alembic downgrade -1                          - Rollback last migration
