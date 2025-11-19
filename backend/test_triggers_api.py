#!/usr/bin/env python3
"""
Test script for Triggers API CRUD endpoints
Tests all endpoints in backend/routes/triggers.py
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:9100/api/triggers"
USER_ID = 2  # Tim House from Fonterra

# Test results tracking
test_results = []


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print and track test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    result = {
        "test": test_name,
        "passed": passed,
        "details": details
    }
    test_results.append(result)

    print(f"\n{status}: {test_name}")
    if details:
        print(f"  Details: {details}")


def print_response(response: requests.Response):
    """Print response details"""
    print(f"\n  Status Code: {response.status_code}")
    try:
        print(f"  Response Body:")
        print(json.dumps(response.json(), indent=2))
    except:
        print(f"  Response Text: {response.text}")


def test_create_trigger() -> Optional[int]:
    """Test POST /api/triggers - Create a new trigger"""
    print_section("TEST 1: POST /api/triggers - Create Trigger")

    trigger_data = {
        "user_id": USER_ID,
        "name": "Test Drought Alert",
        "region": "Taranaki",
        "conditions": [
            {
                "indicator": "temp",
                "operator": ">",
                "threshold": 25.0
            },
            {
                "indicator": "rainfall",
                "operator": "<",
                "threshold": 2.0
            }
        ],
        "combination_rule": "any_2",
        "is_active": True
    }

    print(f"\nRequest: POST {BASE_URL}")
    print(f"Body: {json.dumps(trigger_data, indent=2)}")

    try:
        response = requests.post(BASE_URL, json=trigger_data)
        print_response(response)

        if response.status_code == 201:
            data = response.json()
            trigger_id = data.get("id")

            # Validate response structure
            assert "id" in data, "Response missing 'id' field"
            assert data["name"] == trigger_data["name"], "Name mismatch"
            assert data["region"] == trigger_data["region"], "Region mismatch"
            assert len(data["conditions"]) == 2, "Conditions count mismatch"
            assert data["combination_rule"] == "any_2", "Combination rule mismatch"
            assert data["is_active"] == True, "is_active mismatch"

            print_test_result(
                "Create Trigger",
                True,
                f"Trigger created with ID: {trigger_id}"
            )
            return trigger_id
        else:
            print_test_result(
                "Create Trigger",
                False,
                f"Expected status 201, got {response.status_code}"
            )
            return None

    except Exception as e:
        print_test_result("Create Trigger", False, f"Exception: {str(e)}")
        return None


def test_list_triggers(user_id: int = USER_ID):
    """Test GET /api/triggers?user_id=X - List all triggers for a user"""
    print_section("TEST 2: GET /api/triggers?user_id={user_id} - List Triggers")

    url = f"{BASE_URL}?user_id={user_id}"
    print(f"\nRequest: GET {url}")

    try:
        response = requests.get(url)
        print_response(response)

        if response.status_code == 200:
            data = response.json()

            # Validate response structure
            assert "triggers" in data, "Response missing 'triggers' field"
            assert "total" in data, "Response missing 'total' field"
            assert isinstance(data["triggers"], list), "triggers should be a list"
            assert data["total"] == len(data["triggers"]), "total count mismatch"

            print_test_result(
                "List Triggers",
                True,
                f"Found {data['total']} trigger(s) for user {user_id}"
            )
        else:
            print_test_result(
                "List Triggers",
                False,
                f"Expected status 200, got {response.status_code}"
            )

    except Exception as e:
        print_test_result("List Triggers", False, f"Exception: {str(e)}")


def test_get_trigger(trigger_id: int):
    """Test GET /api/triggers/{id} - Get a specific trigger"""
    print_section(f"TEST 3: GET /api/triggers/{trigger_id} - Get Specific Trigger")

    url = f"{BASE_URL}/{trigger_id}"
    print(f"\nRequest: GET {url}")

    try:
        response = requests.get(url)
        print_response(response)

        if response.status_code == 200:
            data = response.json()

            # Validate response structure
            assert data["id"] == trigger_id, "ID mismatch"
            assert "name" in data, "Response missing 'name' field"
            assert "region" in data, "Response missing 'region' field"
            assert "conditions" in data, "Response missing 'conditions' field"
            assert "combination_rule" in data, "Response missing 'combination_rule' field"
            assert "is_active" in data, "Response missing 'is_active' field"
            assert "created_at" in data, "Response missing 'created_at' field"
            assert "updated_at" in data, "Response missing 'updated_at' field"

            print_test_result(
                "Get Specific Trigger",
                True,
                f"Retrieved trigger: {data['name']}"
            )
        else:
            print_test_result(
                "Get Specific Trigger",
                False,
                f"Expected status 200, got {response.status_code}"
            )

    except Exception as e:
        print_test_result("Get Specific Trigger", False, f"Exception: {str(e)}")


def test_update_trigger(trigger_id: int):
    """Test PUT /api/triggers/{id} - Update a trigger"""
    print_section(f"TEST 4: PUT /api/triggers/{trigger_id} - Update Trigger")

    update_data = {
        "name": "Updated Drought Alert",
        "conditions": [
            {
                "indicator": "temp",
                "operator": ">",
                "threshold": 30.0
            },
            {
                "indicator": "humidity",
                "operator": "<",
                "threshold": 40.0
            }
        ]
    }

    url = f"{BASE_URL}/{trigger_id}"
    print(f"\nRequest: PUT {url}")
    print(f"Body: {json.dumps(update_data, indent=2)}")

    try:
        response = requests.put(url, json=update_data)
        print_response(response)

        if response.status_code == 200:
            data = response.json()

            # Validate updates were applied
            assert data["id"] == trigger_id, "ID mismatch"
            assert data["name"] == update_data["name"], "Name not updated"
            assert len(data["conditions"]) == 2, "Conditions count mismatch"
            assert data["conditions"][0]["threshold"] == 30.0, "Threshold not updated"

            print_test_result(
                "Update Trigger",
                True,
                f"Trigger updated successfully"
            )
        else:
            print_test_result(
                "Update Trigger",
                False,
                f"Expected status 200, got {response.status_code}"
            )

    except Exception as e:
        print_test_result("Update Trigger", False, f"Exception: {str(e)}")


def test_toggle_trigger(trigger_id: int):
    """Test POST /api/triggers/{id}/toggle - Toggle trigger active status"""
    print_section(f"TEST 5: POST /api/triggers/{trigger_id}/toggle - Toggle Trigger")

    url = f"{BASE_URL}/{trigger_id}/toggle"

    # Get current status first
    current_response = requests.get(f"{BASE_URL}/{trigger_id}")
    current_status = current_response.json()["is_active"] if current_response.status_code == 200 else None

    print(f"\nCurrent status: {current_status}")
    print(f"Request: POST {url}")

    try:
        response = requests.post(url)
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            new_status = data["is_active"]

            # Validate status was toggled
            assert data["id"] == trigger_id, "ID mismatch"
            if current_status is not None:
                assert new_status != current_status, "Status not toggled"

            print_test_result(
                "Toggle Trigger",
                True,
                f"Status toggled from {current_status} to {new_status}"
            )
        else:
            print_test_result(
                "Toggle Trigger",
                False,
                f"Expected status 200, got {response.status_code}"
            )

    except Exception as e:
        print_test_result("Toggle Trigger", False, f"Exception: {str(e)}")


def test_delete_trigger(trigger_id: int):
    """Test DELETE /api/triggers/{id} - Delete a trigger"""
    print_section(f"TEST 6: DELETE /api/triggers/{trigger_id} - Delete Trigger")

    url = f"{BASE_URL}/{trigger_id}"
    print(f"\nRequest: DELETE {url}")

    try:
        response = requests.delete(url)
        print_response(response)

        if response.status_code == 200:
            data = response.json()

            # Validate response
            assert "message" in data, "Response missing 'message' field"
            assert "trigger_id" in data, "Response missing 'trigger_id' field"
            assert data["trigger_id"] == trigger_id, "trigger_id mismatch"

            # Verify trigger no longer exists
            verify_response = requests.get(f"{BASE_URL}/{trigger_id}")
            assert verify_response.status_code == 404, "Trigger still exists after deletion"

            print_test_result(
                "Delete Trigger",
                True,
                f"Trigger deleted successfully"
            )
        else:
            print_test_result(
                "Delete Trigger",
                False,
                f"Expected status 200, got {response.status_code}"
            )

    except Exception as e:
        print_test_result("Delete Trigger", False, f"Exception: {str(e)}")


def test_error_cases():
    """Test error handling"""
    print_section("TEST 7: Error Handling")

    # Test 1: Get non-existent trigger
    print("\n7a. Get non-existent trigger (ID 99999):")
    response = requests.get(f"{BASE_URL}/99999")
    print_response(response)

    passed = response.status_code == 404
    print_test_result(
        "Get non-existent trigger",
        passed,
        f"Expected 404, got {response.status_code}"
    )

    # Test 2: Create trigger with invalid indicator
    print("\n7b. Create trigger with invalid indicator:")
    invalid_data = {
        "user_id": USER_ID,
        "name": "Invalid Trigger",
        "region": "Test",
        "conditions": [
            {
                "indicator": "invalid_indicator",
                "operator": ">",
                "threshold": 25.0
            }
        ],
        "combination_rule": "any_1",
        "is_active": True
    }
    response = requests.post(BASE_URL, json=invalid_data)
    print_response(response)

    passed = response.status_code == 422  # Validation error
    print_test_result(
        "Invalid indicator validation",
        passed,
        f"Expected 422, got {response.status_code}"
    )

    # Test 3: Create trigger with invalid combination rule
    print("\n7c. Create trigger with invalid combination rule:")
    invalid_data = {
        "user_id": USER_ID,
        "name": "Invalid Trigger",
        "region": "Test",
        "conditions": [
            {
                "indicator": "temp",
                "operator": ">",
                "threshold": 25.0
            }
        ],
        "combination_rule": "invalid_rule",
        "is_active": True
    }
    response = requests.post(BASE_URL, json=invalid_data)
    print_response(response)

    passed = response.status_code == 422  # Validation error
    print_test_result(
        "Invalid combination rule validation",
        passed,
        f"Expected 422, got {response.status_code}"
    )

    # Test 4: Update non-existent trigger
    print("\n7d. Update non-existent trigger (ID 99999):")
    response = requests.put(f"{BASE_URL}/99999", json={"name": "Updated"})
    print_response(response)

    passed = response.status_code == 404
    print_test_result(
        "Update non-existent trigger",
        passed,
        f"Expected 404, got {response.status_code}"
    )

    # Test 5: Delete non-existent trigger
    print("\n7e. Delete non-existent trigger (ID 99999):")
    response = requests.delete(f"{BASE_URL}/99999")
    print_response(response)

    passed = response.status_code == 404
    print_test_result(
        "Delete non-existent trigger",
        passed,
        f"Expected 404, got {response.status_code}"
    )


def print_summary():
    """Print test summary"""
    print_section("TEST SUMMARY")

    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r["passed"])
    failed_tests = total_tests - passed_tests

    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%\n")

    if failed_tests > 0:
        print("\nFailed Tests:")
        for result in test_results:
            if not result["passed"]:
                print(f"  ✗ {result['test']}: {result['details']}")

    print("\n" + "=" * 80 + "\n")

    return failed_tests == 0


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "CKCIAS TRIGGERS API TEST SUITE" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝")

    # Test server connectivity
    print_section("Checking server connectivity...")
    try:
        response = requests.get("http://localhost:9100/health", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running at http://localhost:9100")
        else:
            print("✗ Server returned unexpected status code")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server at http://localhost:9100")
        print("  Please ensure the backend server is running:")
        print("  cd backend && python main.py")
        sys.exit(1)

    # Run all tests
    trigger_id = test_create_trigger()

    if trigger_id:
        test_list_triggers()
        test_get_trigger(trigger_id)
        test_update_trigger(trigger_id)
        test_toggle_trigger(trigger_id)
        test_delete_trigger(trigger_id)
    else:
        print("\n✗ Skipping remaining tests due to trigger creation failure")

    test_error_cases()

    # Print summary
    all_passed = print_summary()

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
