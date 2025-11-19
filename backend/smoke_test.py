#!/usr/bin/env python3
"""
CKCIAS Drought Monitor Smoke Test Suite
Tests all backend functionality including database and API endpoints
"""

import requests
import json
import sqlite3
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:9100"
DB_PATH = "ckcias.db"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(test_name, status, message=""):
    """Print formatted test result"""
    if status == "PASS":
        print(f"{Colors.GREEN}✓{Colors.RESET} {test_name} - PASS {message}")
    elif status == "FAIL":
        print(f"{Colors.RED}✗{Colors.RESET} {test_name} - FAIL {message}")
    elif status == "INFO":
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {test_name} {message}")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {test_name} - {status} {message}")

def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

# Test Results Tracker
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

def record_test(test_name, passed, error_msg=""):
    """Record test result"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append({
            "test": test_name,
            "error": error_msg
        })

# ========================================
# DATABASE VERIFICATION TESTS
# ========================================

def test_database_verification():
    """Test 1: Verify database was created and has correct schema"""
    print_section("TEST 1: DATABASE VERIFICATION")

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Test 1.1: Verify users table exists and has data
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()["count"]
        if user_count == 2:
            print_test("Users table", "PASS", f"- Found {user_count} users")
            record_test("Database users count", True)
        else:
            print_test("Users table", "FAIL", f"- Expected 2 users, found {user_count}")
            record_test("Database users count", False, f"Expected 2, got {user_count}")

        # Test 1.2: Verify Regan exists
        cursor.execute("SELECT * FROM users WHERE email = ?", ("regan@axiomintelligence.co.nz",))
        regan = cursor.fetchone()
        if regan and regan["name"] == "Regan" and regan["region"] == "Auckland":
            print_test("User: Regan", "PASS", "- All fields correct")
            record_test("User Regan exists", True)
        else:
            print_test("User: Regan", "FAIL", "- User not found or incorrect data")
            record_test("User Regan exists", False, "User missing or incorrect")

        # Test 1.3: Verify Tim House exists
        cursor.execute("SELECT * FROM users WHERE email = ?", ("tim.house@fonterra.com",))
        tim = cursor.fetchone()
        if tim and tim["name"] == "Tim House" and tim["region"] == "Taranaki":
            print_test("User: Tim House", "PASS", "- All fields correct")
            record_test("User Tim House exists", True)
        else:
            print_test("User: Tim House", "FAIL", "- User not found or incorrect data")
            record_test("User Tim House exists", False, "User missing or incorrect")

        # Test 1.4: Verify triggers table exists
        cursor.execute("SELECT COUNT(*) as count FROM triggers")
        trigger_count = cursor.fetchone()["count"]
        if trigger_count >= 1:
            print_test("Triggers table", "PASS", f"- Found {trigger_count} trigger(s)")
            record_test("Database triggers exist", True)
        else:
            print_test("Triggers table", "FAIL", "- No triggers found")
            record_test("Database triggers exist", False, "No triggers")

        # Test 1.5: Verify Tim's default trigger
        cursor.execute("""
            SELECT t.*, u.name as user_name
            FROM triggers t
            JOIN users u ON t.user_id = u.id
            WHERE u.email = ? AND t.name = ?
        """, ("tim.house@fonterra.com", "Taranaki Drought Alert"))
        tim_trigger = cursor.fetchone()

        if tim_trigger:
            print_test("Tim's default trigger", "PASS", f"- Found 'Taranaki Drought Alert' (ID: {tim_trigger['id']})")
            record_test("Tim default trigger exists", True)

            # Test 1.6: Verify trigger conditions
            cursor.execute("SELECT * FROM trigger_conditions WHERE trigger_id = ?", (tim_trigger['id'],))
            conditions = cursor.fetchall()
            if len(conditions) == 3:
                print_test("Trigger conditions", "PASS", f"- Found {len(conditions)} conditions")
                record_test("Trigger conditions count", True)

                # Verify each condition
                expected_conditions = [
                    {"indicator": "temp", "operator": ">", "threshold_value": 25.0},
                    {"indicator": "rainfall", "operator": "<", "threshold_value": 2.0},
                    {"indicator": "humidity", "operator": "<", "threshold_value": 60.0}
                ]

                conditions_list = [dict(c) for c in conditions]
                all_match = True
                for expected in expected_conditions:
                    found = False
                    for actual in conditions_list:
                        if (actual["indicator"] == expected["indicator"] and
                            actual["operator"] == expected["operator"] and
                            actual["threshold_value"] == expected["threshold_value"]):
                            found = True
                            break
                    if found:
                        print_test(f"  Condition: {expected['indicator']} {expected['operator']} {expected['threshold_value']}", "PASS", "")
                    else:
                        print_test(f"  Condition: {expected['indicator']} {expected['operator']} {expected['threshold_value']}", "FAIL", "- Not found")
                        all_match = False

                record_test("Trigger conditions match expected", all_match, "" if all_match else "Conditions mismatch")
            else:
                print_test("Trigger conditions", "FAIL", f"- Expected 3 conditions, found {len(conditions)}")
                record_test("Trigger conditions count", False, f"Expected 3, got {len(conditions)}")
        else:
            print_test("Tim's default trigger", "FAIL", "- Not found")
            record_test("Tim default trigger exists", False, "Trigger not found")

        conn.close()
        return True

    except Exception as e:
        print_test("Database verification", "FAIL", f"- Error: {str(e)}")
        record_test("Database verification", False, str(e))
        return False

# ========================================
# API ENDPOINT TESTS
# ========================================

def test_health_endpoint():
    """Test 2: Health check endpoint"""
    print_section("TEST 2: HEALTH ENDPOINT")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print_test("GET /health", "PASS", f"- Status: {data.get('status')}")
                print_test("  Response data", "INFO", f"- {json.dumps(data, indent=2)}")
                record_test("Health endpoint", True)
                return True
            else:
                print_test("GET /health", "FAIL", f"- Unexpected status: {data.get('status')}")
                record_test("Health endpoint", False, f"Status: {data.get('status')}")
                return False
        else:
            print_test("GET /health", "FAIL", f"- HTTP {response.status_code}")
            record_test("Health endpoint", False, f"HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_test("GET /health", "FAIL", "- Connection refused (server not running)")
        record_test("Health endpoint", False, "Connection refused")
        return False
    except Exception as e:
        print_test("GET /health", "FAIL", f"- Error: {str(e)}")
        record_test("Health endpoint", False, str(e))
        return False

def test_list_triggers():
    """Test 3: GET /api/triggers - List triggers for user"""
    print_section("TEST 3: GET /api/triggers - LIST TRIGGERS")

    try:
        # Test 3.1: List Tim's triggers (user_id=2)
        response = requests.get(f"{BASE_URL}/api/triggers?user_id=2", timeout=5)

        if response.status_code == 200:
            data = response.json()
            if "triggers" in data and len(data["triggers"]) >= 1:
                print_test("GET /api/triggers?user_id=2", "PASS", f"- Found {len(data['triggers'])} trigger(s)")
                print_test("  Response", "INFO", f"\n{json.dumps(data, indent=2)}")
                record_test("List triggers for Tim", True)
                return data["triggers"]
            else:
                print_test("GET /api/triggers?user_id=2", "FAIL", "- No triggers returned")
                record_test("List triggers for Tim", False, "No triggers")
                return []
        else:
            print_test("GET /api/triggers?user_id=2", "FAIL", f"- HTTP {response.status_code}")
            record_test("List triggers for Tim", False, f"HTTP {response.status_code}")
            return []

    except Exception as e:
        print_test("GET /api/triggers", "FAIL", f"- Error: {str(e)}")
        record_test("List triggers for Tim", False, str(e))
        return []

def test_create_trigger():
    """Test 4: POST /api/triggers - Create new trigger"""
    print_section("TEST 4: POST /api/triggers - CREATE TRIGGER")

    try:
        # Create a test trigger for Regan (user_id=1)
        new_trigger = {
            "user_id": 1,
            "name": "Auckland Heat Alert",
            "region": "Auckland",
            "conditions": [
                {"indicator": "temp", "operator": ">", "threshold": 30.0},
                {"indicator": "humidity", "operator": "<", "threshold": 50.0}
            ],
            "combination_rule": "any_2",
            "is_active": True
        }

        response = requests.post(
            f"{BASE_URL}/api/triggers",
            json=new_trigger,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code == 201:
            data = response.json()
            if "id" in data and data["name"] == "Auckland Heat Alert":
                print_test("POST /api/triggers", "PASS", f"- Created trigger ID: {data['id']}")
                print_test("  Response", "INFO", f"\n{json.dumps(data, indent=2)}")
                record_test("Create trigger", True)
                return data
            else:
                print_test("POST /api/triggers", "FAIL", "- Unexpected response format")
                record_test("Create trigger", False, "Invalid response format")
                return None
        else:
            print_test("POST /api/triggers", "FAIL", f"- HTTP {response.status_code}: {response.text}")
            record_test("Create trigger", False, f"HTTP {response.status_code}")
            return None

    except Exception as e:
        print_test("POST /api/triggers", "FAIL", f"- Error: {str(e)}")
        record_test("Create trigger", False, str(e))
        return None

def test_get_single_trigger(trigger_id):
    """Test 5: GET /api/triggers/{id} - Get single trigger"""
    print_section(f"TEST 5: GET /api/triggers/{trigger_id} - GET SINGLE TRIGGER")

    try:
        response = requests.get(f"{BASE_URL}/api/triggers/{trigger_id}", timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data["id"] == trigger_id:
                print_test(f"GET /api/triggers/{trigger_id}", "PASS", f"- Retrieved trigger '{data['name']}'")
                print_test("  Response", "INFO", f"\n{json.dumps(data, indent=2)}")
                record_test("Get single trigger", True)
                return data
            else:
                print_test(f"GET /api/triggers/{trigger_id}", "FAIL", "- ID mismatch")
                record_test("Get single trigger", False, "ID mismatch")
                return None
        elif response.status_code == 404:
            print_test(f"GET /api/triggers/{trigger_id}", "FAIL", "- Trigger not found (404)")
            record_test("Get single trigger", False, "404 Not Found")
            return None
        else:
            print_test(f"GET /api/triggers/{trigger_id}", "FAIL", f"- HTTP {response.status_code}")
            record_test("Get single trigger", False, f"HTTP {response.status_code}")
            return None

    except Exception as e:
        print_test(f"GET /api/triggers/{trigger_id}", "FAIL", f"- Error: {str(e)}")
        record_test("Get single trigger", False, str(e))
        return None

def test_update_trigger(trigger_id):
    """Test 6: PUT /api/triggers/{id} - Update trigger"""
    print_section(f"TEST 6: PUT /api/triggers/{trigger_id} - UPDATE TRIGGER")

    try:
        update_data = {
            "name": "Auckland Heat Alert - Updated",
            "conditions": [
                {"indicator": "temp", "operator": ">=", "threshold": 32.0},
                {"indicator": "humidity", "operator": "<=", "threshold": 45.0}
            ]
        }

        response = requests.put(
            f"{BASE_URL}/api/triggers/{trigger_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            if data["name"] == "Auckland Heat Alert - Updated":
                print_test(f"PUT /api/triggers/{trigger_id}", "PASS", "- Trigger updated successfully")
                print_test("  Response", "INFO", f"\n{json.dumps(data, indent=2)}")
                record_test("Update trigger", True)
                return data
            else:
                print_test(f"PUT /api/triggers/{trigger_id}", "FAIL", "- Update not reflected")
                record_test("Update trigger", False, "Changes not applied")
                return None
        else:
            print_test(f"PUT /api/triggers/{trigger_id}", "FAIL", f"- HTTP {response.status_code}: {response.text}")
            record_test("Update trigger", False, f"HTTP {response.status_code}")
            return None

    except Exception as e:
        print_test(f"PUT /api/triggers/{trigger_id}", "FAIL", f"- Error: {str(e)}")
        record_test("Update trigger", False, str(e))
        return None

def test_toggle_trigger(trigger_id):
    """Test 7: POST /api/triggers/{id}/toggle - Toggle trigger status"""
    print_section(f"TEST 7: POST /api/triggers/{trigger_id}/toggle - TOGGLE TRIGGER")

    try:
        # Get current status first
        current = requests.get(f"{BASE_URL}/api/triggers/{trigger_id}", timeout=5).json()
        original_status = current["is_active"]

        # Toggle the trigger
        response = requests.post(f"{BASE_URL}/api/triggers/{trigger_id}/toggle", timeout=5)

        if response.status_code == 200:
            data = response.json()
            new_status = data["is_active"]

            if new_status != original_status:
                print_test(f"POST /api/triggers/{trigger_id}/toggle", "PASS",
                          f"- Toggled from {original_status} to {new_status}")
                print_test("  Response", "INFO", f"\n{json.dumps(data, indent=2)}")
                record_test("Toggle trigger", True)
                return data
            else:
                print_test(f"POST /api/triggers/{trigger_id}/toggle", "FAIL", "- Status not changed")
                record_test("Toggle trigger", False, "Status unchanged")
                return None
        else:
            print_test(f"POST /api/triggers/{trigger_id}/toggle", "FAIL", f"- HTTP {response.status_code}")
            record_test("Toggle trigger", False, f"HTTP {response.status_code}")
            return None

    except Exception as e:
        print_test(f"POST /api/triggers/{trigger_id}/toggle", "FAIL", f"- Error: {str(e)}")
        record_test("Toggle trigger", False, str(e))
        return None

def test_delete_trigger(trigger_id):
    """Test 8: DELETE /api/triggers/{id} - Delete trigger"""
    print_section(f"TEST 8: DELETE /api/triggers/{trigger_id} - DELETE TRIGGER")

    try:
        response = requests.delete(f"{BASE_URL}/api/triggers/{trigger_id}", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_test(f"DELETE /api/triggers/{trigger_id}", "PASS", f"- {data.get('message', 'Deleted')}")
            record_test("Delete trigger", True)

            # Verify deletion by trying to get the trigger
            verify = requests.get(f"{BASE_URL}/api/triggers/{trigger_id}", timeout=5)
            if verify.status_code == 404:
                print_test("  Verification", "PASS", "- Trigger no longer exists (404)")
                record_test("Delete verification", True)
            else:
                print_test("  Verification", "FAIL", f"- Trigger still exists (HTTP {verify.status_code})")
                record_test("Delete verification", False, "Trigger still exists")

            return True
        else:
            print_test(f"DELETE /api/triggers/{trigger_id}", "FAIL", f"- HTTP {response.status_code}")
            record_test("Delete trigger", False, f"HTTP {response.status_code}")
            return False

    except Exception as e:
        print_test(f"DELETE /api/triggers/{trigger_id}", "FAIL", f"- Error: {str(e)}")
        record_test("Delete trigger", False, str(e))
        return False

# ========================================
# VALIDATION TESTS
# ========================================

def test_validation_constraints():
    """Test 9: Database validation constraints"""
    print_section("TEST 9: VALIDATION CONSTRAINTS")

    # Test 9.1: Invalid indicator
    try:
        invalid_indicator = {
            "user_id": 1,
            "name": "Invalid Indicator Test",
            "region": "Auckland",
            "conditions": [
                {"indicator": "invalid_indicator", "operator": ">", "threshold": 25.0}
            ],
            "combination_rule": "any_1",
            "is_active": True
        }

        response = requests.post(
            f"{BASE_URL}/api/triggers",
            json=invalid_indicator,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code == 422 or response.status_code == 400:
            print_test("Invalid indicator rejection", "PASS", "- Correctly rejected")
            record_test("Invalid indicator validation", True)
        else:
            print_test("Invalid indicator rejection", "FAIL", f"- Expected 400/422, got {response.status_code}")
            record_test("Invalid indicator validation", False, f"Got {response.status_code}")

    except Exception as e:
        print_test("Invalid indicator rejection", "FAIL", f"- Error: {str(e)}")
        record_test("Invalid indicator validation", False, str(e))

    # Test 9.2: Invalid combination_rule
    try:
        invalid_rule = {
            "user_id": 1,
            "name": "Invalid Rule Test",
            "region": "Auckland",
            "conditions": [
                {"indicator": "temp", "operator": ">", "threshold": 25.0}
            ],
            "combination_rule": "invalid_rule",
            "is_active": True
        }

        response = requests.post(
            f"{BASE_URL}/api/triggers",
            json=invalid_rule,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code == 422 or response.status_code == 400:
            print_test("Invalid combination_rule rejection", "PASS", "- Correctly rejected")
            record_test("Invalid combination_rule validation", True)
        else:
            print_test("Invalid combination_rule rejection", "FAIL", f"- Expected 400/422, got {response.status_code}")
            record_test("Invalid combination_rule validation", False, f"Got {response.status_code}")

    except Exception as e:
        print_test("Invalid combination_rule rejection", "FAIL", f"- Error: {str(e)}")
        record_test("Invalid combination_rule validation", False, str(e))

    # Test 9.3: Invalid operator
    try:
        invalid_operator = {
            "user_id": 1,
            "name": "Invalid Operator Test",
            "region": "Auckland",
            "conditions": [
                {"indicator": "temp", "operator": "invalid", "threshold": 25.0}
            ],
            "combination_rule": "any_1",
            "is_active": True
        }

        response = requests.post(
            f"{BASE_URL}/api/triggers",
            json=invalid_operator,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code == 422 or response.status_code == 400:
            print_test("Invalid operator rejection", "PASS", "- Correctly rejected")
            record_test("Invalid operator validation", True)
        else:
            print_test("Invalid operator rejection", "FAIL", f"- Expected 400/422, got {response.status_code}")
            record_test("Invalid operator validation", False, f"Got {response.status_code}")

    except Exception as e:
        print_test("Invalid operator rejection", "FAIL", f"- Error: {str(e)}")
        record_test("Invalid operator validation", False, str(e))

# ========================================
# MAIN TEST RUNNER
# ========================================

def main():
    """Run all smoke tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"CKCIAS DROUGHT MONITOR - SMOKE TEST SUITE")
    print(f"{'='*60}{Colors.RESET}\n")
    print(f"Testing backend at: {BASE_URL}")
    print(f"Database: {DB_PATH}")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Test 1: Database Verification
    db_ok = test_database_verification()

    # Test 2: Health Endpoint
    health_ok = test_health_endpoint()

    if not health_ok:
        print(f"\n{Colors.RED}⚠ WARNING: Backend server is not responding!{Colors.RESET}")
        print(f"{Colors.YELLOW}Please ensure the server is running with: uvicorn main:app --port 9100{Colors.RESET}\n")

        # Print summary even if server is down
        print_section("TEST SUMMARY")
        print(f"Total Tests: {test_results['total']}")
        print(f"{Colors.GREEN}Passed: {test_results['passed']}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {test_results['failed']}{Colors.RESET}")

        if test_results["errors"]:
            print(f"\n{Colors.RED}ERRORS:{Colors.RESET}")
            for error in test_results["errors"]:
                print(f"  - {error['test']}: {error['error']}")

        sys.exit(1)

    # Test 3: List Triggers
    triggers = test_list_triggers()

    # Test 4: Create Trigger
    new_trigger = test_create_trigger()

    if new_trigger:
        trigger_id = new_trigger["id"]

        # Test 5: Get Single Trigger
        test_get_single_trigger(trigger_id)

        # Test 6: Update Trigger
        test_update_trigger(trigger_id)

        # Test 7: Toggle Trigger
        test_toggle_trigger(trigger_id)

        # Test 8: Delete Trigger
        test_delete_trigger(trigger_id)
    else:
        print(f"\n{Colors.YELLOW}⚠ Skipping tests 5-8 (dependent on trigger creation){Colors.RESET}")

    # Test 9: Validation Constraints
    test_validation_constraints()

    # ========================================
    # FINAL SUMMARY
    # ========================================

    print_section("TEST SUMMARY")

    print(f"Total Tests: {test_results['total']}")
    print(f"{Colors.GREEN}Passed: {test_results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {test_results['failed']}{Colors.RESET}")

    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")

    if test_results["errors"]:
        print(f"\n{Colors.RED}ERRORS:{Colors.RESET}")
        for error in test_results["errors"]:
            print(f"  - {error['test']}: {error['error']}")

    # Recommendations
    print_section("RECOMMENDATIONS")

    if test_results["failed"] == 0:
        print(f"{Colors.GREEN}✓ All tests passed! Backend is production-ready for Day 2 work.{Colors.RESET}\n")
        print("The backend successfully:")
        print("  - Created and seeded the database")
        print("  - Responds to health checks")
        print("  - Handles all CRUD operations for triggers")
        print("  - Validates input constraints properly")
        print("  - Returns properly formatted JSON responses")
    else:
        print(f"{Colors.YELLOW}⚠ {test_results['failed']} test(s) failed.{Colors.RESET}\n")
        print("Recommendations:")
        print("  1. Review the error messages above")
        print("  2. Fix any database schema issues")
        print("  3. Ensure all API endpoints are properly registered")
        print("  4. Verify validation logic is working correctly")
        print("  5. Re-run smoke tests after fixes")

    print(f"\n{Colors.BLUE}Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

    # Exit with proper code
    sys.exit(0 if test_results["failed"] == 0 else 1)

if __name__ == "__main__":
    main()
