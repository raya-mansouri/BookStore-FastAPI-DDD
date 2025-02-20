#! /bin/bash
#!/bin/bash

# Run Alembic migrations
alembic upgrade head

# Execute the init.sql file to insert data into the database
#psql -U your_db_user -d your_db_name -f /app/init.sql

# Start the FastAPI app with Uvicorn
uvicorn app.main:app --workers 1 --host 0.0.0.0 --port 8000 --reload

