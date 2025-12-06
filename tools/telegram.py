import os
import logging
import requests
from agents import function_tool


# Tool to send Telegram messages
@function_tool
def send_telegram_message(message: str):
    """
    Tool: Sends a message to a Telegram group using a bot.
    """
    logging.info("Executing send_telegram_message tool...")
    logging.info(f"Formatted message - {message}")
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
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    logging.info(f"Sending message to Telegram chat ID: {chat_id}")
    response = requests.post(url, data=payload)

    if response.status_code != 200:
        logging.error(f"Failed to send message to Telegram: {response.text}")
        raise Exception(f"Failed to send message to Telegram: {response.text}")

    logging.info("Message sent successfully to Telegram.")
    return "Message sent successfully."
