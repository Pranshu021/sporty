# requirements: Python 3.9+
# Install:
#   pip install openai-agents pytz requests

import os
import asyncio
import logging
from typing import List
from dataclasses import dataclass
from datetime import datetime, date
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pytz
import requests

from pydantic import BaseModel
from dotenv import load_dotenv

from agents import Agent, Runner, function_tool, WebSearchTool

# ── -1. Logging Setup ──
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file
logging.info("Loading environment variables from .env file...")
load_dotenv()
logging.info("Environment variables loaded.")

# ── 0. Environment Variables ──
# Make sure to set these environment variables
# OPENAI_API_KEY: Your OpenAI API key
# TELEGRAM_BOT_TOKEN: Your Telegram bot token
# TELEGRAM_CHAT_ID: The chat ID for your Telegram group


# ── 1. Define your context type ──
@dataclass
class UserContext:
    leagues_and_tournaments: List[str]


# ── 2. Define Pydantic schemas for structured outputs ──
class FootballMatchSchema(BaseModel):
    league_or_tournament: str
    team_1: str
    team_2: str
    venue: str
    time: str


class FootballMatchResultSchema(BaseModel):
    league_or_tournament: str
    team_1: str
    team_2: str
    team_1_goals: str
    team_2_goals: str


# ── 3. Define tools ──
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


@function_tool
def get_current_date() -> str:
    """
    Tool: Gets the current date.
    """
    logging.info("Executing get_current_time tool...")
    today = str(date.today())
    formatted_date = str(today).replace("-", "")
    return formatted_date


async def fetch_rendered_html(url: str) -> str:
    """Tool: Scrape fully rendered HTML from ESPN"""
    try:
        logging.info(f"Executing scrape_espn tool for URL: {url}")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, wait_until="domcontentloaded", timeout=120_000)
        # await page.wait_for_timeout(30000)

        html = await page.content()

        await browser.close()
        await playwright.stop()

        soup = BeautifulSoup(html, "lxml")
        day_of_match = soup.select_one("div.Table__Title")
        today = datetime.today()
        formatted_date = today.strftime("%B %d")
        if formatted_date not in day_of_match.text:
            return "<div>No table found</div>"
        else:
            table = soup.select_one("table")
            if not table:
                return "<div>No table found</div>"
            return str(table)

    except Exception as e:
        logging.error(f"Scraper error: {e}")
        return "<div>Error scraping</div>"


@function_tool
async def scrape_data(date: str) -> str:
    leagues = {
        "English Premier League": "eng.1",
        "Spanish LALIGA": "esp.1",
        "UEFA Champions League": "uefa.champions",
        "German Bundesliga": "ger.1",
        "Italian Serie A": "ita.1",
        "English FA Cup": "eng.fa",
        "Spanish Copa Del Rey": "esp.copa_del_rey",
        "English Carabao Cup": "eng.league_cup",
        "FIFA World Cup Qualifying - UEFA": "fifa.worldq.uefa",
    }

    final_html = ""
    for key, league_code in leagues.items():
        url = (
            f"https://www.espn.in/football/fixtures/_/date/{date}/league/{league_code}"
        )
        response = await fetch_rendered_html(url)
        if response.strip() != "<div>No table found</div>":
            final_html += f"<h2>Matches for {key} are below: </h2>\n"
            final_html += response
    return final_html


@function_tool
def schedule_message_formatter(matches: List[FootballMatchSchema]) -> str:
    """
    Tool: Formats match schedules into a visually appealing message.
    """
    try:
        formatted_messages = []
        logging.info(
            f"Executing schedule_message_formatter tool for {len(matches)} matches."
        )
        formatted_messages.append("*📆 Today's Football Fixtures*\n\n")

        matches_by_league = {}
        for match in matches:
            league = match.league_or_tournament
            if league not in matches_by_league:
                matches_by_league[league] = []
            matches_by_league[league].append(match)

        formatted_messages = ["*📆 Today's Football Fixtures*\n\n"]

        for league, league_matches in matches_by_league.items():
            if league_matches:
                formatted_messages.append(f"🏆 *{league}*\n")
                for match in league_matches:
                    formatted_messages.append(
                        f"⚽ {match.team_1} vs {match.team_2} at 🏟️ {match.venue} ⏰ {match.time} \n"
                    )

        final_message = "\n".join(formatted_messages)
        logging.info(f"Formatted message:\n{final_message}")
        return final_message
    except Exception as e:
        logging.error(f"Formatter error: {e}")
        return "Error formatting message."

