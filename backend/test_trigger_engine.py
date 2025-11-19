"""
Test suite for the Trigger Evaluation Engine
Tests all core functionality including condition evaluation, combination rules,
and notification rate limiting.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.trigger_engine import (
    evaluate_condition,
    apply_combination_rule,
    evaluate_trigger,
    evaluate_all_triggers,
    get_trigger_recommendations,
    check_notification_rate_limit
)
from database import (
    init_database,
    seed_users,
    seed_default_triggers,
    get_user_triggers,
    get_trigger_conditions
)


def test_evaluate_condition():
    """Test individual condition evaluation"""
    print("\n" + "="*70)
    print("TEST 1: Condition Evaluation")
    print("="*70)

    # Test cases
    test_cases = [
        {
            "name": "Temperature > 25 (True)",
            "condition": {"indicator": "temp", "operator": ">", "threshold_value": 25.0},
            "weather_data": {"temperature": 27.5, "humidity": 55, "rainfall": 1.2},
            "expected": True
        },
        {
            "name": "Temperature > 25 (False)",
            "condition": {"indicator": "temp", "operator": ">", "threshold_value": 25.0},
            "weather_data": {"temperature": 23.0, "humidity": 55, "rainfall": 1.2},
            "expected": False
        },
        {
            "name": "Rainfall < 2 (True)",
            "condition": {"indicator": "rainfall", "operator": "<", "threshold_value": 2.0},
            "weather_data": {"temperature": 27.5, "humidity": 55, "rainfall": 1.2},
            "expected": True
        },
        {
            "name": "Humidity <= 60 (True)",
            "condition": {"indicator": "humidity", "operator": "<=", "threshold_value": 60.0},
            "weather_data": {"temperature": 27.5, "humidity": 55, "rainfall": 1.2},
            "expected": True
        },
        {
            "name": "Wind speed >= 15 (True)",
            "condition": {"indicator": "wind_speed", "operator": ">=", "threshold_value": 15.0},
            "weather_data": {"temperature": 27.5, "humidity": 55, "rainfall": 1.2, "wind_speed": 15.0},
            "expected": True
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        result, error = evaluate_condition(test["condition"], test["weather_data"])

        if result == test["expected"]:
            print(f"✓ PASS: {test['name']}")
            passed += 1
        else:
            print(f"✗ FAIL: {test['name']} - Expected {test['expected']}, got {result}")
            if error:
                print(f"  Error: {error}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_combination_rules():
    """Test combination rule logic"""
    print("\n" + "="*70)
    print("TEST 2: Combination Rules")
    print("="*70)

    test_cases = [
        {
            "name": "any_1 with 1 true",
            "rule": "any_1",
            "conditions": [True, False, False],
            "expected": True
        },
        {
            "name": "any_1 with 0 true",
            "rule": "any_1",
            "conditions": [False, False, False],
            "expected": False
        },
        {
            "name": "any_2 with 2 true",
            "rule": "any_2",
            "conditions": [True, True, False],
            "expected": True
        },
        {
            "name": "any_2 with 1 true",
            "rule": "any_2",
            "conditions": [True, False, False],
            "expected": False
        },
        {
            "name": "any_3 with 3 true",
            "rule": "any_3",
            "conditions": [True, True, True],
            "expected": True
        },
        {
            "name": "any_3 with 2 true",
            "rule": "any_3",
            "conditions": [True, True, False],
            "expected": False
        },
        {
            "name": "all with all true",
            "rule": "all",
            "conditions": [True, True, True],
            "expected": True
        },
        {
            "name": "all with one false",
            "rule": "all",
            "conditions": [True, False, True],
            "expected": False
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        result = apply_combination_rule(test["rule"], test["conditions"])

        if result == test["expected"]:
            print(f"✓ PASS: {test['name']}")
            passed += 1
        else:
            print(f"✗ FAIL: {test['name']} - Expected {test['expected']}, got {result}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_trigger_evaluation():
    """Test full trigger evaluation with database integration"""
    print("\n" + "="*70)
    print("TEST 3: Full Trigger Evaluation (Database Integration)")
    print("="*70)

    # Initialize database
    print("\nInitializing database...")
    init_database()
    seed_users()
    seed_default_triggers()

    # Get Tim House's user ID (should be 2)
    from database import get_user_by_email
    tim_user = get_user_by_email("tim.house@fonterra.com")

    if not tim_user:
        print("✗ FAIL: Could not find Tim House user")
        return False

    user_id = tim_user['id']
    print(f"✓ Found user: {tim_user['name']} (ID: {user_id})")

    # Get triggers
    triggers = get_user_triggers(user_id)
    print(f"✓ Found {len(triggers)} triggers for user")

    if not triggers:
        print("✗ FAIL: No triggers found")
        return False

    # Test weather data that should trigger the alert
    # Tim's trigger: any_2 of (temp>25, rainfall<2, humidity<60)
    weather_data_triggering = {
        "temperature": 27.5,  # > 25 ✓
        "rainfall": 1.2,      # < 2 ✓
        "humidity": 65.0,     # NOT < 60 ✗
        "wind_speed": 15.0
    }

    print("\n--- Test Case 1: Should trigger (2/3 conditions met) ---")
    print(f"Weather data: temp={weather_data_triggering['temperature']}, "
          f"rainfall={weather_data_triggering['rainfall']}, "
          f"humidity={weather_data_triggering['humidity']}")

    alerts = evaluate_all_triggers(user_id, weather_data_triggering)

    if len(alerts) > 0:
        print(f"✓ PASS: Trigger fired ({len(alerts)} alerts)")
        for alert in alerts:
            print(f"\n  Alert: {alert['trigger']['name']}")
            print(f"  Region: {alert['trigger']['region']}")
            print(f"  Rule: {alert['trigger']['combination_rule']}")
            print(f"  Conditions met: {sum(1 for c in alert['conditions_met'] if c['met'])}")
            print(f"  Recommendations: {len(alert['recommendations'])}")
            for i, rec in enumerate(alert['recommendations'], 1):
                print(f"    {i}. {rec[:80]}...")
    else:
        print("✗ FAIL: Expected trigger to fire but it didn't")
        return False

    # Test weather data that should NOT trigger
    weather_data_not_triggering = {
        "temperature": 22.0,  # NOT > 25 ✗
        "rainfall": 3.5,      # NOT < 2 ✗
        "humidity": 65.0,     # NOT < 60 ✗
        "wind_speed": 10.0
    }

    print("\n--- Test Case 2: Should NOT trigger (0/3 conditions met) ---")
    print(f"Weather data: temp={weather_data_not_triggering['temperature']}, "
          f"rainfall={weather_data_not_triggering['rainfall']}, "
          f"humidity={weather_data_not_triggering['humidity']}")

    alerts = evaluate_all_triggers(user_id, weather_data_not_triggering)

    if len(alerts) == 0:
        print("✓ PASS: No alerts triggered (as expected)")
    else:
        print(f"✗ FAIL: Expected no alerts but got {len(alerts)}")
        return False

    return True


def test_recommendations():
    """Test recommendation generation"""
    print("\n" + "="*70)
    print("TEST 4: Recommendation Generation")
    print("="*70)

    conditions_met = [
        {
            "indicator": "temp",
            "operator": ">",
            "threshold_value": 25.0,
            "actual_value": 28.0,
            "met": True
        },
        {
            "indicator": "rainfall",
            "operator": "<",
            "threshold_value": 2.0,
            "actual_value": 1.2,
            "met": True
        },
        {
            "indicator": "humidity",
            "operator": "<",
            "threshold_value": 60.0,
            "actual_value": 55.0,
            "met": True
        }
    ]

    recommendations = get_trigger_recommendations(conditions_met)

    print(f"Generated {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

    # Should have at least 3 recommendations (one for each condition)
    if len(recommendations) >= 3:
        print("\n✓ PASS: Recommendations generated successfully")
        return True
    else:
        print(f"\n✗ FAIL: Expected at least 3 recommendations, got {len(recommendations)}")
        return False


def test_rate_limiting():
    """Test notification rate limiting"""
    print("\n" + "="*70)
    print("TEST 5: Notification Rate Limiting")
    print("="*70)

    # Get Tim House's user ID
    from database import get_user_by_email, log_notification
    tim_user = get_user_by_email("tim.house@fonterra.com")

    if not tim_user:
        print("✗ FAIL: Could not find Tim House user")
        return False

    user_id = tim_user['id']

    # Get first trigger
    triggers = get_user_triggers(user_id)
    if not triggers:
        print("✗ FAIL: No triggers found")
        return False

    trigger_id = triggers[0]['id']

    # Test 1: Should allow first notification
    should_send, last_sent = check_notification_rate_limit(trigger_id, user_id, rate_limit_hours=6)

    if should_send:
        print("✓ PASS: First notification allowed (no previous notification)")
    else:
        print("✗ FAIL: First notification should be allowed")
        return False

    # Log a notification
    print("\nLogging a test notification...")
    log_notification(
        trigger_id=trigger_id,
        user_id=user_id,
        trigger_conditions_met={"test": "data"}
    )

    # Test 2: Should NOT allow immediate second notification (within rate limit)
    should_send, last_sent = check_notification_rate_limit(trigger_id, user_id, rate_limit_hours=6)

    if not should_send:
        print("✓ PASS: Second notification blocked (within rate limit)")
        print(f"  Last sent: {last_sent}")
    else:
        print("✗ FAIL: Second notification should be blocked")
        return False

    # Test 3: Should allow if rate limit is very short (0 hours)
    should_send, last_sent = check_notification_rate_limit(trigger_id, user_id, rate_limit_hours=0)

    if should_send:
        print("✓ PASS: Notification allowed with 0-hour rate limit")
    else:
        print("✗ FAIL: Notification should be allowed with 0-hour rate limit")
        return False

    return True


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print("CKCIAS DROUGHT MONITOR - TRIGGER ENGINE TEST SUITE")
    print("="*70)

    results = {
        "Condition Evaluation": test_evaluate_condition(),
        "Combination Rules": test_combination_rules(),
        "Trigger Evaluation": test_trigger_evaluation(),
        "Recommendations": test_recommendations(),
        "Rate Limiting": test_rate_limiting()
    }

    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\n{total_passed}/{total_tests} test suites passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! Trigger engine is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    exit(exit_code)
