from typing import List
from agents import Agent
from models.context import UserContext
from models.schemas import FootballMatchSchema
from prompts.system_prompts import (
    MATCH_SCHEDULE_FINDER_INSTRUCTIONS,
    MATCH_RESULTS_FINDER_INSTRUCTIONS,
)
from tools.utils import get_current_date, get_previous_date, logging_tool
from tools.scraping import scrape_data
from tools.formatting import schedule_message_formatter, results_message_formatter
from tools.telegram import send_telegram_message

# Agent to find match schedules
match_schedule_finder = Agent[UserContext](
    name="match_schedule_finder",
    instructions=MATCH_SCHEDULE_FINDER_INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[
        logging_tool,
        get_current_date,
        scrape_data,
        schedule_message_formatter,
        send_telegram_message,
    ],
    output_type=List[FootballMatchSchema],
)

# Agent to find match results
match_results_finder = Agent[UserContext](
    name="match_results_finder",
    instructions=MATCH_RESULTS_FINDER_INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[
        logging_tool,
        get_previous_date,
        scrape_data,
        results_message_formatter,
        send_telegram_message,
    ],
    output_type=str,
)
