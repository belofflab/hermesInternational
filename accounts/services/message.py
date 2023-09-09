from telebot import TeleBot


from django.conf import settings

bot = TeleBot(token=settings.BOT_TOKEN, parse_mode="HTML")


def send(text: str) -> None:
    try:
        bot.send_message(chat_id=settings.CHAT_ID, text=text)
    except Exception as e: print("Error with sending tg", e)
