# RESQ AI

RESQ AI is a Streamlit prototype for disaster classification, severity assessment, rescue-priority scoring, map visualization, and guided safety information.

## Run the application

Install the dependencies and start the dashboard from the repository folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run RESQAI/dashboard.py
```

## SQLite database

The dashboard creates `resq_ai.db` in the repository folder the first time it starts. The database uses Python's built-in SQLite support, so no database server or extra package is needed.

Each analyzed emergency is saved automatically. Open **Reports** in the dashboard to view saved incidents after refreshing or restarting the app. The database also includes tables for disaster types, shelters, rescue teams, team assignments, and report update history.

The database schema is in `schema.sql`, and the Python connection and report functions are in `database.py`. To choose another database location, set the `RESQ_AI_DATABASE_PATH` environment variable before starting the dashboard.

The generated `resq_ai.db` file is ignored by Git because it can contain incident and contact information. The app recreates an empty database from `schema.sql` when needed. Do not treat AI severity or priority estimates as dispatch decisions; authorized responders must review them, and shelter details must be verified before use.

## Prototype limitations

- Map markers use manually entered coordinates and do not provide live GPS tracking.
- Map tiles require an internet connection.
- The AI assessment is preliminary decision support and does not contact or dispatch emergency services.
