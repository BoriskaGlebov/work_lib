from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()

class User(UserMixin,db.Model):
    """Модель пользователя.

    Attributes:
        id (int): Уникальный идентификатор пользователя.
        username (str): Уникальное имя пользователя.
        balance (float): Баланс пользователя.
        commission_rate (float): Процент комиссии для пользователя.
        webhook_url (str): URL для получения уведомлений через вебхук.
    """
    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(20), nullable=False, unique=True)
    balance: float = db.Column(db.Float, nullable=False, default=0.0)
    commission_rate: float = db.Column(db.Float, nullable=False, default=0.05)
    webhook_url: str = db.Column(db.String(255), nullable=True, default=f"http://localhost:5000/user/")
    is_admin = db.Column(db.Boolean, default=False)  # Поле для роли администратора

    # @property
    # def is_active(self):
    #     return True  # Здесь вы можете добавить логику для проверки активности пользователя
    #
    # @property
    # def is_authenticated(self):
    #     return True  # Пользователь считается аутентифицированным после входа
    #
    # @property
    # def is_anonymous(self):
    #     return False  # Пользователь не анонимный после входа

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта User.

        :return: Строка с именем пользователя.
        """
        return f"<User {self.username}>"

class Transaction(db.Model):
    """Модель транзакции.

    Attributes:
        id (int): Уникальный идентификатор транзакции.
        created_at (datetime): Дата и время создания транзакции.
        amount (float): Сумма транзакции.
        commission (float): Комиссия за транзакцию.
        status (str): Статус транзакции ('pending', 'confirmed', 'canceled', 'expired').
        user_id (int): Идентификатор пользователя, связанного с транзакцией.
        user (User): Связанный объект User.
    """
    __tablename__ = "transactions"

    id: int = db.Column(db.Integer, primary_key=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.now)
    amount: float = db.Column(db.Float, nullable=False)  # Сумма транзакции
    commission: float = db.Column(db.Float, nullable=False)  # Комиссия за транзакцию
    status: str = db.Column(
        db.Enum("pending", "confirmed", "canceled", "expired"),
        nullable=False,
        default="pending",
    )  # Статус транзакции

    user_id: int = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )  # Связь с пользователем
    user = db.relationship("User", backref=db.backref("transactions", lazy=True))

    def calculate_commission(self) -> None:
        """Вычисляет комиссию для транзакции на основе комиссии пользователя.

        :return: None
        """
        user = User.query.first()  # Предполагаем, что есть хотя бы один пользователь
        if user:
            self.commission = self.amount * user.commission_rate

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта Transaction.

        :return: Строка с информацией о транзакции.
        """
        return f"<Transaction {self.id}, Amount: {self.amount}, Commission: {self.commission}, Status: {self.status}>"