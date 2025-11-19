"""
Unit tests for the Trigger Evaluation Engine

This test suite provides comprehensive coverage of:
- Single condition evaluation with all operators
- Combination rules (any_1, any_2, any_3, all)
- Edge cases (missing data, invalid operators, null values)
- Error handling and validation

Run with: python -m pytest test_trigger_engine.py -v
Or directly: python test_trigger_engine.py
"""

import unittest
from typing import Dict, Any
from trigger_engine import (
    evaluate_condition,
    apply_combination_rule,
    get_trigger_recommendations,
    OPERATORS,
    INDICATOR_MAP
)


class TestSingleConditionEvaluation(unittest.TestCase):
    """Test individual condition evaluation"""

    def setUp(self):
        """Set up test weather data"""
        self.weather_data = {
            'temperature': 27.5,
            'rainfall': 1.2,
            'humidity': 55.0,
            'wind_speed': 15.0
        }

    def test_temperature_greater_than_true(self):
        """Test temperature > threshold (should pass)"""
        condition = {
            'indicator': 'temp',
            'operator': '>',
            'threshold_value': 25.0
        }
        result, error = evaluate_condition(condition, self.weather_data)
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_temperature_greater_than_false(self):
        """Test temperature > threshold (should fail)"""
        condition = {
            'indicator': 'temp',
            'operator': '>',
            'threshold_value': 30.0
        }
        result, error = evaluate_condition(condition, self.weather_data)
        self.assertFalse(result)
        self.assertIsNone(error)

    def test_rainfall_less_than_true(self):
        """Test rainfall < threshold (should pass)"""
        condition = {
            'indicator': 'rainfall',
            'operator': '<',
            'threshold_value': 2.0
        }
        result, error = evaluate_condition(condition, self.weather_data)
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_rainfall_less_than_false(self):
        """Test rainfall < threshold (should fail)"""
        condition = {
            'indicator': 'rainfall',
            'operator': '<',
            'threshold_value': 1.0
        }
        result, error = evaluate_condition(condition, self.weather_data)
        self.assertFalse(result)
        self.assertIsNone(error)

    def test_humidity_less_than_or_equal_true(self):
        """Test humidity <= threshold (should pass)"""
        condition = {
            'indicator': 'humidity',
            'operator': '<=',
            'threshold_value': 55.0
        }
        result, error = evaluate_condition(condition, self.weather_data)
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_humidity_greater_than_or_equal_true(self):
        """Test humidity >= threshold (should pass)"""
        condition = {
            'indicator': 'humidity',
            'operator': '>=',
            'threshold_value': 55.0
        }
        result, error = evaluate_condition(condition, self.weather_data)
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_wind_speed_equal_true(self):
        """Test wind_speed == threshold (should pass)"""
        condition = {
            'indicator': 'wind_speed',
            'operator': '==',
            'threshold_value': 15.0
        }
        result, error = evaluate_condition(condition, self.weather_data)
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_wind_speed_equal_false(self):
        """Test wind_speed == threshold (should fail)"""
        condition = {
            'indicator': 'wind_speed',
            'operator': '==',
            'threshold_value': 20.0
        }
        result, error = evaluate_condition(condition, self.weather_data)
        self.assertFalse(result)
        self.assertIsNone(error)

    def test_all_operators(self):
        """Test all supported operators"""
        operators_to_test = [
            ('>', 20.0, True),   # 27.5 > 20.0
            ('>', 30.0, False),  # 27.5 > 30.0
            ('<', 30.0, True),   # 27.5 < 30.0
            ('<', 20.0, False),  # 27.5 < 20.0
            ('>=', 27.5, True),  # 27.5 >= 27.5
            ('>=', 28.0, False), # 27.5 >= 28.0
            ('<=', 27.5, True),  # 27.5 <= 27.5
            ('<=', 27.0, False), # 27.5 <= 27.0
            ('==', 27.5, True),  # 27.5 == 27.5
            ('==', 28.0, False), # 27.5 == 28.0
        ]

        for operator, threshold, expected in operators_to_test:
            with self.subTest(operator=operator, threshold=threshold):
                condition = {
                    'indicator': 'temp',
                    'operator': operator,
                    'threshold_value': threshold
                }
                result, error = evaluate_condition(condition, self.weather_data)
                self.assertEqual(result, expected,
                    f"27.5 {operator} {threshold} should be {expected}")
                self.assertIsNone(error)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        """Set up test data"""
        self.valid_weather_data = {
            'temperature': 27.5,
            'rainfall': 1.2,
            'humidity': 55.0,
            'wind_speed': 15.0
        }

    def test_missing_indicator_field(self):
        """Test condition with missing indicator field"""
        condition = {
            'operator': '>',
            'threshold_value': 25.0
        }
        result, error = evaluate_condition(condition, self.valid_weather_data)
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertIn("missing required fields", error)

    def test_missing_operator_field(self):
        """Test condition with missing operator field"""
        condition = {
            'indicator': 'temp',
            'threshold_value': 25.0
        }
        result, error = evaluate_condition(condition, self.valid_weather_data)
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertIn("missing required fields", error)

    def test_missing_threshold_field(self):
        """Test condition with missing threshold field"""
        condition = {
            'indicator': 'temp',
            'operator': '>'
        }
        result, error = evaluate_condition(condition, self.valid_weather_data)
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertIn("missing required fields", error)

    def test_invalid_operator(self):
        """Test condition with invalid operator"""
        condition = {
            'indicator': 'temp',
            'operator': '!=',  # Not supported
            'threshold_value': 25.0
        }
        result, error = evaluate_condition(condition, self.valid_weather_data)
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertIn("Invalid operator", error)

    def test_invalid_indicator(self):
        """Test condition with invalid indicator"""
        condition = {
            'indicator': 'pressure',  # Not in INDICATOR_MAP
            'operator': '>',
            'threshold_value': 1000.0
        }
        result, error = evaluate_condition(condition, self.valid_weather_data)
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertIn("Invalid indicator", error)

    def test_missing_weather_data_field(self):
        """Test when weather data is missing required field"""
        incomplete_weather_data = {
            'rainfall': 1.2,
            'humidity': 55.0
            # Missing 'temperature'
        }
        condition = {
            'indicator': 'temp',
            'operator': '>',
            'threshold_value': 25.0
        }
        result, error = evaluate_condition(condition, incomplete_weather_data)
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertIn("missing indicator", error)

    def test_null_weather_value(self):
        """Test when weather data has None/null value"""
        weather_data_with_null = {
            'temperature': None,
            'rainfall': 1.2,
            'humidity': 55.0
        }
        condition = {
            'indicator': 'temp',
            'operator': '>',
            'threshold_value': 25.0
        }
        result, error = evaluate_condition(condition, weather_data_with_null)
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertIn("null value", error)

    def test_empty_weather_data(self):
        """Test with empty weather data dictionary"""
        condition = {
            'indicator': 'temp',
            'operator': '>',
            'threshold_value': 25.0
        }
        result, error = evaluate_condition(condition, {})
        self.assertFalse(result)
        self.assertIsNotNone(error)

    def test_string_threshold_value(self):
        """Test that string threshold values are handled (should convert to float)"""
        condition = {
            'indicator': 'temp',
            'operator': '>',
            'threshold_value': '25.0'  # String instead of float
        }
        result, error = evaluate_condition(condition, self.valid_weather_data)
        self.assertTrue(result)  # Should work due to float() conversion
        self.assertIsNone(error)

    def test_string_weather_value(self):
        """Test that string weather values are handled (should convert to float)"""
        weather_data = {
            'temperature': '27.5',  # String instead of float
            'rainfall': 1.2
        }
        condition = {
            'indicator': 'temp',
            'operator': '>',
            'threshold_value': 25.0
        }
        result, error = evaluate_condition(condition, weather_data)
        self.assertTrue(result)  # Should work due to float() conversion
        self.assertIsNone(error)

    def test_zero_threshold(self):
        """Test with zero threshold value"""
        condition = {
            'indicator': 'rainfall',
            'operator': '>',
            'threshold_value': 0
        }
        result, error = evaluate_condition(condition, self.valid_weather_data)
        self.assertTrue(result)  # 1.2 > 0
        self.assertIsNone(error)

    def test_negative_values(self):
        """Test with negative threshold and weather values"""
        weather_data = {
            'temperature': -5.0  # Below freezing
        }
        condition = {
            'indicator': 'temp',
            'operator': '<',
            'threshold_value': 0
        }
        result, error = evaluate_condition(condition, weather_data)
        self.assertTrue(result)  # -5 < 0
        self.assertIsNone(error)


class TestCombinationRules(unittest.TestCase):
    """Test combination rule logic"""

    def test_any_1_with_one_true(self):
        """Test any_1 rule with 1 condition met out of 3"""
        result = apply_combination_rule('any_1', conditions_met_count=1, total_conditions=3)
        self.assertTrue(result)

    def test_any_1_with_zero_true(self):
        """Test any_1 rule with 0 conditions met"""
        result = apply_combination_rule('any_1', conditions_met_count=0, total_conditions=3)
        self.assertFalse(result)

    def test_any_1_with_all_true(self):
        """Test any_1 rule with all conditions met"""
        result = apply_combination_rule('any_1', conditions_met_count=3, total_conditions=3)
        self.assertTrue(result)

    def test_any_2_with_two_true(self):
        """Test any_2 rule with exactly 2 conditions met out of 3"""
        result = apply_combination_rule('any_2', conditions_met_count=2, total_conditions=3)
        self.assertTrue(result)

    def test_any_2_with_one_true(self):
        """Test any_2 rule with only 1 condition met"""
        result = apply_combination_rule('any_2', conditions_met_count=1, total_conditions=3)
        self.assertFalse(result)

    def test_any_2_with_three_true(self):
        """Test any_2 rule with 3 conditions met (should still pass)"""
        result = apply_combination_rule('any_2', conditions_met_count=3, total_conditions=3)
        self.assertTrue(result)

    def test_any_2_with_zero_true(self):
        """Test any_2 rule with 0 conditions met"""
        result = apply_combination_rule('any_2', conditions_met_count=0, total_conditions=3)
        self.assertFalse(result)

    def test_any_3_with_three_true(self):
        """Test any_3 rule with exactly 3 conditions met"""
        result = apply_combination_rule('any_3', conditions_met_count=3, total_conditions=3)
        self.assertTrue(result)

    def test_any_3_with_two_true(self):
        """Test any_3 rule with only 2 conditions met out of 3"""
        result = apply_combination_rule('any_3', conditions_met_count=2, total_conditions=3)
        self.assertFalse(result)

    def test_any_3_with_four_true(self):
        """Test any_3 rule with 4 conditions met out of 4 (should pass)"""
        result = apply_combination_rule('any_3', conditions_met_count=4, total_conditions=4)
        self.assertTrue(result)

    def test_all_with_all_true(self):
        """Test all rule with all conditions met"""
        result = apply_combination_rule('all', conditions_met_count=3, total_conditions=3)
        self.assertTrue(result)

    def test_all_with_one_false(self):
        """Test all rule with one condition not met (2/3)"""
        result = apply_combination_rule('all', conditions_met_count=2, total_conditions=3)
        self.assertFalse(result)

    def test_all_with_all_false(self):
        """Test all rule with no conditions met"""
        result = apply_combination_rule('all', conditions_met_count=0, total_conditions=3)
        self.assertFalse(result)

    def test_all_with_single_condition(self):
        """Test all rule with single condition (1/1)"""
        result = apply_combination_rule('all', conditions_met_count=1, total_conditions=1)
        self.assertTrue(result)

    def test_all_with_empty_conditions(self):
        """Test all rule with empty conditions (0/0)"""
        result = apply_combination_rule('all', conditions_met_count=0, total_conditions=0)
        self.assertTrue(result)  # Vacuous truth: all of zero conditions are met

    def test_invalid_combination_rule(self):
        """Test with invalid combination rule"""
        result = apply_combination_rule('some_invalid_rule', conditions_met_count=1, total_conditions=2)
        self.assertFalse(result)

    def test_combination_rules_edge_cases(self):
        """Test various edge cases for all combination rules"""
        test_cases = [
            # (rule, conditions_met, total, expected)
            ('any_1', 0, 0, False),
            ('any_2', 1, 1, False),
            ('any_3', 2, 2, False),
            ('all', 4, 4, True),
            ('any_1', 0, 1, False),
            ('any_2', 0, 2, False),
            ('any_1', 1, 5, True),
            ('any_2', 2, 5, True),
            ('any_3', 3, 5, True),
            ('all', 5, 5, True),
        ]

        for rule, met_count, total, expected in test_cases:
            with self.subTest(rule=rule, met=met_count, total=total):
                result = apply_combination_rule(rule, met_count, total)
                self.assertEqual(result, expected)


class TestRecommendations(unittest.TestCase):
    """Test recommendation generation"""

    def test_high_temperature_recommendation(self):
        """Test recommendation for high temperature"""
        conditions_met = [
            {
                'indicator': 'temp',
                'operator': '>',
                'threshold_value': 25.0,
                'actual_value': 28.0,
                'met': True
            }
        ]
        recommendations = get_trigger_recommendations(conditions_met)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any('temperature' in rec.lower() for rec in recommendations))
        self.assertTrue(any('28' in rec for rec in recommendations))

    def test_low_rainfall_recommendation(self):
        """Test recommendation for low rainfall"""
        conditions_met = [
            {
                'indicator': 'rainfall',
                'operator': '<',
                'threshold_value': 2.0,
                'actual_value': 1.2,
                'met': True
            }
        ]
        recommendations = get_trigger_recommendations(conditions_met)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any('rainfall' in rec.lower() for rec in recommendations))

    def test_low_humidity_recommendation(self):
        """Test recommendation for low humidity"""
        conditions_met = [
            {
                'indicator': 'humidity',
                'operator': '<',
                'threshold_value': 60.0,
                'actual_value': 45.0,
                'met': True
            }
        ]
        recommendations = get_trigger_recommendations(conditions_met)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any('humidity' in rec.lower() for rec in recommendations))

    def test_high_humidity_recommendation(self):
        """Test recommendation for high humidity"""
        conditions_met = [
            {
                'indicator': 'humidity',
                'operator': '>',
                'threshold_value': 80.0,
                'actual_value': 85.0,
                'met': True
            }
        ]
        recommendations = get_trigger_recommendations(conditions_met)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any('humidity' in rec.lower() for rec in recommendations))

    def test_high_wind_speed_recommendation(self):
        """Test recommendation for high wind speed"""
        conditions_met = [
            {
                'indicator': 'wind_speed',
                'operator': '>',
                'threshold_value': 20.0,
                'actual_value': 25.0,
                'met': True
            }
        ]
        recommendations = get_trigger_recommendations(conditions_met)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any('wind' in rec.lower() for rec in recommendations))

    def test_multiple_conditions_recommendations(self):
        """Test recommendations with multiple conditions met"""
        conditions_met = [
            {
                'indicator': 'temp',
                'operator': '>',
                'threshold_value': 25.0,
                'actual_value': 28.0,
                'met': True
            },
            {
                'indicator': 'rainfall',
                'operator': '<',
                'threshold_value': 2.0,
                'actual_value': 1.2,
                'met': True
            },
            {
                'indicator': 'humidity',
                'operator': '<',
                'threshold_value': 60.0,
                'actual_value': 55.0,
                'met': True
            }
        ]
        recommendations = get_trigger_recommendations(conditions_met)
        # Should have at least 3 individual recommendations + 1 multi-condition recommendation
        self.assertGreaterEqual(len(recommendations), 3)
        # Check for multi-condition warning
        self.assertTrue(any('Multiple drought indicators' in rec for rec in recommendations))

    def test_no_recommendations_for_unmet_conditions(self):
        """Test that unmet conditions don't generate recommendations"""
        conditions_met = [
            {
                'indicator': 'temp',
                'operator': '>',
                'threshold_value': 25.0,
                'actual_value': 22.0,
                'met': False
            }
        ]
        recommendations = get_trigger_recommendations(conditions_met)
        # Should be empty or only contain general recommendations
        self.assertEqual(len(recommendations), 0)

    def test_empty_conditions_list(self):
        """Test recommendations with empty conditions list"""
        recommendations = get_trigger_recommendations([])
        self.assertEqual(len(recommendations), 0)


