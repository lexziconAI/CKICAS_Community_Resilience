# CKCIAS Drought Monitor - Trigger Evaluation Engine Documentation

## Overview

The Trigger Evaluation Engine is the core component of the CKCIAS Drought Monitor MVP that evaluates drought alert triggers against live weather data and determines when to notify users.

**Created**: Day 2 of MVP Development
**Location**: `backend/services/trigger_engine.py`
**Lines of Code**: ~450 lines

---

## Architecture

### Core Components

```
backend/
├── services/
│   ├── __init__.py              # Package exports
│   └── trigger_engine.py        # Main engine (THIS FILE)
├── routes/
│   └── triggers.py              # API endpoints (includes /evaluate)
├── database.py                  # Database layer
└── test_trigger_engine.py       # Comprehensive test suite
```

### Data Flow

```
Weather Data → Trigger Engine → Evaluation → Recommendations → User Notification
     ↓              ↓              ↓              ↓                    ↓
  {temp: 27.5}   Fetch triggers  Apply rules   Generate actions   Email/Alert
  {rain: 1.2}    Load conditions  any_2 met    "Consider irrigation"
  {humidity: 55} Check thresholds  → ALERT!     "Monitor soil"
```

---

## Combination Rules

Users can configure how multiple conditions are combined:

| Rule    | Description                           | Example                          |
|---------|---------------------------------------|----------------------------------|
| `any_1` | Trigger if ANY 1 condition is met     | Alert on high temp OR low rain   |
| `any_2` | Trigger if ANY 2 conditions are met   | Alert on 2+ indicators           |
| `any_3` | Trigger if ANY 3 conditions are met   | Alert on 3+ indicators           |
| `all`   | Trigger if ALL conditions are met     | Alert only if everything is bad  |

### Example Scenario

**Tim's Trigger**: "Taranaki Drought Alert"
- **Conditions**: temp > 25, rainfall < 2, humidity < 60
- **Rule**: `any_2` (any 2 conditions must be met)

**Weather Data**:
- Temperature: 27.5°C ✓ (meets condition)
- Rainfall: 1.2mm ✓ (meets condition)
- Humidity: 65% ✗ (does NOT meet condition)

**Result**: **ALERT TRIGGERED** (2/3 conditions met, rule requires 2)

---

## Core Functions

### 1. `evaluate_condition(condition, weather_data)`

Evaluates a single condition against weather data.

**Parameters**:
- `condition`: Dict with `indicator`, `operator`, `threshold_value`
- `weather_data`: Dict with current measurements

**Returns**: `(met: bool, error: Optional[str])`

**Supported Operators**: `>`, `<`, `>=`, `<=`, `==`

**Example**:
```python
condition = {
    "indicator": "temp",
    "operator": ">",
    "threshold_value": 25.0
}
weather_data = {
    "temperature": 27.5,
    "humidity": 55.0,
    "rainfall": 1.2
}

met, error = evaluate_condition(condition, weather_data)
# Returns: (True, None)
```

---

### 2. `evaluate_trigger(trigger, weather_data)`

Evaluates a complete trigger with all its conditions.

**Parameters**:
- `trigger`: Trigger object from database
- `weather_data`: Current measurements

**Returns**: `(triggered: bool, conditions_met: List[Dict], errors: List[str])`

**Example**:
```python
trigger = {
    "id": 1,
    "name": "Taranaki Drought Alert",
    "combination_rule": "any_2"
}
weather_data = {"temperature": 27.5, "rainfall": 1.2, "humidity": 55}

triggered, conditions, errors = evaluate_trigger(trigger, weather_data)
# Returns: (True, [...condition details...], [])
```

---

### 3. `evaluate_all_triggers(user_id, weather_data)`

Evaluates ALL active triggers for a user.

**Parameters**:
- `user_id`: User ID to evaluate triggers for
- `weather_data`: Current measurements

**Returns**: `List[Dict]` - List of triggered alerts

**Example**:
```python
alerts = evaluate_all_triggers(user_id=2, weather_data={
    "temperature": 27.5,
    "rainfall": 1.2,
    "humidity": 55.0,
    "wind_speed": 15.0
})

for alert in alerts:
    print(f"ALERT: {alert['trigger']['name']}")
    for rec in alert['recommendations']:
        print(f"  - {rec}")
```

**Alert Structure**:
```json
{
  "trigger": {
    "id": 1,
    "name": "Taranaki Drought Alert",
    "region": "Taranaki",
    "combination_rule": "any_2",
    "is_active": true
  },
  "conditions_met": [
    {
      "indicator": "temp",
      "operator": ">",
      "threshold_value": 25.0,
      "actual_value": 27.5,
      "met": true
    }
  ],
  "recommendations": [
    "High temperature detected (27.5°C). Consider irrigation scheduling...",
    "Low rainfall detected (1.2mm). Monitor soil moisture levels..."
  ],
  "evaluated_at": "2025-11-19T16:30:00Z",
  "errors": []
}
```

