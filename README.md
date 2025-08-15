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

4. Access the application at `http://localhost:8080`

## API Documentation

TODO:

## Run Tests (Unit & Integration)
```bash

TODO:
