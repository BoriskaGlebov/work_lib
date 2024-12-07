from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    # email = db.Column(db.String(254), nullable=False, unique=True)
    # password_hash = db.Column(db.String(128), nullable=False)  # Хэш пароля?
    balance = db.Column(db.Float, nullable=False, default=0.0)
    commission_rate = db.Column(db.Float, nullable=False, default=0.05)
    # role = db.Column(db.String(20), default='user')  # Add this line
    webhook_url = db.Column(db.String(255), nullable=True)

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    amount = db.Column(db.Float, nullable=False)  # Сумма транзакции
    commission = db.Column(db.Float, nullable=False)  # Комиссия за транзакцию
    status = db.Column(db.Enum('pending', 'confirmed', 'canceled', 'expired'), nullable=False,
                       default='pending')  # Статус транзакции

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Связь с пользователем
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

    def calculate_commission(self):
        # Пример расчета комиссии (можно изменить по необходимости)
        user = User.query.first()  # Предполагаем, что есть хотя бы один пользователь
        if user:
            self.commission = self.amount * user.commission_rate

    def __repr__(self):
        return f'<Transaction {self.id}, Amount: {self.amount}, Commission: {self.commission}, Status: {self.status}>'
