# Online Marketplace

A full-stack online marketplace built with Python and Flask — designed as a university database project, but engineered with real-world architecture in mind.

Two distinct user roles (**buyer** and **seller**) interact through a shared platform with product discovery, cart & checkout, direct messaging, and a subscription-based notification system — all backed by a normalized relational database.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MariaDB / MySQL |
| Frontend | HTML, CSS, JavaScript |
| Auth | Session-based, password hashing via werkzeug |

## Features

**For Buyers**
- Browse, search, and filter products by category
- Shopping cart with database persistence
- Wishlist
- Checkout & order management
- Subscribe to sellers and receive notifications for new products
- Buyer statistics dashboard

**For Sellers**
- Seller shop with full product management (create, update, image upload)
- Product statistics with charts
- Order overview

**Platform**
- Direct messaging between users
- Role-based access control
- Hierarchical product category system

## Architecture

The app follows a clean separation of concerns using Flask's **Blueprint** pattern — each domain (auth, products, cart, orders, wishlist, messaging, users) is an isolated module. All database interactions go through a central `data_access.py` layer; no inline SQL in route handlers.

```
app/
├── __init__.py        # App factory (create_app)
├── config.py          # DevelopmentConfig / ProductionConfig
├── db.py              # DB connection via Flask
├── data_access.py     # All DB query functions
├── utils.py           # login_required decorator
├── blueprints/        # auth, products, cart, orders, wishlist, messaging, users
├── templates/         # Jinja2 templates per blueprint
└── static/            # CSS, JS, images
```

## Setup

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Fill in DB host, user, password, name
   ```

4. **Set up the database:**
   ```bash
   mysql -u <user> -p marketplace < sqlFiles/create_database.sql
   mysql -u <user> -p marketplace < sqlFiles/fill_database.sql
   ```

5. **Run:**
   ```bash
   python run.py
   ```
   App runs at `http://localhost:5000`.
