# dashboard/streamlit_app.py
"""
RM → FG Tracker Dashboard
Run with: streamlit run dashboard/streamlit_app.py
Make sure FastAPI backend is running on port 8000 first.
"""
import streamlit as st
import requests
import pandas as pd
import time
import json

import os

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
try:
    API_BASE = st.secrets.get("API_BASE", API_BASE)
except Exception:
    pass


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def api_post(endpoint: str, data: dict):
    """POST to FastAPI. Returns (success, response_dict)."""
    try:
        response = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=10)
        return response.ok, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"detail": "Cannot connect to backend. Is FastAPI running on port 8000?"}
    except Exception as e:
        return False, {"detail": str(e)}


def api_get(endpoint: str):
    """GET from FastAPI. Returns list or dict, or None on error."""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        if response.ok:
            return response.json()
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def format_event_type(event_type: str) -> str:
    icons = {
        "GENESIS":          "⚪ GENESIS",
        "GRN_RECEIVED":     "📥 GRN RECEIVED",
        "MATERIAL_ISSUED":  "➡️ MATERIAL ISSUED",
        "FG_CREATED":       "🏭 FG CREATED",
        "DISPATCHED":       "🚚 DISPATCHED",
    }
    return icons.get(event_type, f"📌 {event_type}")


def status_color(status: str) -> str:
    colors = {
        "AVAILABLE":    "🟢",
        "ISSUED":       "🔵",
        "DISPATCHED":   "🟠",
        "CONSUMED":     "🔴",
        "IN_STOCK":     "🟢",
        "OPEN":         "🟢",
        "IN_PROGRESS":  "🔵",
        "COMPLETED":    "✅",
    }
    return colors.get(status, "⚫") + " " + status


# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="RM → FG Tracker",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Industrial Factory Classic Theme */
    .stApp {
        background-color: #f8fafc;
        background-image: 
            linear-gradient(rgba(203, 213, 225, 0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(203, 213, 225, 0.5) 1px, transparent 1px),
            linear-gradient(120deg, #e0f2fe 0%, #fdf4ff 50%, #f0fdf4 100%);
        background-size: 20px 20px, 20px 20px, 100% 100%;
        background-attachment: fixed;
    }
    .main-header {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #2C3E50;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.2rem;
        border-bottom: 3px solid #D35400;
        padding-bottom: 10px;
    }
    .sub-header {
        font-family: 'Courier New', Courier, monospace;
        font-size: 1rem;
        color: #7F8C8D;
        margin-bottom: 1.5rem;
        font-weight: bold;
    }
    .block-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(189, 195, 199, 0.5);
        border-left: 5px solid #34495E;
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    /* Style metric cards */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(189, 195, 199, 0.5);
        border-top: 4px solid #2980B9;
        padding: 15px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Tabs styling */
    button[data-baseweb="tab"] {
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .success-box {
        background: #EAFAF1;
        border: 1px solid #2ECC71;
        border-left: 5px solid #27AE60;
        border-radius: 4px;
        padding: 12px;
        color: #1D8348;
        font-weight: bold;
    }
    .error-box {
        background: #FDEDEC;
        border: 1px solid #E74C3C;
        border-left: 5px solid #C0392B;
        border-radius: 4px;
        padding: 12px;
        color: #943126;
        font-weight: bold;
    }

    /* Bold Subheadings */
    h2, h3, h4 {
        font-weight: 800 !important;
        color: #1E293B !important;
    }
    h4 {
        border-bottom: 2px solid rgba(226, 232, 240, 0.8);
        padding-bottom: 8px;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 1.1rem;
    }

    /* Individual Blocks / Expanders Background */
    [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 15px !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        background-color: rgba(248, 250, 252, 0.5) !important;
        font-weight: 700 !important;
        border-bottom: 1px solid rgba(241, 245, 249, 0.5) !important;
    }
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.95rem;
    }

    /* 1. Interactive Hover Micro-Animations */
    .block-card,
    div[data-testid="metric-container"],
    [data-testid="stExpander"] {
        transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.2s ease-in-out !important;
    }

    .block-card:hover,
    div[data-testid="metric-container"]:hover,
    [data-testid="stExpander"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04) !important;
        border-color: #94A3B8 !important;
    }

    /* 3. Custom Timeline HTML styling */
    .timeline-wrapper {
        position: relative;
        padding-left: 30px;
        margin-top: 20px;
    }
    .timeline-wrapper::before {
        content: '';
        position: absolute;
        left: 9px;
        top: 0;
        bottom: 0;
        width: 4px;
        background: #CBD5E1;
        border-radius: 2px;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 25px;
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .timeline-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
        border-color: #94A3B8;
    }
    .timeline-dot {
        position: absolute;
        left: -30px;
        top: 25px;
        width: 22px;
        height: 22px;
        border: 4px solid #F8FAFC;
        border-radius: 50%;
        z-index: 2;
        box-shadow: 0 0 0 1px #CBD5E1;
    }
    .timeline-content {
        display: flex;
        flex-direction: row;
        gap: 20px;
        font-size: 0.95rem;
    }
    .tl-col {
        flex: 1;
    }
    .timeline-header {
        margin-top: 0;
        margin-bottom: 15px;
        border-bottom: 2px solid rgba(226, 232, 240, 0.8);
        padding-bottom: 8px;
        font-weight: 800;
        color: #1E293B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 1.1rem;
    }
    .timeline-item p { margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════

st.markdown('<div class="main-header">🏭 RM → FG Material Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Simulated Blockchain | Immutable Event Logging | Real-time Traceability</div>', unsafe_allow_html=True)

# Backend status check
backend_status = api_get("/")
if backend_status:
    st.success("✅ Backend connected | FastAPI running on port 8000")
else:
    st.error("❌ Cannot reach backend. Run: `uvicorn main:app --reload --port 8000`")
    st.stop()

st.divider()


# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════

tab_events, tab_inventory, tab_blockchain, tab_trace, tab_validate = st.tabs([
    "⚡ Submit Events",
    "📦 Inventory",
    "⛓ Blockchain Log",
    "🔎 Trace Material",
    "🔐 Validate Chain"
])


# ───────────────────────────────────────────────────────────────
# TAB 1: SUBMIT EVENTS
# ───────────────────────────────────────────────────────────────
with tab_events:
    st.subheader("Submit Material Events")
    st.caption("Each submission writes to PostgreSQL and creates a new blockchain block.")

    event_type = st.selectbox(
        "Select Event Type",
        ["📥 GRN — Receive Raw Material",
         "➡️ Issue Material to Production",
         "🏭 Create Finished Good",
         "🚚 Dispatch Finished Good"],
        key="event_type_selector"
    )

    st.divider()

    # ── GRN FORM ──────────────────────────────────────────────
    if "GRN" in event_type:
        st.markdown("#### 📥 Goods Receipt Note (GRN)")
        st.caption("Record arrival of raw material from supplier")

        col_a, col_b = st.columns(2)
        with col_a:
            grn_mat_id      = st.text_input("Material ID *", value="RM001", key="grn_mat_id")
            grn_mat_name    = st.text_input("Material Name *", value="Chemical X", key="grn_mat_name")
            grn_batch_id    = st.text_input("Batch ID *", value="BATCH101", key="grn_batch")
            grn_qty         = st.number_input("Quantity *", min_value=0.1, value=50.0, step=0.1, key="grn_qty")
            grn_unit        = st.selectbox("Unit", ["kg", "litres", "units", "pcs", "g", "ml"], key="grn_unit")

        with col_b:
            grn_supplier_id     = st.text_input("Supplier ID *", value="SUP-ABC", key="grn_sup_id")
            grn_supplier_name   = st.text_input("Supplier Name *", value="ABC Corporation", key="grn_sup_name")
            grn_location        = st.text_input("Storage Location *", value="Rack A-1", key="grn_loc")
            grn_worker          = st.text_input("Worker ID *", value="W007", key="grn_worker")
            grn_quality         = st.selectbox("Quality Status", ["PASSED", "FAILED", "PENDING"], key="grn_quality")

        if st.button("✅ Submit GRN", type="primary", key="btn_grn"):
            if not all([grn_mat_id, grn_mat_name, grn_batch_id, grn_supplier_id]):
                st.warning("Please fill all required (*) fields")
            else:
                with st.spinner("Processing GRN and creating blockchain block..."):
                    ok, result = api_post("/api/create-grn", {
                        "material_id":      grn_mat_id,
                        "material_name":    grn_mat_name,
                        "batch_id":         grn_batch_id,
                        "quantity":         grn_qty,
                        "unit":             grn_unit,
                        "supplier_id":      grn_supplier_id,
                        "supplier_name":    grn_supplier_name,
                        "worker_id":        grn_worker,
                        "location":         grn_location,
                        "quality_status":   grn_quality
                    })

                if ok:
                    st.success(f"✅ {result['message']}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Event ID", result["event_id"])
                    col2.metric("Block #", result["blockchain"]["block_index"])
                    col3.metric("Status", result["blockchain"]["status"])
                    st.code(f"Block Hash: {result['blockchain']['block_hash']}", language=None)
                else:
                    st.error(f"❌ {result.get('detail', 'Unknown error')}")

    # ── ISSUE MATERIAL FORM ───────────────────────────────────
    elif "Issue" in event_type:
        st.markdown("#### ➡️ Issue Material to Production")
        st.caption("Move raw material from warehouse to production floor")

        # Load available materials for dropdown
        materials_data = api_get("/api/materials") or []
        rm_materials = [m for m in materials_data if m["material_type"] == "RM" and m["status"] == "AVAILABLE"]
        orders_data = api_get("/api/production-orders") or []
        open_orders = [o for o in orders_data if o["status"] in ("OPEN", "IN_PROGRESS")]

        col_a, col_b = st.columns(2)
        with col_a:
            if rm_materials:
                mat_options = [f"{m['material_id']} — {m['material_name']} ({m['current_qty']} {m['unit']})" for m in rm_materials]
                selected_mat = st.selectbox("Select Material *", mat_options, key="issue_mat_select")
                iss_mat_id = selected_mat.split(" — ")[0]
                iss_mat = next(m for m in rm_materials if m["material_id"] == iss_mat_id)
            else:
                iss_mat_id = st.text_input("Material ID *", value="RM001", key="issue_mat_id")
                iss_mat = None

            iss_batch = st.text_input("Batch ID *", value="BATCH101", key="issue_batch")
            iss_qty = st.number_input(
                "Quantity *",
                min_value=0.1,
                max_value=float(iss_mat["current_qty"]) if iss_mat else 9999.0,
                value=min(50.0, float(iss_mat["current_qty"])) if iss_mat else 50.0,
                step=0.1,
                key="issue_qty"
            )

        with col_b:
            if open_orders:
                order_options = [f"{o['order_id']} — {o['product_name']}" for o in open_orders]
                selected_order = st.selectbox("Production Order *", order_options, key="issue_order_select")
                iss_order = selected_order.split(" — ")[0]
            else:
                iss_order = st.text_input("Production Order ID *", value="PO-2026-01", key="issue_order")
            iss_worker = st.text_input("Worker ID *", value="W012", key="issue_worker")

        if st.button("✅ Issue Material", type="primary", key="btn_issue"):
            with st.spinner("Processing issue event..."):
                ok, result = api_post("/api/issue-material", {
                    "material_id":          iss_mat_id,
                    "batch_id":             iss_batch,
                    "quantity":             iss_qty,
                    "production_order_id":  iss_order,
                    "worker_id":            iss_worker
                })
            if ok:
                st.success(f"✅ {result['message']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Event ID", result["event_id"])
                col2.metric("Block #", result["blockchain"]["block_index"])
                col3.metric("Status", result["blockchain"]["status"])
                st.code(f"Block Hash: {result['blockchain']['block_hash']}", language=None)
            else:
                st.error(f"❌ {result.get('detail', 'Unknown error')}")

    # ── CREATE FG FORM ────────────────────────────────────────
    elif "Finished Good" in event_type:
        st.markdown("#### 🏭 Create Finished Good")
        st.caption("Record completion of production — raw material becomes finished product")

        orders_data = api_get("/api/production-orders") or []
        active_orders = [o for o in orders_data if o["status"] in ("OPEN", "IN_PROGRESS")]

        col_a, col_b = st.columns(2)
        with col_a:
            fg_id       = st.text_input("FG ID *", value="FG-789", key="fg_id")
            fg_name     = st.text_input("FG Name *", value="Product Alpha", key="fg_name")
            fg_qty      = st.number_input("Quantity Produced *", min_value=0.1, value=200.0, step=0.1, key="fg_qty")
            fg_unit     = st.selectbox("Unit", ["units", "pcs", "kg", "litres"], key="fg_unit")

        with col_b:
            if active_orders:
                order_options = [f"{o['order_id']} — {o['product_name']}" for o in active_orders]
                selected_order = st.selectbox("Production Order *", order_options, key="fg_order_select")
                fg_order = selected_order.split(" — ")[0]
            else:
                fg_order = st.text_input("Production Order ID *", value="PO-2026-01", key="fg_order")
            fg_worker   = st.text_input("Worker ID *", value="W015", key="fg_worker")
            fg_batches  = st.text_input("RM Batches Used (comma separated)", value="BATCH101", key="fg_batches")

        if st.button("✅ Create Finished Good", type="primary", key="btn_fg"):
            batches_list = [b.strip() for b in fg_batches.split(",") if b.strip()]
            with st.spinner("Creating FG record and logging to blockchain..."):
                ok, result = api_post("/api/create-fg", {
                    "fg_id":                fg_id,
                    "fg_name":              fg_name,
                    "production_order_id":  fg_order,
                    "quantity":             fg_qty,
                    "unit":                 fg_unit,
                    "worker_id":            fg_worker,
                    "rm_batches_used":      batches_list
                })
            if ok:
                st.success(f"✅ {result['message']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("FG ID", result["fg_id"])
                col2.metric("Block #", result["blockchain"]["block_index"])
                col3.metric("Status", result["blockchain"]["status"])
                st.code(f"Block Hash: {result['blockchain']['block_hash']}", language=None)
            else:
                st.error(f"❌ {result.get('detail', 'Unknown error')}")

    # ── DISPATCH FORM ─────────────────────────────────────────
    elif "Dispatch" in event_type:
        st.markdown("#### 🚚 Dispatch Finished Good")
        st.caption("Record outward movement of finished goods to customer")

        materials_data = api_get("/api/materials") or []
        fg_available = [m for m in materials_data if m["material_type"] == "FG" and m["status"] == "AVAILABLE"]

        col_a, col_b = st.columns(2)
        with col_a:
            if fg_available:
                fg_options = [f"{m['material_id']} — {m['material_name']} ({m['current_qty']} {m['unit']})" for m in fg_available]
                selected_fg = st.selectbox("Select Finished Good *", fg_options, key="disp_fg_select")
                disp_fg_id = selected_fg.split(" — ")[0]
                disp_fg = next(m for m in fg_available if m["material_id"] == disp_fg_id)
            else:
                disp_fg_id = st.text_input("FG ID *", value="FG-789", key="disp_fg_id")
                disp_fg = None
            disp_qty = st.number_input(
                "Quantity *",
                min_value=0.1,
                max_value=float(disp_fg["current_qty"]) if disp_fg else 9999.0,
                value=min(200.0, float(disp_fg["current_qty"])) if disp_fg else 200.0,
                step=0.1,
                key="disp_qty"
            )

        with col_b:
            disp_cust_id    = st.text_input("Customer ID *", value="CUST-XYZ", key="disp_cust_id")
            disp_cust_name  = st.text_input("Customer Name *", value="XYZ Industries", key="disp_cust_name")
            disp_vehicle    = st.text_input("Vehicle Number *", value="TN-01-AB-1234", key="disp_vehicle")
            disp_worker     = st.text_input("Worker ID *", value="W020", key="disp_worker")

        if st.button("✅ Dispatch", type="primary", key="btn_dispatch"):
            with st.spinner("Recording dispatch and logging to blockchain..."):
                ok, result = api_post("/api/dispatch", {
                    "fg_id":            disp_fg_id,
                    "customer_id":      disp_cust_id,
                    "customer_name":    disp_cust_name,
                    "quantity":         disp_qty,
                    "vehicle_number":   disp_vehicle,
                    "worker_id":        disp_worker
                })
            if ok:
                st.success(f"✅ {result['message']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Dispatch ID", result["dispatch_id"])
                col2.metric("Block #", result["blockchain"]["block_index"])
                col3.metric("Status", result["blockchain"]["status"])
                st.code(f"Block Hash: {result['blockchain']['block_hash']}", language=None)
            else:
                st.error(f"❌ {result.get('detail', 'Unknown error')}")


# ───────────────────────────────────────────────────────────────
# TAB 2: INVENTORY
# ───────────────────────────────────────────────────────────────
with tab_inventory:
    st.subheader("📦 Current Inventory")

    if st.button("🔄 Refresh", key="refresh_inventory"):
        st.rerun()

    materials_data = api_get("/api/materials")

    if materials_data:
        df = pd.DataFrame(materials_data)

        # Summary metrics
        rm_count = len([m for m in materials_data if m["material_type"] == "RM"])
        fg_count = len([m for m in materials_data if m["material_type"] == "FG"])
        available_count = len([m for m in materials_data if m["status"] == "AVAILABLE"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Materials", len(materials_data))
        col2.metric("Raw Materials", rm_count)
        col3.metric("Finished Goods", fg_count)
        col4.metric("Available", available_count)

        st.divider()

        # Filter
        filter_type = st.radio("Filter by type", ["All", "RM only", "FG only"], horizontal=True, key="inv_filter")
        if filter_type == "RM only":
            df = df[df["material_type"] == "RM"]
        elif filter_type == "FG only":
            df = df[df["material_type"] == "FG"]

        # Format status with emoji
        df["status_display"] = df["status"].apply(status_color)

        display_df = df[["material_id", "material_name", "material_type", "current_qty", "unit", "status_display", "location"]].rename(columns={
            "material_id": "ID",
            "material_name": "Name",
            "material_type": "Type",
            "current_qty": "Qty",
            "unit": "Unit",
            "status_display": "Status",
            "location": "Location"
        })

        def highlight_status(val):
            val_str = str(val).upper()
            if "AVAILABLE" in val_str or "IN_STOCK" in val_str or "OPEN" in val_str:
                return 'background-color: #D1FAE5; color: #065F46; font-weight: bold;'
            elif "ISSUED" in val_str or "IN_PROGRESS" in val_str:
                return 'background-color: #E0E7FF; color: #3730A3; font-weight: bold;'
            elif "DISPATCHED" in val_str:
                return 'background-color: #FFEDD5; color: #9A3412; font-weight: bold;'
            elif "CONSUMED" in val_str:
                return 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;'
            elif "COMPLETED" in val_str:
                return 'background-color: #DCFCE7; color: #166534; font-weight: bold;'
            return ''

        try:
            styled_df = display_df.style.map(highlight_status, subset=['Status'])
        except AttributeError:
            styled_df = display_df.style.applymap(highlight_status, subset=['Status'])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    else:
        st.info("No materials found. Submit a GRN first.")

    st.divider()
    st.subheader("📋 Recent Events")

    events_data = api_get("/api/scan-events?limit=10")
    if events_data:
        df_events = pd.DataFrame(events_data)
        df_events["timestamp"] = pd.to_datetime(df_events["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        df_events["event_type"] = df_events["event_type"].apply(format_event_type)

        st.dataframe(
            df_events[[
                "event_id", "event_type", "material_id", "quantity",
                "production_order_id", "worker_id", "timestamp", "blockchain_block_index"
            ]].rename(columns={
                "event_id": "Event ID",
                "event_type": "Type",
                "material_id": "Material",
                "quantity": "Qty",
                "production_order_id": "Prod. Order",
                "worker_id": "Worker",
                "timestamp": "Timestamp",
                "blockchain_block_index": "Block #"
            }),
            use_container_width=True,
            hide_index=True
        )


# ───────────────────────────────────────────────────────────────
# TAB 3: BLOCKCHAIN LOG
# ───────────────────────────────────────────────────────────────
with tab_blockchain:
    st.subheader("⛓ Blockchain Log")
    st.caption("Immutable event history — each block is cryptographically linked to the previous one.")

    if st.button("🔄 Refresh", key="refresh_blockchain"):
        st.rerun()

    limit = st.slider("Show last N blocks", min_value=5, max_value=50, value=10, key="bc_limit")
    blocks = api_get(f"/api/blockchain-log?limit={limit}")

    if blocks:
        st.metric("Total Blocks Shown", len(blocks))
        st.divider()

        for block in reversed(blocks):  # Show newest first
            event_icon = {
                "GENESIS":          "⚪",
                "GRN_RECEIVED":     "📥",
                "MATERIAL_ISSUED":  "➡️",
                "FG_CREATED":       "🏭",
                "DISPATCHED":       "🚚"
            }.get(block["event_type"], "📌")

            is_genesis = block["event_type"] == "GENESIS"

            with st.expander(
                f"{event_icon} Block #{block['block_index']} — {block['event_type']} "
                f"| {block.get('created_at', '')[:19]}",
                expanded=(not is_genesis)
            ):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"**Block Index:** `{block['block_index']}`")
                    st.markdown(f"**Event Type:** `{block['event_type']}`")
                    st.markdown(f"**Timestamp:** `{block.get('created_at', 'N/A')[:19]}`")

                with col2:
                    st.markdown(f"**Current Hash:**")
                    st.code(block["block_hash"], language=None)
                    st.markdown(f"**Previous Hash:**")
                    st.code(block["previous_hash"], language=None)

                st.markdown("**Block Data:**")
                st.json(block["data_json"])
    else:
        st.info("No blocks found. Run init_db.py to create the genesis block.")


# ───────────────────────────────────────────────────────────────
# TAB 4: TRACE MATERIAL
# ───────────────────────────────────────────────────────────────
with tab_trace:
    st.subheader("🔎 Trace Material Journey")
    st.caption("Enter any Material ID or FG ID to see its complete event history with blockchain proof.")

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        trace_id = st.text_input(
            "Enter Material ID or FG ID",
            value="RM001",
            placeholder="e.g. RM001, FG-789",
            key="trace_input"
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        trace_clicked = st.button("🔍 Trace Now", type="primary", key="btn_trace")

    if trace_clicked and trace_id:
        with st.spinner(f"Tracing {trace_id}..."):
            result = api_get(f"/api/trace/{trace_id}")

        if result and "events" in result:
            # Material summary
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Material ID", result["material_id"])
            col2.metric("Name", result["material_name"])
            col3.metric("Type", result["material_type"])
            col4.metric("Status", result["current_status"])

            st.markdown(f"**Total Events Found:** {result['total_events']}")
            st.divider()

            # Timeline
            st.markdown("#### 📅 Event Timeline")

            html_timeline = '<div class="timeline-wrapper">\n'
            for i, event in enumerate(result["events"]):
                event_icon = {
                    "GRN_RECEIVED":     "📥",
                    "MATERIAL_ISSUED":  "➡️",
                    "FG_CREATED":       "🏭",
                    "DISPATCHED":       "🚚"
                }.get(event["event_type"], "📌")

                bc = event["blockchain"]
                bc_status = "✅ Verified" if bc.get("status") == "VERIFIED" else "⚠️ Not logged"
                
                col_a_html = f"<p><strong>Event ID:</strong> <code>{event['event_id']}</code></p>"
                col_a_html += f"<p><strong>Type:</strong> <code>{event['event_type']}</code></p>"
                if event.get("quantity"): col_a_html += f"<p><strong>Quantity:</strong> <code>{event['quantity']}</code></p>"
                if event.get("from_location"): col_a_html += f"<p><strong>From:</strong> <code>{event['from_location']}</code></p>"
                if event.get("to_location"): col_a_html += f"<p><strong>To:</strong> <code>{event['to_location']}</code></p>"
                if event.get("production_order_id"): col_a_html += f"<p><strong>Prod. Order:</strong> <code>{event['production_order_id']}</code></p>"
                col_a_html += f"<p><strong>Worker:</strong> <code>{event.get('worker_id', 'N/A')}</code></p>"

                col_b_html = "<p><strong>Blockchain Proof:</strong></p>"
                if bc.get("block_index"):
                    col_b_html += f'<div class="success-box" style="margin-bottom:10px;">{bc_status} | Block #{bc["block_index"]}</div>'
                    col_b_html += f'<code>Hash: {bc["block_hash"]}</code>'
                else:
                    col_b_html += '<div class="error-box">Not linked to blockchain block</div>'

                dot_color = "#3498DB"
                if event["event_type"] == "GRN_RECEIVED": dot_color = "#9B59B6"
                elif event["event_type"] == "MATERIAL_ISSUED": dot_color = "#F1C40F"
                elif event["event_type"] == "FG_CREATED": dot_color = "#2ECC71"
                elif event["event_type"] == "DISPATCHED": dot_color = "#E67E22"

                html_timeline += f"""
                <div class="timeline-item">
                    <div class="timeline-dot" style="background-color: {dot_color};"></div>
                    <div class="timeline-header">{event_icon} Step {i+1}: {event['event_type']} <span style="font-weight:normal; font-size:0.9rem; color:#7F8C8D; float:right;">{event.get('timestamp', '')[:19]}</span></div>
                    <div class="timeline-content">
                        <div class="tl-col">{col_a_html}</div>
                        <div class="tl-col">{col_b_html}</div>
                    </div>
                </div>
                """
            html_timeline += '</div>'
            st.markdown(html_timeline, unsafe_allow_html=True)
        else:
            st.error(f"No trace data found for '{trace_id}'. Check the material ID.")


# ───────────────────────────────────────────────────────────────
# TAB 5: VALIDATE CHAIN
# ───────────────────────────────────────────────────────────────
with tab_validate:
    st.subheader("🔐 Blockchain Chain Validation")
    st.caption(
        "Fetches every block, recomputes its SHA-256 hash from scratch, "
        "and verifies the previous_hash link. Detects any tampering."
    )

    st.markdown("""
    **How validation works:**
    1. Fetch all blocks in order from `blockchain_log`
    2. For each block, recompute `SHA256(index + event_type + data + prev_hash + timestamp)`
    3. Compare recomputed hash with stored hash → mismatch = data was changed
    4. Verify `previous_hash` matches actual previous block's hash → mismatch = chain broken
    """)

    if st.button("🔍 Run Chain Validation Now", type="primary", key="btn_validate"):
        with st.spinner("Validating all blocks... this may take a moment"):
            result = api_get("/api/validate-chain")

        if result:
            if result["valid"]:
                st.success(f"✅ {result['message']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Blocks", result["total_blocks"])
                col2.metric("Errors Found", result["error_count"])
                col3.metric("Chain Status", "INTACT ✅")
            else:
                st.error(f"❌ {result['message']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Blocks", result["total_blocks"])
                col2.metric("Errors Found", result["error_count"])
                col3.metric("Chain Status", "TAMPERED ⚠️")

                st.divider()
                st.markdown("#### Error Details:")
                for error in result.get("errors", []):
                    st.warning(
                        f"**Block #{error['block_index']}** — "
                        f"`{error['issue']}`: {error['detail']}"
                    )

    st.divider()
    st.markdown("""
    #### 🎯 Demo: Simulate Tampering
    To demonstrate tamper detection during a presentation:
    1. Go to Supabase Dashboard → Table Editor → `blockchain_log`
    2. Edit any block's `data_json` — change a quantity value
    3. Come back here and click "Run Chain Validation"
    4. The system will report exactly which block was tampered with

    This is how the blockchain proves integrity — not by preventing changes,
    but by making them mathematically detectable.
    """)
