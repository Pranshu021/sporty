import os
import logging
import requests
from bs4 import BeautifulSoup


def sanitize_message(message: str) -> str:
    """
    Sanitizes the message by removing unsupported HTML tags for Telegram.
    Supported tags: b, strong, i, em, u, ins, s, strike, del, a, code, pre
    """
    allowed_tags = [
        "b",
        "strong",
        "i",
        "em",
        "u",
        "ins",
        "s",
        "strike",
        "del",
        "a",
        "code",
        "pre",
    ]
    soup = BeautifulSoup(message, "html.parser")

    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            # Unwrap the tag (keep content, remove tag)
            # For block-level elements like div, p, ul, li, we might want to add a newline
            if tag.name in ["div", "p", "li", "br"]:
                tag.insert_after("\n")
            tag.unwrap()

    return str(soup)


# Tool to send Telegram messages
def send_telegram_message(message: str):
    """
    Tool: Sends a message to a Telegram group using a bot.
    """
    logging.info("Executing send_telegram_message tool...")

    # Sanitize the message before sending
    sanitized_message = sanitize_message(message)
    logging.info(f"Original message: {message}")
    logging.info(f"Sanitized message: {sanitized_message}")

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
    # Keeping parse mode as HTML. Markdown didn't work well.
    payload = {"chat_id": chat_id, "text": sanitized_message, "parse_mode": "HTML"}

    logging.info(f"Sending message to Telegram chat ID: {chat_id}")
    response = requests.post(url, data=payload)

    if response.status_code != 200:
        logging.error(f"Failed to send message to Telegram: {response.text}")
        raise Exception(f"Failed to send message to Telegram: {response.text}")

    logging.info("Message sent successfully to Telegram.")
    return "Message sent successfully."
