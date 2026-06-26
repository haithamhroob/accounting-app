# Lightweight Accounting System

A lightweight, fully Arabic (RTL) double-entry accounting web application built with Django and PostgreSQL. It manages parties (customers and suppliers), sales and purchase invoices, payments, an automated ledger, and balance reporting — designed to run locally on Windows or in Docker.

## Features

- ✅ Fully Arabic Right-to-Left (RTL) user interface
- ✅ Party management (customers and suppliers)
- ✅ Sales and purchase invoice management
- ✅ Payment recording and tracking
- ✅ Automated ledger entries based on accounting rules
- ✅ Balance and period summary reports
- ✅ Django admin dashboard
- ✅ REST API with JWT authentication and OpenAPI documentation
- ✅ Excel import/export support
- ✅ Containerized with Docker and Docker Compose
- ✅ Health-check endpoint for monitoring

## Tech Stack

| Layer            | Technology                                             |
|------------------|--------------------------------------------------------|
| Backend          | Django 5.x                                             |
| API              | Django REST Framework, SimpleJWT, drf-spectacular      |
| Database         | PostgreSQL 15                                          |
| Data Processing  | pandas, openpyxl                                       |
| Server           | Gunicorn, WhiteNoise                                   |
| Containerization | Docker, Docker Compose                                 |
| Config           | python-dotenv, dj-database-url                         |
| Filtering        | django-filter                                          |

## Prerequisites

- Python 3.11+
- PostgreSQL (localhost:5432)
- pgAdmin (optional, for database management)
- Docker (optional, for containerized deployment)

## Local Setup

### 1. Create the Database

Open `psql` or pgAdmin and run:

```sql
CREATE DATABASE accounting_db;
```

### 2. Create a Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```powershell
Copy-Item .env.example .env
```

Edit the `.env` file with your database credentials:

```
DB_NAME=accounting_db
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-change-this
DEBUG=True
```

### 5. Apply Database Migrations

```powershell
python manage.py makemigrations parties invoices payments ledger
python manage.py migrate
```

### 6. Create an Admin User

```powershell
python manage.py createsuperuser
```

### 7. Run the Development Server

```powershell
python manage.py runserver
```

Open your browser at: http://localhost:8000

## Docker Deployment

Run the entire stack (PostgreSQL + Django) with a single command:

```powershell
docker-compose up --build
```

The app will be available at http://localhost:8000.

## Application Routes

| Page            | URL                                    |
|-----------------|----------------------------------------|
| Home            | http://localhost:8000/                 |
| Parties         | http://localhost:8000/parties/         |
| Invoices        | http://localhost:8000/invoices/        |
| Period Summary  | http://localhost:8000/reports/summary/ |
| Admin Dashboard | http://localhost:8000/admin/           |
| Health Check    | http://localhost:8000/health           |

## Project Structure

```
accounting-system/
├── core/               # Django project settings
├── parties/            # Parties app (customers & suppliers)
├── invoices/           # Invoices app (sales & purchases)
├── payments/           # Payments app
├── ledger/             # Automated ledger app
├── reports/            # Reporting app
├── api/                # REST API endpoints
├── templates/          # Shared HTML templates
├── static/             # Static assets
├── Dockerfile          # Container image definition
├── docker-compose.yml  # Multi-container orchestration
├── requirements.txt    # Python dependencies
├── manage.py           # Django management entry point
├── .env.example        # Environment variable template
└── README.md           # This file
```

## Accounting Rules

### Invoices
- A **sales invoice** to a customer creates a **debit entry** against that customer.
- A **purchase invoice** from a supplier creates a **credit entry** against that supplier.

### Payments
- A **payment received** from a customer creates a **credit entry** (reduces their debit balance).
- A **payment made** to a supplier creates a **debit entry** (reduces their credit balance).

### Balance Calculation
- **Balance = Total Debit − Total Credit**
- A **positive balance** means the party owes us.
- A **negative balance** means we owe the party.

## Health Check

Verify that the application and database are running correctly:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

Expected response:

```json
{
    "status": "ok",
    "database": "connected"
}
```

## Learning Outcomes

This project demonstrates practical experience with:

- Designing a modular, multi-app Django architecture
- Implementing double-entry accounting logic in software
- Building and securing a REST API with JWT authentication
- Containerizing a full-stack application with Docker Compose
- Integrating a relational database (PostgreSQL) with an ORM
- Generating API documentation with OpenAPI/Swagger
- Managing environment-based configuration for dev and production

## License

All rights reserved © 2026.