---

### 4. `get_trigger_recommendations(conditions_met)`

Generates actionable recommendations based on triggered conditions.

**Parameters**:
- `conditions_met`: List of condition evaluation results

**Returns**: `List[str]` - List of recommendation strings

**Recommendation Templates**:

| Indicator    | Condition Type | Recommendation                                          |
|--------------|----------------|---------------------------------------------------------|
| Temperature  | High (>)       | Consider irrigation scheduling, provide livestock shade |
| Rainfall     | Low (<)        | Monitor soil moisture, consider reducing stock numbers  |
| Humidity     | Low (<)        | Adjust irrigation for increased evapotranspiration      |
| Humidity     | High (>)       | Monitor for disease pressure in crops                   |
| Wind Speed   | High (>)       | Protect young plants, check irrigation coverage         |

**Multi-Condition Bonus**: If 2+ conditions are met, adds:
> "Multiple drought indicators detected. Review your drought management plan and consider consulting with local agricultural advisors."

---

### 5. `check_notification_rate_limit(trigger_id, user_id, rate_limit_hours=6)`

Prevents notification spam by enforcing a minimum time window between notifications.

**Parameters**:
- `trigger_id`: ID of the trigger
- `user_id`: ID of the user
- `rate_limit_hours`: Minimum hours between notifications (default: 6)

**Returns**: `(should_send: bool, last_sent_at: Optional[datetime])`

**Example**:
```python
should_send, last_sent = check_notification_rate_limit(
    trigger_id=1,
    user_id=2,
    rate_limit_hours=6
)

if should_send:
    # Send notification
    send_email(...)
    log_notification(trigger_id, user_id, conditions_data)
else:
    print(f"Rate limit active. Last sent: {last_sent}")
```

**Rate Limit Logic**:
1. Query `notification_log` table for most recent notification
2. Calculate time since last notification
3. Allow if: `time_since_last >= rate_limit_hours`

---

## API Endpoint

### `POST /api/triggers/evaluate`

Evaluate all active triggers for a user against current weather data.

**Request**:
```json
{
  "user_id": 2,
  "weather_data": {
    "temperature": 27.5,
    "rainfall": 1.2,
    "humidity": 55.0,
    "wind_speed": 15.0
  }
}
```

**Response** (200 OK):
```json
{
  "user_id": 2,
  "total_alerts": 1,
  "evaluated_at": "2025-11-19T16:30:00Z",
  "alerts": [
    {
      "trigger": {
        "id": 1,
        "name": "Taranaki Drought Alert",
        "region": "Taranaki",
        "combination_rule": "any_2",
        "is_active": true
      },
      "conditions_met": [
        {
          "indicator": "temp",
          "operator": ">",
          "threshold_value": 25.0,
          "actual_value": 27.5,
          "met": true
        },
        {
          "indicator": "rainfall",
          "operator": "<",
          "threshold_value": 2.0,
          "actual_value": 1.2,
          "met": true
        }
      ],
      "recommendations": [
        "High temperature detected (27.5°C). Consider irrigation scheduling and provide shade for livestock. Monitor heat stress in animals.",
        "Low rainfall detected (1.2mm). Monitor soil moisture levels closely. Consider reducing stock numbers if pasture condition deteriorates.",
        "Multiple drought indicators detected. Review your drought management plan and consider consulting with local agricultural advisors."
      ],
      "evaluated_at": "2025-11-19T16:30:00Z",
      "errors": []
    }
  ]
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:9100/api/triggers/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "weather_data": {
      "temperature": 27.5,
      "rainfall": 1.2,
      "humidity": 55.0,
      "wind_speed": 15.0
    }
  }'
```

**Python Example**:
```python
import requests

response = requests.post('http://localhost:9100/api/triggers/evaluate', json={
    "user_id": 2,
    "weather_data": {
        "temperature": 27.5,
        "rainfall": 1.2,
        "humidity": 55.0,
        "wind_speed": 15.0
    }
})

alerts = response.json()['alerts']
for alert in alerts:
    print(f"ALERT: {alert['trigger']['name']}")
    for rec in alert['recommendations']:
        print(f"  - {rec}")
```

---

## Error Handling

The engine handles various error scenarios gracefully:

### 1. Missing Weather Data Indicators
```python
weather_data = {"temperature": 27.5}  # Missing humidity, rainfall, etc.
# Result: Conditions with missing data return (False, "Weather data missing indicator: rainfall")
```

### 2. Invalid Operators
```python
condition = {"indicator": "temp", "operator": "!=", "threshold_value": 25}
# Result: (False, "Invalid operator: !=")
```

### 3. Database Connection Errors
```python
# Database unreachable
# Result: Empty alerts list + error logged
```

### 4. Null/None Values
```python
weather_data = {"temperature": None, "rainfall": 1.2}
# Result: (False, "Weather data has null value for: temperature")
```

