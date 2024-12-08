from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, User, Transaction
from config import logger


def test_login(client):
    """Test the login functionality."""
    response = client.post('/login', data={'username': 'admin','password':'asd'})
    assert response.status_code == 302  # Check for redirect after login
    assert b'Dashboard' in response.data  # Check if the dashboard is accessible


def test_create_user(client):
    """Test creating a new user."""
    response = client.post('/users', data={
        'username': 'newuser',
        'balance': 100,
        'commission_rate': 0.01,
    })

    assert response.status_code == 302  # Check for redirect after creating user
    user = User.query.filter_by(username='newuser').first()
    assert user is not None  # Ensure the user was created



def test_create_user(client):
    response = client.post('/users', data={'username': 'testUser1', 'balance': 1001, 'commission_rate': 0.01})
    assert response.status_code == 302  # Redirect after successful creation
    user = User.query.filter_by(username='testUser1').first()
    assert user is not None
    assert user.balance == 1001


def test_create_transaction(client):
    # Сначала создаем пользователя
    client.post('/users', data={'username': 'testUser2', 'balance': 100, 'commission_rate': 0.01})
    user = User.query.filter_by(username='testUser2').first()

    response = client.post('/create_transaction', json={'amount': 200, 'user_id': user.id})
    assert response.status_code == 201
    transaction_data = response.get_json()
    transaction = Transaction.query.get(transaction_data['id'])
    assert transaction is not None
    assert transaction.amount == 200

def test_change_status(client):
    client.post('/users', data={'username': 'testUser3', 'balance': 100, 'commission_rate': 0.01})
    user = User.query.filter_by(username='testUser3').first()
    response = client.post('/create_transaction', json={'amount': 200, 'user_id': user.id})
    transaction_data = response.json
    assert response.status_code==201
    expired_status=client.put(f'/transactions/{transaction_data['id']}')
    assert expired_status.status=='302 FOUND'

    response2 = client.post('/create_transaction', json={'amount': 200, 'user_id': user.id})
    transaction_data2 = response2.json
    assert response2.status_code == 201
    expired_status2 = client.post(f'/transactions/{transaction_data2['id']}',data={"status":"confirmed"})
    assert expired_status2.status == '302 FOUND'

    response3 = client.post('/create_transaction', json={'amount': 200, 'user_id': user.id})
    transaction_data3 = response3.json
    assert response3.status_code == 201
    expired_status3 = client.post(f'/transactions/{transaction_data3['id']}', data={"status": "canceled"})
    assert expired_status3.status == '302 FOUND'




def test_cancel_transaction(client):
    # Создаем пользователя и транзакцию
    client.post('/users', data={'username': 'testUser4', 'balance': 100, 'commission_rate': 0.01})
    user = User.query.filter_by(username='testUser4').first()
    response = client.post('/create_transaction', json={'amount': 200, 'user_id': user.id})

    transaction_data = response.get_json()

    # Отменяем транзакцию
    response = client.post('/cancel_transaction', json={'id': transaction_data['id']})
    assert response.status_code == 200
    transaction = Transaction.query.get(transaction_data['id'])
    assert transaction.status == 'canceled'


def test_confirm_transaction(client):
    # Создаем пользователя и транзакцию
    client.post('/users', data={'username': 'testUser5', 'balance': 100, 'commission_rate': 0.01})
    user = User.query.filter_by(username='testUser5').first()

    response = client.post('/create_transaction', json={'amount': 200, 'user_id': user.id})

    transaction_data = response.get_json()

    # Подтверждаем транзакцию
    response = client.post('/confirm_transaction', json={'id': transaction_data['id']})
    assert response.status_code == 200
    transaction = Transaction.query.get(transaction_data['id'])
    assert transaction.status == 'confirmed'


def test_check_transaction(client):
    # Создаем пользователя и транзакцию
    client.post('/users', data={'username': 'testUser6', 'balance': 100, 'commission_rate': 0.01})
    user = User.query.filter_by(username='testUser6').first()

    response = client.post('/create_transaction', json={'amount': 200, 'user_id': user.id})

    transaction_data = response.get_json()

    # Проверяем транзакцию
    response = client.get(f'/check_transaction/{transaction_data["id"]}')
    assert response.status_code == 200
    data = response.get_json()

    assert data['id'] == transaction_data['id']