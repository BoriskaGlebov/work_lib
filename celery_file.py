from datetime import datetime, timedelta

import requests
from celery import Celery
from celery.schedules import crontab
from flask import request

from app import app
from models import Transaction, db  # Import your database instance

# from models import Transaction  # Import your Transaction model

periodic_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)



@periodic_app.task
def check_pending_transactions():
    """Check for pending transactions and update their status."""
    # Get the current time
    now = datetime.now()

    # Find transactions with status 'Pending' older than 15 minutes
    fifteen_minutes_ago = now - timedelta(minutes=1)
    print(fifteen_minutes_ago)
    with app.app_context():
        expired_transactions = Transaction.query.filter(
            Transaction.status == 'pending',
            Transaction.created_at < fifteen_minutes_ago
        ).all()

        for transaction in expired_transactions:
            # Update the transaction status to 'Expired'
            print(transaction)
            transaction.status = 'expired'
            db.session.commit()

            # Send webhook notification
            # webhook_url = transaction.webhook_url  # Assuming you have a webhook URL field in your model
            webhook_url=f'http://localhost:5000/transactions/{transaction.id}'
            payload = {
                "id": transaction.id,
                "status": "expired"
            }
            requests.put(webhook_url, json=payload)
        return {"expired_tranzaction":len(expired_transactions)}

periodic_app.conf.beat_schedule = {
    'check-pending-transactions-every-minute': {
        'task': 'celery_file.check_pending_transactions',
        'schedule': crontab(minute='*'),  # Every minute
    },
}

if __name__ == '__main__':
    now = datetime.now()
    fifteen_minutes_ago = now - timedelta(minutes=1)
    print(fifteen_minutes_ago)
    with app.app_context():
        expired_transactions = Transaction.query.filter(
            Transaction.status == 'pending',
            # Transaction.created_at < fifteen_minutes_ago
        ).all()

        for transaction in expired_transactions:
            # Update the transaction status to 'Expired'
            print(transaction)
        for transaction in expired_transactions:
            # Update the transaction status to 'Expired'
            print(transaction)
            transaction.status = 'expired'
            db.session.commit()

            # Send webhook notification
            # webhook_url = transaction.webhook_url  # Assuming you have a webhook URL field in your model
            webhook_url=f'http://localhost:5000/transactions/{transaction.id}'
            payload = {
                "id": transaction.id,
                "status": "expired"
            }
            res=requests.post(webhook_url, json=payload)
            print(res.status_code)