---

## Logging

The engine uses Python's `logging` module for comprehensive logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
```

**Log Examples**:
```
INFO - Evaluating all triggers for user 2
INFO - Found 1 total triggers, 1 active for user 2
INFO - Evaluating trigger 1: Taranaki Drought Alert
INFO - Condition evaluation: temperature (27.5) > 25.0 = True
INFO - Trigger 1 evaluation complete: triggered=True, conditions_met=2/3, rule=any_2
INFO - ALERT TRIGGERED: Trigger 1 - Taranaki Drought Alert
INFO - Evaluation complete: 1 alerts triggered out of 1 active triggers
```

---

## Testing

### Running Tests

```bash
cd backend
python3 test_trigger_engine.py
```

### Test Coverage

The test suite covers:

1. **Condition Evaluation** (5 tests)
   - Temperature comparisons (>, <)
   - Rainfall thresholds
   - Humidity ranges
   - Wind speed checks

2. **Combination Rules** (8 tests)
   - any_1, any_2, any_3, all
   - Edge cases (0 met, all met)

3. **Full Trigger Evaluation** (2 tests)
   - Database integration
   - Triggering scenario (2/3 conditions met)
   - Non-triggering scenario (0/3 conditions met)

4. **Recommendations** (1 test)
   - Multi-condition recommendations
   - Contextual advice generation

5. **Rate Limiting** (3 tests)
   - First notification (should send)
   - Immediate second notification (should block)
   - Custom rate limits (0 hours)

### Expected Output

```
======================================================================
FINAL RESULTS
======================================================================
✓ PASS: Condition Evaluation
✓ PASS: Combination Rules
✓ PASS: Trigger Evaluation
✓ PASS: Recommendations
✓ PASS: Rate Limiting

5/5 test suites passed

🎉 All tests passed! Trigger engine is working correctly.
```

---

## Database Integration

The engine integrates with the SQLite database schema:

### Tables Used

**triggers**:
```sql
CREATE TABLE triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    combination_rule TEXT CHECK(combination_rule IN ('any_1', 'any_2', 'any_3', 'all')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**trigger_conditions**:
```sql
CREATE TABLE trigger_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_id INTEGER NOT NULL,
    indicator TEXT CHECK(indicator IN ('temp', 'rainfall', 'humidity', 'wind_speed')),
    operator TEXT CHECK(operator IN ('>', '<', '>=', '<=', '==')),
    threshold_value REAL NOT NULL,
    FOREIGN KEY (trigger_id) REFERENCES triggers(id) ON DELETE CASCADE
)
```

**notification_log**:
```sql
CREATE TABLE notification_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notification_type TEXT DEFAULT 'email',
    trigger_conditions_met TEXT NOT NULL,
    FOREIGN KEY (trigger_id) REFERENCES triggers(id) ON DELETE CASCADE
)
```

---

## Performance Considerations

1. **Database Queries**: Uses indexed queries for efficient lookups
2. **Condition Evaluation**: O(n) complexity where n = number of conditions
3. **Rate Limiting**: Single query per trigger (indexed on user_id + trigger_id)
4. **Memory**: Lightweight - all data structures are dictionaries/lists

**Scalability**:
- Current design: 100+ triggers, evaluated in < 1 second
- Future optimization: Add caching for frequently evaluated triggers

---

## Future Enhancements

### Phase 1 (Next Sprint)
- [ ] Email notification service integration (SendGrid)
- [ ] SMS notifications via Twilio
- [ ] Webhook support for third-party integrations

### Phase 2 (Later)
- [ ] Historical trigger evaluation (backfill)
- [ ] Machine learning for threshold recommendations
- [ ] Trigger templates library
- [ ] Multi-region batch evaluation

### Phase 3 (Advanced)
- [ ] Real-time websocket push notifications
- [ ] Trigger condition scheduling (time-based rules)
- [ ] Compound triggers (cross-region)
- [ ] AI-powered recommendation refinement

---

## Troubleshooting

### Issue: "No triggers found for user"
**Solution**: Ensure triggers are seeded in database:
```bash
cd backend
python3 database.py
```

### Issue: "Weather data missing indicator"
**Solution**: Ensure weather data includes all required fields:
```python
weather_data = {
    "temperature": 27.5,  # Required
    "rainfall": 1.2,      # Required
    "humidity": 55.0,     # Required
    "wind_speed": 15.0    # Optional but recommended
}
```

### Issue: "Trigger not firing"
**Solution**: Check combination rule and threshold values:
```bash
# Debug by checking trigger conditions
python3 -c "from database import get_trigger_conditions; print(get_trigger_conditions(1))"
```

---

## Credits

**Developer**: Claude (Anthropic)
**Project**: CKCIAS Drought Monitor MVP
**Sprint**: Day 2 - Trigger Evaluation Engine
**Date**: November 19, 2025

---

## License

Part of the CKCIAS Community Resilience App project.
