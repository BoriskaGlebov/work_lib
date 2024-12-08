from datetime import datetime, timedelta
from venv import logger

import requests
from celery import Celery
from celery.schedules import crontab
from flask_login import login_user

from app import app
from models import Transaction, db, User

periodic_app = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)


@periodic_app.task
def check_pending_transactions() -> dict:
    """
    Проверяет ожидающие транзакции, которые старше 15 минут,
    и обновляет их статус на 'Expired' (истекший).

    Эта функция запрашивает базу данных на наличие транзакций со
    статусом 'Pending' (ожидающий), созданных более 15 минут назад.
    Она обновляет их статус на 'Expired' и отправляет уведомление
    по вебхуку на указанный URL.

    Returns:
        dict: Словарь, содержащий количество истекших транзакций.
    """

    # Получаем текущее время
    now: datetime = datetime.now()

    # Находим транзакции со статусом 'Pending', старше 15 минут
    fifteen_minutes_ago: datetime = now - timedelta(minutes=1)
    print(fifteen_minutes_ago)

    with app.app_context():
        expired_transactions: list[Transaction] = Transaction.query.filter(
            Transaction.status == 'pending',
            Transaction.created_at < fifteen_minutes_ago
        ).all()


        # login_user(admin_user)
        for transaction in expired_transactions:
            # Обновляем статус транзакции на 'Expired'
            print(transaction)
            transaction.status = 'expired'
            db.session.commit()

            # Отправляем уведомление по вебхуку
            webhook_url: str = f'http://web:5000/transactions/{transaction.id}'
            payload: dict = {
                "id": transaction.id,
                "status": "expired"
            }
            requests.put(webhook_url, json=payload)

        return {"expired_transaction": len(expired_transactions)}


periodic_app.conf.beat_schedule = {
    'check-pending-transactions-every-minute': {
        'task': 'celery_file.check_pending_transactions',
        'schedule': crontab(minute='*'),  # Каждую минуту
    },
}
