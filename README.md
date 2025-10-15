# Secret Santa Webapp

This project contains a React frontend and a FastAPI backend.

## Backend Setup (FastAPI, SQLite, SQLAlchemy)

1. Create and activate a Python 3.13 virtual environment:
   ```sh
   python3.13 -m venv backend/.venv
   source backend/.venv/bin/activate
   ```
2. Install dependencies with uv:
   ```sh
   cd backend
   uv sync
   ```
3. Run the FastAPI server:
   ```sh
   uvicorn app:app --reload
   ```

## Frontend Setup (React)

1. Install dependencies:
   ```sh
   cd frontend
   npm install
   ```
2. Start the development server:
   ```sh
   npm start
   ```

## Notes
- The backend uses FastAPI, SQLAlchemy, and SQLite.
- The frontend uses React and npm.
- Ensure Python 3.13 and Node.js are installed on your system.

