# Environment Configuration Guide

This project is a Django-based E-commerce Ordering and Payment System. Follow this guide to set up your development environment.

## 1. Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose** (for the database)
- **Git**

## 2. Project Structure

```
ecommerce-ordering-and-payment-system/
├── app/                  # Django project root
│   ├── app/              # Project settings & wsgi
│   ├── core/             # Core functionality
│   ├── users/            # User management
│   ├── products/         # Product catalog
│   ├── orders/           # Order processing
│   └── payments/         # Payment integration (Stripe)
├── venv/                 # Virtual environment (recommended)
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Database configuration
└── ENVIRONMENT_SETUP.md  # This guide
```

## 3. Virtual Environment Setup

It is best practice to work in a virtual environment.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## 4. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## 5. Database Setup

This project uses **PostgreSQL**. The easiest way to run it is via Docker.

### Start the Database
Run the following command in the project root (where `docker-compose.yml` is located):

```bash
docker-compose up -d
```

This will start a PostgreSQL 15 container exposing port `5432`.
- **Database Name:** `ecommerce_db`
- **User:** `postgres`
- **Password:** `postgres`

## 6. Environment Variables

The application uses environment variables for configuration. You can set these in your shell or create a script to load them.

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `DEBUG` | `False` | Enable debug mode (set to `True` for development) |
| `DB_NAME` | `ecommerce_db` | Postgres Database Name |
| `DB_USER` | `postgres` | Postgres User |
| `DB_PASSWORD` | `postgres` | Postgres Password |
| `DB_HOST` | `localhost` | Postgres Host |
| `DB_PORT` | `5432` | Postgres Port |
| `STRIPE_SECRET_KEY` | `sk_test_placeholder` | Stripe Secret Key (Required for payments) |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Stripe Webhook Secret (Required for webhooks) |

### Example: Running with Environment Variables

```bash
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export DEBUG=True
```

## 7. Running the Application

### A. Apply Migrations
Before running the server, ensure the database schema is up to date:

```bash
cd app
python manage.py migrate
```

### B. Seed the Database (Optional)
To populate the database with initial products:

```bash
python manage.py seed_db
```

### C. Create Superuser (Admin)
To access the Django Admin panel:

```bash
python manage.py createsuperuser
```

### D. Start the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`.

## 8. Documentation

Once the server is running, you can access the API documentation:

- **Swagger UI:** [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **Redoc:** [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)

## 9. Testing Stripe Webhooks (Local Development)

To test Stripe webhooks locally, you can use the Stripe CLI or the provided simulation script.

### Option A: Using Simulation Script (No Stripe CLI required)
This script simulates a payload sent to your webhook endpoint.

```bash
cd app
python simulate_webhook.py
```

### Option B: Using Stripe CLI
1. Forward events to your local server:
   ```bash
   stripe listen --forward-to localhost:8000/payments/webhook/
   ```
2. Trigger an event:
   ```bash
   stripe trigger payment_intent.succeeded
   ```
