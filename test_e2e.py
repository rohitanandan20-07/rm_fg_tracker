import requests
import time

BASE_URL = "http://localhost:8000/api"

def test_flow():
    # 1. GRN
    print("Testing GRN...")
    res = requests.post(f"{BASE_URL}/create-grn", json={
        "material_id": "RM001",
        "material_name": "Chemical X",
        "batch_id": "BATCH101",
        "quantity": 50,
        "unit": "kg",
        "supplier_id": "SUP-ABC",
        "supplier_name": "ABC Corporation",
        "worker_id": "W007",
        "location": "Rack A-1",
        "quality_status": "PASSED"
    })
    print(res.json())

    # 2. Issue Material
    print("\nTesting Issue...")
    res = requests.post(f"{BASE_URL}/issue-material", json={
        "material_id": "RM001",
        "batch_id": "BATCH101",
        "quantity": 50,
        "production_order_id": "PO-2026-01",
        "worker_id": "W012"
    })
    print(res.json())

    # 3. Create FG
    print("\nTesting FG...")
    res = requests.post(f"{BASE_URL}/create-fg", json={
        "fg_id": "FG-789",
        "fg_name": "Product Alpha",
        "production_order_id": "PO-2026-01",
        "quantity": 200.0,
        "unit": "units",
        "worker_id": "W015",
        "rm_batches_used": ["BATCH101"]
    })
    print(res.json())

    # 4. Dispatch
    print("\nTesting Dispatch...")
    res = requests.post(f"{BASE_URL}/dispatch", json={
        "fg_id": "FG-789",
        "customer_id": "CUST-XYZ",
        "customer_name": "XYZ Industries",
        "quantity": 200,
        "vehicle_number": "TN-01-AB-1234",
        "worker_id": "W020"
    })
    print(res.json())

    # 5. Trace
    print("\nTesting Trace RM001...")
    res = requests.get(f"{BASE_URL}/trace/RM001")
    print(f"Events found: {res.json()['total_events']}")

    # 6. Validate Chain
    print("\nTesting Validation...")
    res = requests.get(f"{BASE_URL}/validate-chain")
    print(f"Valid: {res.json()['valid']}, Details: {res.json()['message']}")

if __name__ == "__main__":
    test_flow()
