#!/usr/bin/env python3
"""
Test script to populate the database with sample data and test the API
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8002"

def create_test_client():
    """Create a test client"""
    client_data = {
        "name": "Acme Corporation",
        "email": "billing@acme.com",
        "phone": "+1-555-0123",
        "address": "123 Business St, Suite 100, New York, NY 10001"
    }
    
    response = requests.post(f"{BASE_URL}/api/clients/", json=client_data)
    if response.status_code == 200:
        print("[SUCCESS] Client created successfully")
        return response.json()
    else:
        print(f"[ERROR] Failed to create client: {response.text}")
        return None

def create_test_invoice(client_id):
    """Create a test invoice"""
    due_date = (datetime.now() + timedelta(days=30)).isoformat()
    
    invoice_data = {
        "client_id": client_id,
        "amount": 1500.00,
        "due_date": due_date,
        "description": "Web Development Services - Q1 2024"
    }
    
    response = requests.post(f"{BASE_URL}/api/invoices/", json=invoice_data)
    if response.status_code == 200:
        print("[SUCCESS] Invoice created successfully")
        return response.json()
    else:
        print(f"[ERROR] Failed to create invoice: {response.text}")
        return None

def test_api_endpoints():
    """Test various API endpoints"""
    print("Testing API endpoints...")
    
    # Test root endpoint
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("[SUCCESS] Root endpoint working")
        print(f"   Response: {response.json()}")
    else:
        print("[ERROR] Root endpoint failed")
    
    # Create test client
    client = create_test_client()
    if not client:
        return
    
    # Create test invoice
    invoice = create_test_invoice(client["id"])
    if not invoice:
        return
    
    # Test PDF generation
    try:
        response = requests.get(f"{BASE_URL}/invoices/{invoice['id']}/pdf")
        if response.status_code == 200:
            print("[SUCCESS] PDF generation working")
            # Save PDF for demonstration
            with open("test_invoice.pdf", "wb") as f:
                f.write(response.content)
            print("   [INFO] PDF saved as 'test_invoice.pdf'")
        else:
            print(f"[ERROR] PDF generation failed: {response.text}")
    except Exception as e:
        print(f"[ERROR] PDF generation error: {e}")
    
    print(f"\nTest Results Summary:")
    print(f"   Client ID: {client['id']}")
    print(f"   Invoice ID: {invoice['id']}")
    print(f"   Invoice Amount: ${invoice['amount']}")

if __name__ == "__main__":
    print("Starting API tests...")
    test_api_endpoints()
    print("Tests completed!")