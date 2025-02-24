# Notes App

A note-taking application that allows users to organize and manage their notes in different categories with an aesthetic interface

## About the code

There are three main components in this project:
- Backend API server: Django REST framework
- Frontend: Next.js
- Database: PostgreSQL

## How to build

```bash
docker-compose build
```

## How to run

```bash
docker-compose up
```

## Inital setup

Run the create initial db objects command to create the initial database objects: superuser and base categories.
```bash
docker-compose run --rm backend python manage.py create_init_objects
```

_Project built by Turbo_
