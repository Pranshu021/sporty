import logging
from datetime import datetime, timedelta, date
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from agents import function_tool
import dateparser


# Scraping ESPN website for match results and schedules depending upon type_of_data required.
async def fetch_rendered_html(url: str, type_of_data: str) -> str:
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
        # Fetching the first table of the page which will be for the date mentioned in the URL params/path
        day_of_match = soup.select_one("div.Table__Title")
        # If today's date not found on the page, return no matches or results
        if day_of_match is None or dateparser.parse(day_of_match.text) is None:
            return "<div>No table found</div>"
        # Using dateparser to convert the day of the match to a standard date object. No errors or edge-cases in comparing dates now. Better than comparing strings.
        parsed_day_of_match = dateparser.parse(day_of_match.text).date()
        parsed_formatted_date = ""
        if type_of_data == "fixtures":
            today = datetime.today()
            formatted_date = today.strftime("%B %d")
            # Using dateparser to convert the today's date to a standard date object.
            parsed_formatted_date = dateparser.parse(formatted_date).date()
        else:
            yesterday = datetime.today() - timedelta(days=1)
            formatted_date = yesterday.strftime("%B %d")
            # Using dateparser to convert the yesterday's date to a standard date object.
            parsed_formatted_date = dateparser.parse(formatted_date).date()
        # Better errorless date comparison with standard objects.
        if parsed_formatted_date != parsed_day_of_match:
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
async def scrape_data(Date: str) -> str:
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
            f"https://www.espn.in/football/fixtures/_/date/{Date}/league/{league_code}"
        )
        today = str(date.today())
        formatted_date = str(today).replace("-", "")
        if formatted_date == Date:
            response = await fetch_rendered_html(url, "fixtures")
        else:
            response = await fetch_rendered_html(url, "results")

        if response.strip() != "<div>No table found</div>":
            final_html += f"<h2>Matches for {key} are below: </h2>\n"
            final_html += response
    return final_html


# --------------------------------------------------
# FOR TESTING Tools directly -
# Don't forget to Remove `@function_tool` above
# --------------------------------------------------

# async def main():
#     await scrape_data("20251201")

# if __name__ == "__main__":
#     import asyncio

# asyncio.run(main())
