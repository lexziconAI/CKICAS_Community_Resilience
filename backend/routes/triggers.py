"""
CKCIAS Drought Monitor - Trigger Management API
CRUD operations for drought triggers
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import sqlite3
import json

from config import DATABASE_PATH, AVAILABLE_INDICATORS, COMBINATION_RULES

router = APIRouter(prefix="/triggers", tags=["triggers"])


# Pydantic Models
class TriggerCondition(BaseModel):
    """Individual condition within a trigger"""
    indicator: str = Field(..., description="Indicator key (temp, rainfall, humidity, wind_speed)")
    operator: str = Field(..., description="Comparison operator (>, <, >=, <=, ==)")
    threshold: float = Field(..., description="Threshold value")

    @validator('indicator')
    def validate_indicator(cls, v):
        if v not in AVAILABLE_INDICATORS:
            raise ValueError(f"Invalid indicator. Must be one of: {list(AVAILABLE_INDICATORS.keys())}")
        return v

    @validator('operator')
    def validate_operator(cls, v):
        valid_operators = ['>', '<', '>=', '<=', '==']
        if v not in valid_operators:
            raise ValueError(f"Invalid operator. Must be one of: {valid_operators}")
        return v


class TriggerCreate(BaseModel):
    """Request model for creating a trigger"""
    user_id: int = Field(..., description="User ID who owns the trigger")
    name: str = Field(..., min_length=1, max_length=100, description="Trigger name")
    region: str = Field(..., min_length=1, max_length=100, description="Region to monitor")
    conditions: List[TriggerCondition] = Field(..., min_items=1, description="List of conditions")
    combination_rule: str = Field(..., description="How to combine conditions")
    is_active: bool = Field(default=True, description="Whether trigger is active")

    @validator('combination_rule')
    def validate_combination_rule(cls, v):
        if v not in COMBINATION_RULES:
            raise ValueError(f"Invalid combination rule. Must be one of: {COMBINATION_RULES}")
        return v


class TriggerUpdate(BaseModel):
    """Request model for updating a trigger"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    region: Optional[str] = Field(None, min_length=1, max_length=100)
    conditions: Optional[List[TriggerCondition]] = Field(None, min_items=1)
    combination_rule: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('combination_rule')
    def validate_combination_rule(cls, v):
        if v is not None and v not in COMBINATION_RULES:
            raise ValueError(f"Invalid combination rule. Must be one of: {COMBINATION_RULES}")
        return v


class TriggerResponse(BaseModel):
    """Response model for a trigger"""
    id: int
    user_id: int
    name: str
    region: str
    conditions: List[Dict[str, Any]]
    combination_rule: str
    is_active: bool
    created_at: str
    updated_at: str


class TriggerListResponse(BaseModel):
    """Response model for list of triggers"""
    triggers: List[TriggerResponse]
    total: int


# Database Helper Functions
def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_triggers_table():
    """Initialize triggers table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            conditions TEXT NOT NULL,
            combination_rule TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# Initialize table on module import
init_triggers_table()


# API Endpoints
@router.get("", response_model=TriggerListResponse)
async def list_triggers(user_id: int = Query(..., description="User ID to filter triggers")):
    """
    Get all triggers for a specific user

    - **user_id**: The ID of the user whose triggers to retrieve
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, user_id, name, region, conditions, combination_rule,
                   is_active, created_at, updated_at
            FROM triggers
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        rows = cursor.fetchall()
        conn.close()

        triggers = []
        for row in rows:
            triggers.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "name": row["name"],
                "region": row["region"],
                "conditions": json.loads(row["conditions"]),
                "combination_rule": row["combination_rule"],
                "is_active": bool(row["is_active"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })

        return TriggerListResponse(triggers=triggers, total=len(triggers))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("", response_model=TriggerResponse, status_code=201)
