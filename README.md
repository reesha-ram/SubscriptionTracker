# Subscription & Expense Tracker

A full-stack Web Application built with **FastAPI**, **SQLAlchemy**, **Alembic**, **MySQL**, **JWT Authentication**, and **Jinja2 Templates**. 

This application helps users manage recurring subscriptions, monitor monthly/annual spend (burn rate), track upcoming renewal dates, and organize expenses by category.

---

## Architecture Overview

```
                          +-----------------------------------+
                          |            CLIENT                 |
                          | (Browser: Jinja2 Templates, HTML,  |
                          |    Bootstrap/Tailwind, Vanilla JS) |
                          +-----------------+-----------------+
                                            |
                                            | HTTP / HTTPS (JWT Cookie / Header)
                                            v
                          +-----------------+-----------------+
                          |        FASTAPI BACKEND            |
                          |  - Routers (Auth, Subs, Dashboard)|
                          |  - Middleware (Cookie Parser)     |
                          |  - Pydantic Validation & Schemas  |
                          |  - SQLAlchemy ORM                 |
                          +--------+----------------+---------+
                                   |                |
                SQL via SQLAlchemy |                | Migration Scripts
                                   v                v
                          +--------+----+      +----+--------+
                          |   MYSQL     |      |  ALEMBIC    |
                          | DATABASE    |      | MIGRATIONS  |
                          +-------------+      +-------------+
```

---

## Project Structure

```text
SubscriptionTracker/
├── alembic/                      # Database migration scripts
├── static/                       # CSS and Vanilla JavaScript
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── auth.js               # Login & Register handling
│       └── subscriptions.js      # CRUD DOM operations
├── templates/                    # Jinja2 HTML Templates
│   ├── base.html                 # Main layout wrapper
│   ├── navbar.html               # Header navigation component
│   ├── login.html                # User login page
│   ├── register.html             # User registration page
│   ├── dashboard.html            # Analytics dashboard
│   ├── subscriptions.html        # Subscription list & filters
│   ├── add_subscription.html     # Create subscription form
│   └── edit_subscription.html    # Update subscription form
├── app/                          # Main Application Package
│   ├── __init__.py
│   ├── config.py                 # Configuration & Environment settings
│   ├── database.py               # DB Engine & Session creation
│   ├── models.py                 # SQLAlchemy ORM Models
│   ├── schemas.py                # Pydantic Schemas
│   ├── utils.py                  # JWT & Hashing helpers
│   └── routers/                  # Application Routes
│       ├── __init__.py
│       ├── auth.py               # Authentication endpoints
│       ├── subscriptions.py      # Subscription CRUD
│       └── dashboard.py          # Analytics calculations
├── .env.example                  # Environment Variables Template
├── .gitignore                    # Git Ignore rules
├── alembic.ini                   # Alembic configuration
├── main.py                       # Application Entrypoint
├── render.yaml                   # Render deployment configuration
└── requirements.txt              # Dependency file
```

---

## Database Schema Design

```text
        +-------------------+            +------------------------+
        |       USERS       |            |     SUBSCRIPTIONS      |
        +-------------------+            +------------------------+
        | id (PK, Int)      |<----------1| id (PK, Int)           |
        | email (UQ, Str)   |            | user_id (FK, Int)      |
        | username (UQ, Str)|            | service_name (Str(100))|
        | hashed_pass (Str) |            | price (Numeric)        |
        | currency (Str(3)) |            | billing_cycle (Enum)   |
        | is_active (Bool)  |            | next_billing_date (Date|
        | created_at (DT)   |            | category (Enum/Str)    |
        +-------------------+            | status (Enum/Str)      |
                                         | auto_renew (Bool)      |
                                         | created_at (DT)        |
                                         +------------------------+
```

---

## Financial Analytics & Logic

- **Monthly Burn Rate:**
  $$\text{Monthly Burn} = \sum (\text{Active Monthly Subs}) + \sum \left(\frac{\text{Active Yearly Subs}}{12}\right)$$

- **Annual Spend:**
  $$\text{Annual Spend} = \text{Monthly Burn} \times 12$$

- **Renewal Urgency:**
  - `Red`: $\le 3$ days remaining
  - `Yellow`: $3 < \text{Days} \le 7$
  - `Green`: $> 7$ days remaining

---

## Tech Stack

- **Backend:** Python 3.13+, FastAPI, Pydantic v2, PyJWT / Python-Jose, Passlib (bcrypt)
- **Database & ORM:** MySQL, SQLAlchemy 2.0, Alembic
- **Frontend:** Jinja2, HTML5, Bootstrap 5 / Tailwind CSS, Vanilla JS
- **Deployment:** Render