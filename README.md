# RM → FG Material Tracker 🏭

A full-stack **Raw Material to Finished Goods** tracking system with a **simulated blockchain** for immutable event logging and real-time traceability.

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Database | PostgreSQL (Supabase) |
| Blockchain | Custom SHA-256 chain (Python) |
| Frontend | Streamlit |
| ORM | SQLAlchemy |

## 📦 Features

- **GRN (Goods Receipt Note)** — Record raw material arrivals
- **Issue Material** — Move material from warehouse to production
- **Create Finished Good** — Log production completion
- **Dispatch** — Record outbound shipments
- **Blockchain Ledger** — Every event is cryptographically chained
- **Material Tracing** — Full journey timeline for any material
- **Chain Validation** — Detect any data tampering instantly

## 🚀 Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/rm-fg-tracker.git
cd rm-fg-tracker

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your database URL
echo DATABASE_URL=your_postgresql_url > .env

# 5. Initialize database tables and genesis block
python init_db.py

# 6. Start the backend API
uvicorn main:app --reload --port 8000

# 7. In a new terminal, start the dashboard
streamlit run dashboard/streamlit_app.py
```

## 🌐 Live Deployment

- **Dashboard:** Deployed on Streamlit Community Cloud
- **Backend API:** Deployed on Render

## 📁 Project Structure

```
rm_fg_tracker/
├── api/                    # FastAPI route handlers
├── blockchain/             # Block creation & chain validation
├── dashboard/              # Streamlit frontend
├── database/               # SQLAlchemy DB session
├── models/                 # ORM models & Pydantic schemas
├── services/               # Business logic layer
├── main.py                 # FastAPI app entry point
├── config.py               # Environment config
├── init_db.py              # DB initialization script
└── requirements.txt        # Python dependencies
```

## 👤 Author

Rohit Anandan
