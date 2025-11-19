"""
Test script for NIWA DataHub API integration
"""
import asyncio
import sys
import os

# Add parent directory to path to import drought_risk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from drought_risk import fetch_niwa_rainfall_data, calculate_drought_risk

async def test_niwa_api():
    """Test NIWA DataHub API connection"""
    print("=" * 60)
    print("NIWA DataHub API Test")
    print("=" * 60)

    print("\n1. Testing NIWA DataHub file listing...")
    try:
        niwa_data = await fetch_niwa_rainfall_data()

        if niwa_data:
            print(f"✅ NIWA API connection successful!")
            print(f"   Total files available: {niwa_data.get('total_files', 'Unknown')}")

            files = niwa_data.get('files', [])
            if files:
                print(f"   Rainfall files found: {len(files)}")
                print("\n   First 5 rainfall files:")
                for i, file in enumerate(files[:5], 1):
                    print(f"   {i}. {file.get('fileName', 'Unknown')} (ID: {file.get('id', 'Unknown')})")
            else:
                print("   No rainfall-specific files found in the first 50 files")
                print("   (This is normal - NIWA might use different file naming)")
        else:
            print("⚠️  NIWA API returned no data")
            print("   This could mean:")
            print("   - No files available in your account")
            print("   - API credentials need verification")

    except Exception as e:
        print(f"❌ NIWA API test failed: {e}")
        print("\n   Common issues:")
        print("   - Check NIWA_CUSTOMER_ID is correct")
        print("   - Check NIWA_API_KEY is valid")
        print("   - Ensure you have access to rainfall data products")

    print("\n" + "=" * 60)
    print("\n2. Testing full drought risk calculation (with NIWA integration)...")
    try:
        result = await calculate_drought_risk("Canterbury")
        print(f"✅ Drought risk calculated successfully!")
        print(f"   Location: {result.get('location')}")
        print(f"   Risk Level: {result.get('risk_level')}")
        print(f"   Risk Score: {result.get('risk_score')}/10")
        print(f"   NIWA Data Available: {result.get('factors', {}).get('niwa_data_available', False)}")
    except Exception as e:
        print(f"❌ Drought risk calculation failed: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_niwa_api())
