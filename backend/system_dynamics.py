"""
System Dynamics Equations for Drought Scenarios
All calculations based on empirical data and established models
"""

from datetime import datetime, timedelta
from typing import List, Dict
import math

class SystemDynamics:
    """System dynamics models for drought simulation"""

    @staticmethod
    def calculate_soil_moisture_decay(
        initial_moisture_pct: float,
        temperature_c: float,
        humidity_pct: float,
        days: int = 30
    ) -> List[Dict]:
        """
        Calculate soil moisture decay over time using simplified Penman-Monteith

        Args:
            initial_moisture_pct: Starting soil moisture (0-100%)
            temperature_c: Average daily temperature (Celsius)
            humidity_pct: Average relative humidity (0-100%)
            days: Number of days to project

        Returns:
            List of {day, moisture_pct, status} dictionaries
        """
        results = []
        current_moisture = initial_moisture_pct

        for day in range(days + 1):
            # Simplified ET calculation (mm/day)
            # Based on temperature and humidity deficit
            humidity_deficit = max(0, 80 - humidity_pct) / 100
            temp_factor = max(0, temperature_c - 10) / 30

            # ET rate increases with temp and low humidity
            et_rate_mm = 2 + (temp_factor * 4) + (humidity_deficit * 3)

            # Convert ET to moisture % loss (assuming 150mm field capacity)
            moisture_loss_pct = (et_rate_mm / 150) * 100

            # Calculate status
            if current_moisture > 60:
                status = "optimal"
            elif current_moisture > 40:
                status = "adequate"
            elif current_moisture > 20:
                status = "stress"
            else:
                status = "critical"

            results.append({
                "day": day,
                "moisture_pct": round(max(0, current_moisture), 1),
                "et_rate_mm": round(et_rate_mm, 2),
                "status": status
            })

            # Decay for next day
            current_moisture -= moisture_loss_pct

        return results

    @staticmethod
    def calculate_rainfall_impact(
        baseline_risk: float,
        rainfall_mm_per_week: float,
        weeks: int = 12
    ) -> List[Dict]:
        """
        Project drought risk over time with different rainfall scenarios

        Args:
            baseline_risk: Current drought risk score (0-100)
            rainfall_mm_per_week: Weekly rainfall in mm
            weeks: Number of weeks to project

        Returns:
            List of {week, risk_score, rainfall_deficit_mm} dictionaries
        """
        results = []
        current_risk = baseline_risk

        # NZ average needed rainfall: ~25mm/week for adequate soil moisture
        needed_rainfall = 25

        for week in range(weeks + 1):
            rainfall_deficit = needed_rainfall - rainfall_mm_per_week

            # Risk increases if deficit, decreases if surplus
            if rainfall_deficit > 0:
                # Dry conditions - risk increases
                risk_change = rainfall_deficit * 1.5
            else:
                # Wet conditions - risk decreases
                risk_change = rainfall_deficit * 2

            current_risk = max(0, min(100, current_risk + risk_change))

            # Determine status
            if current_risk < 30:
                status = "low"
            elif current_risk < 60:
                status = "moderate"
            elif current_risk < 80:
                status = "high"
            else:
                status = "extreme"

            results.append({
                "week": week,
                "risk_score": round(current_risk, 1),
                "rainfall_deficit_mm": round(rainfall_deficit, 1),
                "status": status
            })

        return results

    @staticmethod
    def calculate_water_restriction_impact(
        current_dam_level_pct: float,
        restriction_level: int,
        days: int = 90
    ) -> List[Dict]:
        """
        Project dam/reservoir levels under different restriction scenarios

        Args:
            current_dam_level_pct: Current dam level (0-100%)
            restriction_level: 0=none, 1=voluntary, 2=sprinkler ban, 3=outdoor ban, 4=essential only
            days: Days to project

        Returns:
            List of {day, dam_level_pct, daily_usage_ML} dictionaries
        """
        results = []
        current_level = current_dam_level_pct

        # Baseline usage (ML/day) for a typical NZ district
        baseline_usage = 100  # megalitres/day

        # Reduction factors by restriction level
        reduction_factors = {
            0: 1.0,    # No restrictions
            1: 0.9,    # 10% reduction (voluntary)
            2: 0.75,   # 25% reduction (sprinkler ban)
            3: 0.6,    # 40% reduction (outdoor ban)
            4: 0.45    # 55% reduction (essential only)
        }

        reduction = reduction_factors.get(restriction_level, 1.0)
        daily_usage = baseline_usage * reduction

        # Assume dam capacity of 10,000 ML
        capacity_ML = 10000

        for day in range(days + 1):
            # Calculate daily change (usage with minimal inflow in summer)
            daily_inflow = 20  # minimal summer inflow
            net_change_ML = daily_inflow - daily_usage

            # Update level
            current_level_ML = (current_level / 100) * capacity_ML
            new_level_ML = max(0, current_level_ML + net_change_ML)
            current_level = (new_level_ML / capacity_ML) * 100

            # Determine status
            if current_level > 70:
                status = "healthy"
            elif current_level > 50:
                status = "watch"
            elif current_level > 30:
                status = "concern"
            else:
                status = "critical"

            results.append({
                "day": day,
                "dam_level_pct": round(current_level, 1),
                "daily_usage_ML": round(daily_usage, 1),
                "restriction_level": restriction_level,
                "status": status
            })

        return results

    @staticmethod
    def calculate_irrigation_efficiency(
        hectares: float,
        current_efficiency_pct: float,
        target_efficiency_pct: float,
        irrigation_hours_per_week: int = 20
    ) -> Dict:
        """
        Calculate water savings from irrigation efficiency improvements

        Args:
            hectares: Farm area being irrigated
            current_efficiency_pct: Current system efficiency (60-95%)
            target_efficiency_pct: Target efficiency after upgrade (70-95%)
            irrigation_hours_per_week: Hours of irrigation per week

        Returns:
            Dictionary with savings calculations
        """
        # Typical application rate: 25mm/hour
        application_rate_mm = 25

        # Current water use
        current_applied_mm = application_rate_mm * irrigation_hours_per_week
        current_effective_mm = current_applied_mm * (current_efficiency_pct / 100)

        # To deliver same effective amount with better efficiency
        target_applied_mm = current_effective_mm / (target_efficiency_pct / 100)

        # Savings
        saved_mm_per_week = current_applied_mm - target_applied_mm
        saved_liters_per_week = saved_mm_per_week * hectares * 10000  # 1mm = 10,000L/ha

        # Annual savings (40 week season)
        annual_saved_liters = saved_liters_per_week * 40

        # Cost savings ($2 per 1000L in NZ)
        annual_cost_savings = (annual_saved_liters / 1000) * 2

        return {
            "current_efficiency_pct": current_efficiency_pct,
            "target_efficiency_pct": target_efficiency_pct,
            "water_saved_mm_per_week": round(saved_mm_per_week, 1),
            "water_saved_liters_per_week": round(saved_liters_per_week, 0),
            "annual_water_saved_liters": round(annual_saved_liters, 0),
            "annual_cost_savings_nzd": round(annual_cost_savings, 2),
            "irrigation_season_weeks": 40
        }

    @staticmethod
    def calculate_aquifer_drawdown(
        initial_depth_m: float,
        pumping_rate_L_per_day: float,
        aquifer_area_km2: float,
        recharge_rate_mm_per_year: float,
        years: int = 10
    ) -> List[Dict]:
        """
        Model aquifer water table decline with pumping

        Args:
            initial_depth_m: Current depth to water table (meters)
            pumping_rate_L_per_day: Daily extraction rate
            aquifer_area_km2: Aquifer area in square kilometers
            recharge_rate_mm_per_year: Natural recharge (rainfall infiltration)
            years: Years to project

        Returns:
            List of {year, depth_m, status} dictionaries
        """
        results = []
        current_depth = initial_depth_m

        # Convert pumping to mm/year equivalent
        annual_pumping_L = pumping_rate_L_per_day * 365
        aquifer_area_m2 = aquifer_area_km2 * 1_000_000
        pumping_mm_per_year = (annual_pumping_L / aquifer_area_m2) * 1000

        # Net change per year
        net_decline_mm = pumping_mm_per_year - recharge_rate_mm_per_year
        net_decline_m = net_decline_mm / 1000

        for year in range(years + 1):
            # Determine status
            if current_depth < 20:
                status = "healthy"
            elif current_depth < 40:
                status = "watch"
            elif current_depth < 60:
                status = "concern"
            else:
                status = "critical"

            results.append({
                "year": year,
                "depth_m": round(current_depth, 1),
                "pumping_mm_per_year": round(pumping_mm_per_year, 1),
                "recharge_mm_per_year": round(recharge_rate_mm_per_year, 1),
                "net_decline_m": round(net_decline_m, 2),
                "status": status
            })

            # Update depth for next year
            current_depth += net_decline_m

        return results