class TestOperatorsAndIndicatorMaps(unittest.TestCase):
    """Test operator and indicator mappings"""

    def test_all_operators_defined(self):
        """Test that all expected operators are defined"""
        expected_operators = ['>', '<', '>=', '<=', '==']
        for op in expected_operators:
            self.assertIn(op, OPERATORS)

    def test_all_indicators_mapped(self):
        """Test that all indicators are properly mapped"""
        expected_indicators = ['temp', 'rainfall', 'humidity', 'wind_speed']
        for indicator in expected_indicators:
            self.assertIn(indicator, INDICATOR_MAP)

    def test_indicator_map_values(self):
        """Test that indicator map has correct values"""
        self.assertEqual(INDICATOR_MAP['temp'], 'temperature')
        self.assertEqual(INDICATOR_MAP['rainfall'], 'rainfall')
        self.assertEqual(INDICATOR_MAP['humidity'], 'humidity')
        self.assertEqual(INDICATOR_MAP['wind_speed'], 'wind_speed')


def run_tests_with_summary():
    """Run all tests and provide a detailed summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSingleConditionEvaluation))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestCombinationRules))
    suite.addTests(loader.loadTestsFromTestCase(TestRecommendations))
    suite.addTests(loader.loadTestsFromTestCase(TestOperatorsAndIndicatorMaps))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    if result.wasSuccessful():
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed. See details above.")
        return 1


if __name__ == '__main__':
    exit_code = run_tests_with_summary()
    exit(exit_code)
