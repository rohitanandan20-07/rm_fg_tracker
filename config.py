# config.py
import os
from dotenv import load_dotenv

# Load .env locally (ignored on Render where env vars are set directly)
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. "
        "Local: check your .env file. "
        "Render: set it in Environment Variables in the service dashboard."
    )
