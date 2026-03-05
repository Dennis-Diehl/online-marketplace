# Online Marketplace

A Flask-based online marketplace web application (university DB project) with a MariaDB/MySQL backend. Supports two user roles: **buyers** and **sellers**.

## Features

- Product listing, search, and detail pages
- Shopping cart and checkout
- Wishlist
- Seller shop management and product statistics
- Buyer statistics
- Direct messaging between users
- Seller subscriptions with new-product notifications
- Session-based authentication (buyer / seller roles)

## Requirements

- Python 3.10+
- MariaDB / MySQL

## Setup

1. **Clone the repo and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and fill in DB credentials
   ```

3. **Set up the database:**
   ```bash
   mysql -u <user> -p marketplace < sqlFiles/create_database.sql
   mysql -u <user> -p marketplace < sqlFiles/fill_database.sql
   ```

4. **Run the app:**
   ```bash
   python run.py
   ```
   App runs at `http://localhost:5000`.

## Project Structure

```
online-marketplace/
├── run.py                  # Entry point
├── app/
│   ├── __init__.py         # App factory (create_app)
│   ├── config.py           # DevelopmentConfig / ProductionConfig
│   ├── db.py               # DB connection (Flask g)
│   ├── utils.py            # login_required decorator
│   ├── data_access.py      # All DB query functions
│   ├── blueprints/         # auth, products, cart, orders, wishlist, messaging, users
│   ├── templates/          # Jinja2 templates (organized by blueprint)
│   └── static/             # CSS, JS, images
├── sqlFiles/
│   ├── create_database.sql
│   └── fill_database.sql
└── .env.example
```
