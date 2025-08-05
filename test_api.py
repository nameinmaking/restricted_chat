#!/usr/bin/env python3
"""
Test script for the Ecommerce Audit Logs API.
This script tests the main API endpoints to ensure they work correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_api():
    """Test the main API endpoints"""
    
    print("Testing Ecommerce Audit Logs API...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("1. Testing server availability...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the Flask app is running.")
        return
    
    # Test 2: Create a new account
    print("\n2. Testing account creation...")
    account_data = {
        "name": "Test Ecommerce Store",
        "domain": "test-store.com",
        "owner_email": "test-owner@test-store.com",
        "owner_password": "testpassword123",
        "owner_first_name": "Test",
        "owner_last_name": "Owner"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/accounts", json=account_data)
        if response.status_code == 201:
            print("✅ Account created successfully")
            account_response = response.json()
            print(f"   Account ID: {account_response['account']['id']}")
            account_id = account_response['account']['id']
        else:
            print(f"❌ Account creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating account: {e}")
        return
    
    # Test 3: Login with the created account
    print("\n3. Testing login...")
    login_data = {
        "email": "test-owner@test-store.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login successful")
            login_response = response.json()
            print(f"   User ID: {login_response['user']['id']}")
            print(f"   Role: {login_response['user']['role']}")
            
            # Get session cookies
            session_cookies = response.cookies
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return
    
    # Test 4: Create a new user (requires authentication)
    print("\n4. Testing user creation...")
    user_data = {
        "email": "test-admin@test-store.com",
        "password": "adminpassword123",
        "first_name": "Test",
        "last_name": "Admin",
        "role": "admin"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/users", 
            json=user_data,
            cookies=session_cookies
        )
        if response.status_code == 201:
            print("✅ User created successfully")
            user_response = response.json()
            print(f"   User ID: {user_response['user']['id']}")
            print(f"   Role: {user_response['user']['role']}")
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
    
    # Test 5: Get users list
    print("\n5. Testing get users...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/users",
            cookies=session_cookies
        )
        if response.status_code == 200:
            print("✅ Users retrieved successfully")
            users_response = response.json()
            print(f"   Number of users: {len(users_response['users'])}")
            for user in users_response['users']:
                print(f"   - {user['email']} ({user['role']})")
        else:
            print(f"❌ Get users failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting users: {e}")
    
    # Test 6: Get audit logs
    print("\n6. Testing audit logs retrieval...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/audit-logs?page=1&per_page=5",
            cookies=session_cookies
        )
        if response.status_code == 200:
            print("✅ Audit logs retrieved successfully")
            logs_response = response.json()
            print(f"   Number of logs: {len(logs_response['audit_logs'])}")
            print(f"   Total logs: {logs_response['pagination']['total']}")
            
            # Show first few logs
            for i, log in enumerate(logs_response['audit_logs'][:3]):
                print(f"   Log {i+1}: {log['action']} by {log['user']['email']}")
        else:
            print(f"❌ Get audit logs failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting audit logs: {e}")
    
    # Test 7: Get account details
    print("\n7. Testing account details retrieval...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/accounts/{account_id}",
            cookies=session_cookies
        )
        if response.status_code == 200:
            print("✅ Account details retrieved successfully")
            account_details = response.json()
            print(f"   Account: {account_details['account']['name']}")
            print(f"   Domain: {account_details['account']['domain']}")
        else:
            print(f"❌ Get account details failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting account details: {e}")
    
    # Test 8: Logout
    print("\n8. Testing logout...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            cookies=session_cookies
        )
        if response.status_code == 200:
            print("✅ Logout successful")
        else:
            print(f"❌ Logout failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error during logout: {e}")
    
    print("\n" + "=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    test_api() 