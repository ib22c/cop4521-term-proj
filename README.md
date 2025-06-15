# Bookstore Platform

A comprehensive web-based bookstore platform built with Flask and PostgreSQL, featuring role-based access control, parallel processing capabilities, and advanced inventory management.

## Features

- **User Roles & Authentication**

  - Customer: Browse products, manage cart, place orders
  - Vendor: List products, manage inventory, track sales
  - Employee: Process orders, update inventory, customer service
  - Admin: Full system access and configuration

- **Core Functionality**
  - Product catalog with search and filtering
  - Shopping cart and secure checkout
  - Order tracking and management
  - Real-time inventory management
  - Parallel processing for inventory updates
  - Recommendation engine
  - Comprehensive audit logging

## Tech Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login, Flask-Security
- **Task Queue**: Celery (for parallel processing)
- **Search**: Elasticsearch
- **Testing**: pytest

## Project Structure

```
bookstore/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── static/
│   └── templates/
├── config/
│   ├── __init__.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── migrations/
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── run.py
```

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Initialize the database:
   ```bash
   flask db upgrade
   ```
6. Run the development server:
   ```bash
   flask run
   ```

## License

MIT License
