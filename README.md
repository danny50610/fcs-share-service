# FCS Share Service

Quick share FCS file to other

## Features
- Upload and share FCS files (public or private)
- View Statistics of shared files

## Technology Stack
- FastAPI
- PostgreSQL
- Redis
- Docker

## Installation (Docker)
1. Copy the example environment file for Docker:
```bash
cp .env.example .env.docker
```

2. Modify the `.env.docker` (SECRET_KEY)
```
SECRET_KEY="your_secret_key"
```

3. Build and run the Docker containers:
```bash
docker-compose up -d
```

4. Create the user, replace `<your_email>` with your email:
```bash
docker compose exec app python -m app.create_user "<your_email>"
```
Please remember password output by the command above.

5. Access the application doc at `http://localhost:8080/docs`

## API Documentation

You can access the API documentation at `http://localhost:8080/docs` when the application is running.

## Development

1. Install dependencies:
```
PIPENV_VENV_IN_PROJECT=1 pipenv install
```

2. Activate the virtual environment:
```
pipenv shell
```

3. Run the application:
```
fastapi dev app/main.py --port 8080
```

4. Run the worker:
```
celery --app=app.task.app worker --concurrency=1 --loglevel=DEBUG
```

### Run Tests (Unit & Integration)

1. create the `docker-compose.override.yaml` file with the following content:
```
services:
  postgresql-15:
    ports:
      - '54329:5432'
```

2. create the test database (only once):
```
docker compose exec postgresql-15 psql -U homestead -c "CREATE DATABASE \"homestead-test\";"
```

3. Run the tests:
```
python -m pytest
```