async def create_trigger(trigger: TriggerCreate):
    """
    Create a new drought trigger

    - **user_id**: User ID who owns this trigger
    - **name**: Descriptive name for the trigger
    - **region**: Geographic region to monitor
    - **conditions**: List of conditions (indicator, operator, threshold)
    - **combination_rule**: How to combine conditions (any_1, any_2, any_3, all)
    - **is_active**: Whether the trigger is active (default: true)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Convert conditions to JSON
        conditions_json = json.dumps([c.dict() for c in trigger.conditions])

        cursor.execute(
            """
            INSERT INTO triggers (user_id, name, region, conditions, combination_rule, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                trigger.user_id,
                trigger.name,
                trigger.region,
                conditions_json,
                trigger.combination_rule,
                trigger.is_active
            )
        )

        trigger_id = cursor.lastrowid
        conn.commit()

        # Fetch the created trigger
        cursor.execute(
            """
            SELECT id, user_id, name, region, conditions, combination_rule,
                   is_active, created_at, updated_at
            FROM triggers
            WHERE id = ?
            """,
            (trigger_id,)
        )

        row = cursor.fetchone()
        conn.close()

        return TriggerResponse(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            region=row["region"],
            conditions=json.loads(row["conditions"]),
            combination_rule=row["combination_rule"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Database constraint violation: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{trigger_id}", response_model=TriggerResponse)
async def get_trigger(trigger_id: int):
    """
    Get a specific trigger by ID

    - **trigger_id**: The ID of the trigger to retrieve
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, user_id, name, region, conditions, combination_rule,
                   is_active, created_at, updated_at
            FROM triggers
            WHERE id = ?
            """,
            (trigger_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")

        return TriggerResponse(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            region=row["region"],
            conditions=json.loads(row["conditions"]),
            combination_rule=row["combination_rule"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/{trigger_id}", response_model=TriggerResponse)
async def update_trigger(trigger_id: int, trigger_update: TriggerUpdate):
    """
    Update an existing trigger

    - **trigger_id**: The ID of the trigger to update
    - **name**: New name (optional)
    - **region**: New region (optional)
    - **conditions**: New conditions list (optional)
    - **combination_rule**: New combination rule (optional)
    - **is_active**: New active status (optional)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if trigger exists
        cursor.execute("SELECT id FROM triggers WHERE id = ?", (trigger_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")

        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []

        if trigger_update.name is not None:
            update_fields.append("name = ?")
            update_values.append(trigger_update.name)

        if trigger_update.region is not None:
            update_fields.append("region = ?")
            update_values.append(trigger_update.region)

        if trigger_update.conditions is not None:
            update_fields.append("conditions = ?")
            update_values.append(json.dumps([c.dict() for c in trigger_update.conditions]))

        if trigger_update.combination_rule is not None:
            update_fields.append("combination_rule = ?")
            update_values.append(trigger_update.combination_rule)

        if trigger_update.is_active is not None:
            update_fields.append("is_active = ?")
            update_values.append(trigger_update.is_active)

        if not update_fields:
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")

        # Always update the updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_values.append(trigger_id)

        query = f"UPDATE triggers SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        conn.commit()

        # Fetch updated trigger
        cursor.execute(
            """
            SELECT id, user_id, name, region, conditions, combination_rule,
                   is_active, created_at, updated_at
            FROM triggers
            WHERE id = ?
            """,
            (trigger_id,)
        )

        row = cursor.fetchone()
        conn.close()

        return TriggerResponse(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            region=row["region"],
            conditions=json.loads(row["conditions"]),
            combination_rule=row["combination_rule"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/{trigger_id}", status_code=200)
async def delete_trigger(trigger_id: int):
    """
    Delete a trigger

    - **trigger_id**: The ID of the trigger to delete
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if trigger exists
        cursor.execute("SELECT id, name FROM triggers WHERE id = ?", (trigger_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")

        trigger_name = row["name"]

        # Delete the trigger
        cursor.execute("DELETE FROM triggers WHERE id = ?", (trigger_id,))
        conn.commit()
        conn.close()

        return {
            "message": f"Trigger '{trigger_name}' deleted successfully",
            "trigger_id": trigger_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/{trigger_id}/toggle", response_model=TriggerResponse)
async def toggle_trigger(trigger_id: int):
    """
    Toggle the active status of a trigger

    - **trigger_id**: The ID of the trigger to toggle
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if trigger exists and get current status
        cursor.execute("SELECT is_active FROM triggers WHERE id = ?", (trigger_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")

        current_status = bool(row["is_active"])
        new_status = not current_status

        # Update the status
        cursor.execute(
            """
            UPDATE triggers
            SET is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_status, trigger_id)
        )
        conn.commit()

        # Fetch updated trigger
        cursor.execute(
            """
            SELECT id, user_id, name, region, conditions, combination_rule,
                   is_active, created_at, updated_at
            FROM triggers
            WHERE id = ?
            """,
            (trigger_id,)
        )

        row = cursor.fetchone()
        conn.close()

        return TriggerResponse(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            region=row["region"],
            conditions=json.loads(row["conditions"]),
            combination_rule=row["combination_rule"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
