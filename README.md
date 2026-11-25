# Pet Shelter Management System

A modular, console-based Pet Shelter Management System written in Python. It demonstrates object-oriented programming, inheritance, polymorphism, custom exceptions, decorators, JSON persistence, validation, and automated testing.

## Requirements

- Python 3.10 or newer
- Python standard library only

## Run the application

From this directory, run:

```bash
python main.py
```

The application creates `data/database.json` and `logs/shelter.log` when needed. The database is local runtime data and is intentionally excluded from Git because it can contain adopter names, phone numbers, and national IDs.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Features

- Register, display, remove, and search animals
- Search animals by name and species
- Adopt and return animals
- Display available and adopted animals
- `Animal` base class with `Dog`, `Cat`, `Bird`, and `Horse` subclasses
- Inheritance and polymorphic `make_sound()` methods
- Adopter registration and a maximum of nine active adoptions per adopter
- Validation of Iranian mobile-number format (`09xxxxxxxxx`) and ten-digit national-ID format
- Custom exceptions and controlled command-line error handling
- Decorators for operation logging and execution-time measurement
- JSON persistence with atomic file replacement
- Validation of database structure and animal/adopter relationships
- Timestamped health records and adoption/return history
- Shelter summaries, statistics, filtering, and sorting
- Automated unit and command-line integration tests

## Project structure

```text
Oraz Tahmasbi_python_petshelter/
├── animals.py
├── people.py
├── shelter.py
├── exceptions.py
├── decorators.py
├── reports.py
├── storage.py
├── main.py
├── data/
├── logs/
└── tests/
```

## Privacy and security

The database may contain personal information, including phone numbers and national IDs. Keep the runtime database and log files private. They are excluded from the repository by `.gitignore`. This is an educational management application, not a production system for processing real personal data.
