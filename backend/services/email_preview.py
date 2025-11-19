"""
Email Template Preview Generator
Generates a preview of the drought alert email HTML for testing/review
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from email_service import (
    get_email_template,
    format_conditions_table,
    get_recommendations_html
)
from datetime import datetime


def generate_preview():
    """
    Generates a complete email preview with sample data.
    """
    # Sample conditions
    sample_conditions = [
        {
            "indicator": "temp",
            "operator": ">",
            "threshold": 25.0,
            "actual_value": 28.5
        },
        {
            "indicator": "rainfall",
            "operator": "<",
            "threshold": 2.0,
            "actual_value": 0.8
        },
        {
            "indicator": "humidity",
            "operator": "<",
            "threshold": 60.0,
            "actual_value": 45.0
        }
    ]

    # Get template
    template = get_email_template()

    # Generate components
    conditions_table = format_conditions_table(sample_conditions)
    recommendations = get_recommendations_html(sample_conditions)

    # Replace placeholders
    html = template.replace("{{USER_NAME}}", "Tim House")
    html = html.replace("{{TRIGGER_NAME}}", "Taranaki Drought Alert")
    html = html.replace("{{REGION}}", "Taranaki")
    html = html.replace("{{CONDITIONS_TABLE}}", conditions_table)
    html = html.replace("{{RECOMMENDATIONS}}", recommendations)
    html = html.replace("{{TIMESTAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S NZDT"))

    return html


def save_preview():
    """
    Saves the email preview to an HTML file for viewing in browser.
    """
    html = generate_preview()

    output_path = os.path.join(os.path.dirname(__file__), "email_preview.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Email preview saved to: {output_path}")
    print(f"   Open this file in your browser to see the email design!")

    return output_path


if __name__ == "__main__":
    save_preview()
