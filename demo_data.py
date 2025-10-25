#!/usr/bin/env python3
"""
Demo script to create multiple clients and invoices for presentation
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8002"

def create_demo_data():
    """Create comprehensive demo data"""
    print("Creating demo data for client presentation...")
    
    # Create multiple clients
    clients_data = [
        {
            "name": "TechCorp Solutions",
            "email": "billing@techcorp.com",
            "phone": "+1-555-0101",
            "address": "456 Tech Avenue, Silicon Valley, CA 94000"
        },
        {
            "name": "Global Marketing Inc",
            "email": "accounts@globalmarketing.com", 
            "phone": "+1-555-0202",
            "address": "789 Marketing Blvd, New York, NY 10002"
        },
        {
            "name": "StartupXYZ",
            "email": "finance@startupxyz.com",
            "phone": "+1-555-0303", 
            "address": "321 Innovation Street, Austin, TX 73301"
        }
    ]
    
    created_clients = []
    for client_data in clients_data:
        response = requests.post(f"{BASE_URL}/api/clients/", json=client_data)
        if response.status_code == 200:
            client = response.json()
            created_clients.append(client)
            print(f"[SUCCESS] Created client: {client['name']} (ID: {client['id']})")
        else:
            print(f"[ERROR] Failed to create client {client_data['name']}: {response.text}")
    
    # Create invoices for each client
    invoice_templates = [
        {"description": "Website Development & Design", "amount": 2500.00, "days_due": 30},
        {"description": "Mobile App Development", "amount": 4500.00, "days_due": 45},
        {"description": "SEO & Digital Marketing Services", "amount": 1200.00, "days_due": 15},
        {"description": "Database Migration & Optimization", "amount": 3200.00, "days_due": 60},
        {"description": "Cloud Infrastructure Setup", "amount": 1800.00, "days_due": 20}
    ]
    
    created_invoices = []
    for i, client in enumerate(created_clients):
        # Create 1-2 invoices per client
        num_invoices = min(2, len(invoice_templates) - i)
        for j in range(num_invoices):
            template = invoice_templates[i + j]
            due_date = (datetime.now() + timedelta(days=template["days_due"])).isoformat()
            
            invoice_data = {
                "client_id": client["id"],
                "amount": template["amount"],
                "due_date": due_date,
                "description": template["description"]
            }
            
            response = requests.post(f"{BASE_URL}/api/invoices/", json=invoice_data)
            if response.status_code == 200:
                invoice = response.json()
                created_invoices.append(invoice)
                print(f"[SUCCESS] Created invoice #{invoice['id']} for {client['name']} - ${invoice['amount']}")
            else:
                print(f"[ERROR] Failed to create invoice: {response.text}")
    
    # Test payment creation for one invoice
    if created_invoices:
        test_invoice = created_invoices[0]
        payment_data = {
            "invoice_id": test_invoice["id"],
            "amount": test_invoice["amount"],
            "method": "stripe",
            "transaction_id": "demo_txn_12345"
        }
        
        response = requests.post(f"{BASE_URL}/api/payments/", json=payment_data)
        if response.status_code == 200:
            payment = response.json()
            print(f"[SUCCESS] Created payment for invoice #{test_invoice['id']} - ${payment['amount']}")
        else:
            print(f"[INFO] Payment creation test: {response.text}")
    
    print(f"\nDemo Data Summary:")
    print(f"  Clients created: {len(created_clients)}")
    print(f"  Invoices created: {len(created_invoices)}")
    print(f"  Total invoice value: ${sum(inv['amount'] for inv in created_invoices):,.2f}")
    print(f"\nAPI Documentation: {BASE_URL}/docs")
    print(f"Access the system at: {BASE_URL}")

if __name__ == "__main__":
    create_demo_data()