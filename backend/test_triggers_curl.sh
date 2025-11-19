#!/bin/bash
#
# CKCIAS Triggers API - Curl Test Script
# Manual testing of all CRUD endpoints
#

BASE_URL="http://localhost:9100/api/triggers"
USER_ID=2

echo "=========================================================================="
echo "  CKCIAS TRIGGERS API - CURL TESTS"
echo "=========================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Testing server connectivity...${NC}"
curl -s http://localhost:9100/health | jq '.'
echo ""

# TEST 1: Create a trigger
echo "=========================================================================="
echo -e "${BLUE}TEST 1: POST /api/triggers - Create Trigger${NC}"
echo "=========================================================================="
echo ""

TRIGGER_RESPONSE=$(curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "name": "Curl Test Drought Alert",
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
    "is_active": true
  }')

echo "$TRIGGER_RESPONSE" | jq '.'
TRIGGER_ID=$(echo "$TRIGGER_RESPONSE" | jq -r '.id')

if [ "$TRIGGER_ID" != "null" ] && [ -n "$TRIGGER_ID" ]; then
    echo -e "${GREEN}✓ Trigger created with ID: $TRIGGER_ID${NC}"
else
    echo -e "${RED}✗ Failed to create trigger${NC}"
    exit 1
fi

echo ""
read -p "Press Enter to continue..."

# TEST 2: List all triggers for user
echo ""
echo "=========================================================================="
echo -e "${BLUE}TEST 2: GET /api/triggers?user_id=$USER_ID - List Triggers${NC}"
echo "=========================================================================="
echo ""

curl -s -X GET "$BASE_URL?user_id=$USER_ID" | jq '.'
echo -e "${GREEN}✓ Listed all triggers for user $USER_ID${NC}"
echo ""
read -p "Press Enter to continue..."

# TEST 3: Get specific trigger
echo ""
echo "=========================================================================="
echo -e "${BLUE}TEST 3: GET /api/triggers/$TRIGGER_ID - Get Specific Trigger${NC}"
echo "=========================================================================="
echo ""

curl -s -X GET "$BASE_URL/$TRIGGER_ID" | jq '.'
echo -e "${GREEN}✓ Retrieved trigger ID: $TRIGGER_ID${NC}"
echo ""
read -p "Press Enter to continue..."

# TEST 4: Update trigger
echo ""
echo "=========================================================================="
echo -e "${BLUE}TEST 4: PUT /api/triggers/$TRIGGER_ID - Update Trigger${NC}"
echo "=========================================================================="
echo ""

curl -s -X PUT "$BASE_URL/$TRIGGER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Curl Test - UPDATED",
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
  }' | jq '.'

echo -e "${GREEN}✓ Updated trigger ID: $TRIGGER_ID${NC}"
echo ""
read -p "Press Enter to continue..."

# TEST 5: Toggle trigger
echo ""
echo "=========================================================================="
echo -e "${BLUE}TEST 5: POST /api/triggers/$TRIGGER_ID/toggle - Toggle Trigger${NC}"
echo "=========================================================================="
echo ""

echo "Before toggle:"
curl -s -X GET "$BASE_URL/$TRIGGER_ID" | jq '.is_active'

echo ""
echo "Toggling..."
curl -s -X POST "$BASE_URL/$TRIGGER_ID/toggle" | jq '.'

echo -e "${GREEN}✓ Toggled trigger ID: $TRIGGER_ID${NC}"
echo ""
read -p "Press Enter to continue..."

# TEST 6: Delete trigger
echo ""
echo "=========================================================================="
echo -e "${BLUE}TEST 6: DELETE /api/triggers/$TRIGGER_ID - Delete Trigger${NC}"
echo "=========================================================================="
echo ""

curl -s -X DELETE "$BASE_URL/$TRIGGER_ID" | jq '.'
echo -e "${GREEN}✓ Deleted trigger ID: $TRIGGER_ID${NC}"

# Verify deletion
echo ""
echo "Verifying deletion (should return 404):"
curl -s -X GET "$BASE_URL/$TRIGGER_ID" | jq '.'
echo ""

# ERROR HANDLING TESTS
echo ""
echo "=========================================================================="
echo -e "${BLUE}TEST 7: Error Handling${NC}"
echo "=========================================================================="
echo ""

echo "7a. Get non-existent trigger (should return 404):"
curl -s -X GET "$BASE_URL/99999" | jq '.'
echo ""

echo "7b. Invalid indicator (should return 422):"
curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "name": "Invalid",
    "region": "Test",
    "conditions": [{"indicator": "invalid", "operator": ">", "threshold": 25}],
    "combination_rule": "any_1"
  }' | jq '.'
echo ""

echo "7c. Invalid combination rule (should return 422):"
curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "name": "Invalid",
    "region": "Test",
    "conditions": [{"indicator": "temp", "operator": ">", "threshold": 25}],
    "combination_rule": "invalid_rule"
  }' | jq '.'
echo ""

echo "=========================================================================="
echo -e "${GREEN}✓ ALL TESTS COMPLETED${NC}"
echo "=========================================================================="