@function_tool
def results_message_formatter(matches: List[FootballMatchResultSchema]) -> str:
    """
    Tool: Formats match results into a visually appealing message.
    """
    logging.info(
        f"Executing schedule_message_formatter tool for {len(matches)} matches."
    )
    formatted_messages = []
    formatted_messages.append("*📆 Today's Football Fixtures*\n\n")

    matches_by_league = {}
    for match in matches:
        league = match.league_or_tournament
        if league not in matches_by_league:
            matches_by_league[league] = []
        matches_by_league[league].append(match)

    for league, league_matches in matches_by_league.items():
        if league_matches:
            formatted_messages.append(f"🏆 *{league}*\n")
            for match in league_matches:
                formatted_messages.append(
                    f"🗒️ {match.team_1} *{match.team_1_goals}* - *{match.team_2_goals}*\n"
                )

    final_message = "\n".join(formatted_messages)
    logging.info(f"Formatted message:\n{final_message}")
    return final_message

@function_tool
def send_telegram_message(message: str):
    """
    Tool: Sends a message to a Telegram group using a bot.
    """
    logging.info("Executing send_telegram_message tool...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logging.error(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables not set."
        )
        raise ValueError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables not set."
        )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    logging.info(f"Sending message to Telegram chat ID: {chat_id}")
    response = requests.post(url, data=payload)

    if response.status_code != 200:
        logging.error(f"Failed to send message to Telegram: {response.text}")
        raise Exception(f"Failed to send message to Telegram: {response.text}")

    logging.info("Message sent successfully to Telegram.")
    return "Message sent successfully."


@function_tool
def logging_tool(message: str):
    """
    Tool: Logs the messages to terminal
    """
    logging.info(message)


# ── 4. Define agents ──

# Agent to find match schedules

match_schedule_finder = Agent[UserContext](
    name="match_schedule_finder",
    instructions="""
        You are a Football match schedule reporting Agent. Use the `get_current_date` tool to get today's date. After fetching the date, use `scrape_data(date)` tool by passing today's date to receive a FULLY RENDERED HTML string. After you recieve the HTML string, your task is to extract football matches for today's date and populate `FootballMatchSchema`.
        After populating the schema, use the `schedule_message_formatter` tool to receive a formatted message. Finally, deliver the formatted message using the `send_telegram_message` tool. 
    """,
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
    instructions="""
        You are a Football match results reporting Agent. Use the `get_current_date` tool to get today's date. After fetching the date, use `scrape_data(date)` tool by passing today's date to receive a FULLY RENDERED HTML string. After you recieve the HTML string, your task is to extract football matches for today's date and populate `FootballMatchResultsSchema`.
        After populating the schema, use the `schedule_message_formatter` tool to receive a formatted message. Finally, deliver the formatted message using the `send_telegram_message` tool. 
    """,
    model="gpt-4o-mini",
    tools=[WebSearchTool(), results_message_formatter, send_telegram_message],
    output_type=str,
)

# Main agent to manage the workflow
manager_agent = Agent[UserContext](
    name="manager_agent",
    instructions="You are a Sports Newsroom Manager. Your primary responsibility is to coordinate the timely release of soccer news. First, check the current time in IST using the get_current_time tool. Based on the. Based on the time, you will delegate tasks to your team of reporters:\n- If time is between 12:30 PM IST and 05:00 PM IST, delegate to the match_schedule_finder to gather and send the day's match schedules.\n- At 11:50 PM IST, delegate to the match_results_finder to gather and send the results of the day's matches.\nIf it is not one of these times, your job is finished and return a message saying Not the right time.",
    model="gpt-4o-mini",
    tools=[get_current_time],
    handoffs=[match_schedule_finder, match_results_finder],
)

# ── 4. Running the agent ──


async def main():
    logging.info("Starting the agent run...")
    # Define the leagues and tournaments you are interested in
    context = UserContext(
        leagues_and_tournaments=[
            "Premier League",
            "LaLiga",
            "UEFA Champions League",
            "Bundesliga",
        ]
    )

    # The input to the manager_agent doesn't matter as it will use the get_current_time tool
    result = await Runner.run(
        manager_agent, input="start", context=context, max_turns=15
    )
    # await scrape_data("20251116")
    logging.info(f"Run finished. Final output: {result.final_output}")
    print("Run finished. Final output:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
