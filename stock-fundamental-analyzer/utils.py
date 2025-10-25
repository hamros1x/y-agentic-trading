"""
Utilities Module
Helper functions for formatting, validation, and file operations
"""

import os
import re
from datetime import datetime
from typing import Tuple, List, Optional


def format_currency(value: float, currency: str = "₹") -> str:
    """
    Format number as currency with Indian numbering system
    Example: 12345678 -> ₹1,23,45,678
    
    Args:
        value: Numeric value to format
        currency: Currency symbol (default: ₹)
    
    Returns:
        Formatted currency string
    """
    if value is None or (isinstance(value, float) and (value != value)):  # Check for None or NaN
        return "N/A"
    
    try:
        value = float(value)
        if value < 0:
            sign = "-"
            value = abs(value)
        else:
            sign = ""
        
        # Convert to string and split into integer and decimal parts
        value_str = f"{value:.2f}"
        int_part, dec_part = value_str.split('.')
        
        # Apply Indian numbering system
        if len(int_part) <= 3:
            formatted = int_part
        else:
            # Last 3 digits
            last_three = int_part[-3:]
            # Remaining digits in groups of 2
            remaining = int_part[:-3]
            
            # Add commas every 2 digits from right to left
            formatted_remaining = ""
            for i in range(len(remaining) - 1, -1, -2):
                if i == 0:
                    formatted_remaining = remaining[0] + formatted_remaining
                else:
                    formatted_remaining = "," + remaining[i-1:i+1] + formatted_remaining
            
            formatted = formatted_remaining.lstrip(',') + "," + last_three
        
        return f"{sign}{currency}{formatted}.{dec_part}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format number as percentage
    
    Args:
        value: Numeric value (e.g., 0.15 for 15%)
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    if value is None or (isinstance(value, float) and (value != value)):  # Check for None or NaN
        return "N/A"
    
    try:
        value = float(value)
        # If value is already in percentage form (>1), use as is
        if abs(value) > 1:
            return f"{value:.{decimal_places}f}%"
        else:
            # Convert decimal to percentage
            return f"{value * 100:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_large_number(value: float) -> str:
    """
    Format large numbers with Cr/L suffixes (Indian system)
    Example: 15000000000 -> ₹150.00 Cr
    
    Args:
        value: Numeric value
    
    Returns:
        Formatted string with suffix
    """
    if value is None or (isinstance(value, float) and (value != value)):  # Check for None or NaN
        return "N/A"
    
    try:
        value = float(value)
        if value < 0:
            sign = "-"
            value = abs(value)
        else:
            sign = ""
        
        # 1 Crore = 10,000,000
        # 1 Lakh = 100,000
        if value >= 1_00_00_000:  # 1 Crore or more
            return f"{sign}₹{value / 1_00_00_000:.2f} Cr"
        elif value >= 1_00_000:  # 1 Lakh or more
            return f"{sign}₹{value / 1_00_000:.2f} L"
        else:
            return format_currency(value)
    except (ValueError, TypeError):
        return "N/A"


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text with ellipsis if too long
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if text is None:
        return "N/A"
    
    text = str(text)
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length - 3] + "..."



def validate_ticker(ticker: str) -> Tuple[bool, str]:
    """
    Validate ticker format
    Valid formats: SYMBOL.NS (NSE) or SYMBOL.BO (BSE)
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ticker or not isinstance(ticker, str):
        return False, "Ticker cannot be empty"
    
    ticker = ticker.strip().upper()
    
    # Check for valid format: SYMBOL.NS or SYMBOL.BO
    pattern = r'^[A-Z0-9&]+\.(NS|BO)$'
    if re.match(pattern, ticker):
        return True, ""
    else:
        return False, "Invalid symbol format. Please use format: SYMBOL.NS for NSE or SYMBOL.BO for BSE"


def normalize_ticker(ticker: str) -> str:
    """
    Normalize ticker to uppercase and trim whitespace
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Normalized ticker
    """
    if not ticker:
        return ""
    return ticker.strip().upper()


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide with default for zero denominator
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
    
    Returns:
        Result of division or default
    """
    try:
        if denominator == 0 or denominator is None:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default



def create_directory(path: str) -> None:
    """
    Create directory if it doesn't exist
    
    Args:
        path: Directory path
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_timestamp() -> str:
    """
    Get formatted timestamp string
    
    Returns:
        Timestamp in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_report(content: str, ticker: str) -> str:
    """
    Save report to file and return file path
    
    Args:
        content: Report content
        ticker: Stock ticker symbol
    
    Returns:
        File path of saved report
    """
    from config import REPORTS_DIR
    
    # Create reports directory if it doesn't exist
    create_directory(REPORTS_DIR)
    
    # Generate filename with timestamp
    timestamp = get_timestamp()
    filename = f"{ticker}_{timestamp}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    # Write content to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        raise IOError(f"Failed to save report: {str(e)}")


def load_report(file_path: str) -> str:
    """
    Load report content from file
    
    Args:
        file_path: Path to report file
    
    Returns:
        Report content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise IOError(f"Failed to load report: {str(e)}")


def list_saved_reports() -> List[Tuple[str, str, datetime]]:
    """
    List all saved reports with metadata
    
    Returns:
        List of tuples (filename, filepath, creation_date)
    """
    from config import REPORTS_DIR
    
    if not os.path.exists(REPORTS_DIR):
        return []
    
    reports = []
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith('.txt'):
            filepath = os.path.join(REPORTS_DIR, filename)
            creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
            reports.append((filename, filepath, creation_time))
    
    # Sort by creation time, newest first
    reports.sort(key=lambda x: x[2], reverse=True)
    return reports



def calculate_percentage_change(old: float, new: float) -> Optional[float]:
    """
    Calculate percentage change between two values
    
    Args:
        old: Old value
        new: New value
    
    Returns:
        Percentage change or None if calculation not possible
    """
    if old is None or new is None:
        return None
    
    try:
        old = float(old)
        new = float(new)
        
        if old == 0:
            return None
        
        return ((new - old) / abs(old)) * 100
    except (ValueError, TypeError):
        return None
