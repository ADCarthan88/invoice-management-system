# Configuration settings
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./invoice_system.db")

# Email settings
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "your-email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-password")

# Payment settings
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "your-stripe-secret-key")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "your-paypal-client-id")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "your-paypal-client-secret")