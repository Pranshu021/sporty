import logging
from typing import List
from agents import function_tool
from models.schemas import (
    FootballMatchSchema,
    FootballMatchResultSchema,
    FootballNewsSchema,
)
from tools.telegram import send_telegram_message
from bs4 import BeautifulSoup


# custom function to remove additional non-parsable HTML tags that are added by LLMs. More like a safeguard function to clean the response.
def clean_html(text: str) -> str:
    """Removes HTML tags from a string."""
    return BeautifulSoup(text, "html.parser").get_text()


# Helper function to format the message in a specific way. Might change it later tbh
def _format_schedule_message(matches: List[FootballMatchSchema]) -> str:
    try:
        formatted_messages = []
        logging.info(f"Formatting schedule message for {len(matches)} matches.")
        formatted_messages.append("<b>📆 Today's Football Fixtures</b>\n\n")

        matches_by_league = {}
        for match in matches:
            league = clean_html(match.league_or_tournament)
            if league not in matches_by_league:
                matches_by_league[league] = []
            matches_by_league[league].append(match)

        for league, league_matches in matches_by_league.items():
            if league_matches:
                formatted_messages.append(f"🏆 <b>{league}</b>\n")
                for match in league_matches:
                    formatted_messages.append(
                        f"⚽ <b>{clean_html(match.team_1)}</b> vs <b>{clean_html(match.team_2)}</b> at 🏟️ {clean_html(match.venue)} ⏰ {clean_html(match.time)} \n"
                    )

        final_message = "\n".join(formatted_messages)
        return final_message
    except Exception as e:
        logging.error(f"Formatter error: {e}")
        return "Error formatting message."


# Helper function to format the message in a specific way. Might change it later tbh
def _format_news_message(news: List[FootballNewsSchema]) -> str:
    """
    Tool: Formats news into a visually appealing message.
    """
    logging.info(f"Executing format_news tool for {len(news)} news.")
    formatted_messages = []
    formatted_messages.append("<b>⚽ Today's Football News</b>\n\n")

    for news_item in news:
        formatted_messages.append(f"\n<b> 📰 {clean_html(news_item.headline)}</b>\n")
        formatted_messages.append(f" 🔗 {clean_html(news_item.article_url)}\n\n")

    final_message = "\n".join(formatted_messages)
    logging.info(f"Formatted message:\n{final_message}")
    return final_message


# Function tool to format the message and send the message to telegram
@function_tool
def broadcast_schedule_message(matches: List[FootballMatchSchema]) -> str:
    """
    Tool: Formats match schedules and sends them to Telegram.
    """
    formatted_message = _format_schedule_message(matches)
    if formatted_message == "Error formatting message.":
        return "Failed to format message."

    return send_telegram_message(formatted_message)


@function_tool
def broadcast_news_message(news: List[FootballNewsSchema]) -> str:
    """
    Tool: Formats today's football news and sends them to Telegram.
    """
    formatted_message = _format_news_message(news)
    logging.info(f"Formatted news: {formatted_message}")
    if formatted_message == "Error formatting message.":
        return "Failed to format message."

    return send_telegram_message(formatted_message)


# Message formatter tool for a consistent output message on telegram for Match Results
# HTML Formatted
@function_tool
def results_message_formatter(matches: List[FootballMatchResultSchema]) -> str:
    """
    Tool: Formats match results into a visually appealing message.
    """
    logging.info(
        f"Executing results_message_formatter tool for {len(matches)} matches."
    )
    formatted_messages = []
    formatted_messages.append("<b>📆 Yesterday's Fixtures Results</b>\n\n")

    matches_by_league = {}
    for match in matches:
        league = clean_html(match.league_or_tournament)
        if league not in matches_by_league:
            matches_by_league[league] = []
        matches_by_league[league].append(match)

    for league, league_matches in matches_by_league.items():
        if league_matches:
            formatted_messages.append(f"🏆 <b>{league}</b>\n")
            for match in league_matches:
                formatted_messages.append(
                    f"🗒️ {clean_html(match.home_team)} <b>{clean_html(match.score)}</b> {clean_html(match.away_team)}\n"
                )

    final_message = "\n".join(formatted_messages)
    logging.info(f"Formatted message:\n{final_message}")
    return final_message
