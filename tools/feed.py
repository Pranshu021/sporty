import feedparser
from datetime import datetime, date
from agents import function_tool

RSS_FEEDS = {
    "ESPN": "https://www.espn.com/espn/rss/soccer/news",
    "BBC": "https://feeds.bbci.co.uk/sport/football/rss.xml",
}


def deduplicate(news):
    seen = set()
    unique = []

    for item in news:
        key = item["headline"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


@function_tool
def fetch_today_news():
    today = date.today()
    news_items = []

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue

            published = datetime(*entry.published_parsed[:6]).date()
            if published != today:
                continue

            news_items.append(
                {
                    "headline": entry.title,
                    "source": source,
                    "url": entry.link,
                    "published": published,
                }
            )
    de_duplicated_news = deduplicate(news_items)
    return de_duplicated_news
