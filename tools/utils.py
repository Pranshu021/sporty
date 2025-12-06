import logging
import pytz
from datetime import datetime, date, timedelta
from agents import function_tool


# Get current time. Used by manager agent to check time for handovers.
@function_tool
def get_current_time() -> str:
    """
    Tool: Gets the current time in Indian Standard Time (IST).
    """
    logging.info("Executing get_current_time tool...")
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    current_time = now.strftime("%H:%M")
    logging.info(f"Current IST time: {current_time}")
    return current_time


# Get current date. Used by Scheduling agent to get the current date.
@function_tool
def get_current_date() -> str:
    """
    Tool: Gets the current date.
    """
    logging.info("Executing get_current_time tool...")
    today = str(date.today())
    # Formatting for ESPN URL.
    formatted_date = str(today).replace("-", "")
    return formatted_date


# Get previous date. Used by results reporting agent to get the previous date.
@function_tool
def get_previous_date() -> str:
    """
    Tool: Gets the previous date.
    """
    logging.info("Executing get_previous_date tool...")
    yesterday = str(date.today() - timedelta(days=1))
    formatted_date = str(yesterday).replace("-", "")
    return formatted_date


# For logging stuff in terminal
@function_tool
def logging_tool(message: str):
    """
    Tool: Logs the messages to terminal
    """
    logging.info(message)
