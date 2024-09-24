import logging

import requests
from config import CONFIG


def send_message(token, conversation_id, message=""):
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Payload with chat ID and the message to be sent
    payload = {
        'chat_id': conversation_id,
        'text': message
    }
    # Sending the request to the Telegram API
    response = requests.post(url, data=payload)
    logging.debug(f"telegram bot response : {response.text}")
    return response.status_code == 200


def send(message=""):
    return send_message(CONFIG.telegram_token, CONFIG.telegram_conversation_id, message)


if __name__ == "__main__":
    send("hello this is the test")
