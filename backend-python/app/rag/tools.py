from datetime import datetime
from typing import Optional
from llama_index.core.tools import FunctionTool

def calculate_employment_duration(start_date_str: str, end_date_str: str = "Present") -> str:
    """
    Calculates the duration between two dates in years and months.
    Args:
        start_date_str: Start date in format 'YYYY-MM-DD' or 'YYYY-MM' or 'YYYY'.
        end_date_str: End date in format 'YYYY-MM-DD', 'YYYY-MM', 'YYYY', or 'Present'.
    Returns:
        String describing the duration, e.g., "2 years and 3 months".
    """
    try:
        # Normalize "Present" to today
        if end_date_str.lower() == "present":
            end_date = datetime.now()
        else:
            end_date = _parse_date(end_date_str)

        start_date = _parse_date(start_date_str)
        
        # Calculate difference
        diff = end_date - start_date
        days = diff.days
        
        if days < 0:
            return "0 years and 0 months (End date before start date)"
            
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        
        return f"{years} years and {months} months"
    except Exception as e:
        return f"Error calculating duration: {str(e)}"

def _parse_date(date_str: str) -> datetime:
    formats = ["%Y-%m-%d", "%Y-%m", "%Y", "%d.%m.%Y", "%m.%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    # Default fallback if parsing fails (try to extract year at least)
    import re
    year_match = re.search(r"\d{4}", date_str)
    if year_match:
        return datetime(int(year_match.group(0)), 1, 1)
        
    raise ValueError(f"Could not parse date: {date_str}")

# Create Function Tool
date_calculator_tool = FunctionTool.from_defaults(
    fn=calculate_employment_duration,
    name="date_calculator",
    description="Calculates the duration between two dates (e.g., employment). formats: YYYY-MM-DD. 'Present' is valid."
)
