import logging
from typing import List

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from telebot import TeleBot

logger = logging.getLogger(__name__)

bot = TeleBot(token=settings.BOT_TOKEN, parse_mode="HTML")


@shared_task
def send_email(body: str, subject: str, recipients: List[str], **kwargs) -> None:
    try:

        message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )

        message.content_subtype = "html"
    

        message.send()
        logger.info("Сообщения были разосланы")
    except Exception as e:
        logger.error(f"Почтовое сообщение не было отправлено, {e}")


@shared_task
def notify_admin_by_telegram(text: str) -> None:
    try:
        bot.send_message(chat_id=settings.CHAT_ID, text=text)
    except Exception as e:
        logger.error(f"Сообщение админам не удалось отправить {e}")