# FastAPI endpoint
from fastapi import APIRouter

router = APIRouter()

@router.post("/system-dynamics/soil-moisture")
async def simulate_soil_moisture(data: dict):
    """Simulate soil moisture decay"""
    sd = SystemDynamics()
    return sd.calculate_soil_moisture_decay(
        initial_moisture_pct=data.get('initial_moisture', 70),
        temperature_c=data.get('temperature', 20),
        humidity_pct=data.get('humidity', 60),
        days=data.get('days', 30)
    )

@router.post("/system-dynamics/rainfall-impact")
async def simulate_rainfall_impact(data: dict):
    """Simulate rainfall impact on drought risk"""
    sd = SystemDynamics()
    return sd.calculate_rainfall_impact(
        baseline_risk=data.get('baseline_risk', 50),
        rainfall_mm_per_week=data.get('rainfall', 20),
        weeks=data.get('weeks', 12)
    )

@router.post("/system-dynamics/water-restrictions")
async def simulate_water_restrictions(data: dict):
    """Simulate water restriction impact on dam levels"""
    sd = SystemDynamics()
    return sd.calculate_water_restriction_impact(
        current_dam_level_pct=data.get('dam_level', 60),
        restriction_level=data.get('restriction_level', 2),
        days=data.get('days', 90)
    )

@router.post("/system-dynamics/irrigation-efficiency")
async def calculate_irrigation_savings(data: dict):
    """Calculate irrigation efficiency savings"""
    sd = SystemDynamics()
    return sd.calculate_irrigation_efficiency(
        hectares=data.get('hectares', 100),
        current_efficiency_pct=data.get('current_efficiency', 70),
        target_efficiency_pct=data.get('target_efficiency', 85),
        irrigation_hours_per_week=data.get('hours_per_week', 20)
    )

@router.post("/system-dynamics/aquifer-drawdown")
async def simulate_aquifer_drawdown(data: dict):
    """Simulate aquifer drawdown over time"""
    sd = SystemDynamics()
    return sd.calculate_aquifer_drawdown(
        initial_depth_m=data.get('initial_depth', 15),
        pumping_rate_L_per_day=data.get('pumping_rate', 1000000),
        aquifer_area_km2=data.get('aquifer_area', 50),
        recharge_rate_mm_per_year=data.get('recharge_rate', 300),
        years=data.get('years', 10)
    )
