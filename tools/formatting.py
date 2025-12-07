import logging
from typing import List
from agents import function_tool
from models.schemas import FootballMatchSchema, FootballMatchResultSchema


from bs4 import BeautifulSoup


# custom function to remove additional non-parsable HTML tags that are added by LLMs. More like a safeguard function to clean the response.
def clean_html(text: str) -> str:
    """Removes HTML tags from a string."""
    return BeautifulSoup(text, "html.parser").get_text()


# Message formatter tool for a consistent output message on telegram for Match schedules
# HTML Formatted
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
        formatted_messages.append("<b>📆 Today's Football Fixtures</b>\n\n")

        matches_by_league = {}
        for match in matches:
            league = clean_html(match.league_or_tournament)
            if league not in matches_by_league:
                matches_by_league[league] = []
            matches_by_league[league].append(match)

        formatted_messages = ["<b>📆 Today's Football Fixtures</b>\n\n"]

        for league, league_matches in matches_by_league.items():
            if league_matches:
                formatted_messages.append(f"🏆 <b>{league}</b>\n")
                for match in league_matches:
                    formatted_messages.append(
                        f"⚽ <b>{clean_html(match.team_1)}</b> vs <b>{clean_html(match.team_2)}</b> at 🏟️ {clean_html(match.venue)} ⏰ {clean_html(match.time)} \n"
                    )

        final_message = "\n".join(formatted_messages)
        # logging.info(f"Formatted message:\n{final_message}")
        return final_message
    except Exception as e:
        logging.error(f"Formatter error: {e}")
        return "Error formatting message."


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
