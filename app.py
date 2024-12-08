import os
from datetime import datetime

import click
from celery import Celery
from flasgger import Swagger
from flask import (Flask, jsonify, redirect, render_template,
                   request, url_for, Response, flash)
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

from config import Config, logger
from forms import LoginForm
from models import Transaction, User, db

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

app.config.from_object(Config)
# app.secret_key = os.getenv('SECRET_KEY')  # Замените на ваш уникальный ключ
CORS(app)  # Enable CORS for all routes
# Инициализация Swagger.
swagger = Swagger(app, template_file="swagger.yml")
db.init_app(app)
with app.app_context():
    db.create_all()
    db.session.commit()


@app.cli.command("create-admin")
@click.argument("admin")
def create_user(admin: str) -> None:
    """
    Создает дефолтного администратора.

    :param admin: Имя администратора (строка).
    :return: None
    """
    db.drop_all()
    db.create_all()

    user = User(
        balance=100,
        username="testUser",
        commission_rate=0.01,
        webhook_url="http://localhosts:5000/user/1",
    )  # Создание базы данных и таблиц
    admin_user = User(username="admin", is_admin=True)
    transaction_test = Transaction(amount=100, commission=user.commission_rate * 100, status="confirmed", user_id=2)
    transaction_test1 = Transaction(amount=200, commission=user.commission_rate * 200, status="pending", user_id=2)
    transaction_test2 = Transaction(amount=300, commission=user.commission_rate * 300, status="canceled", user_id=2)
    transaction_test3 = Transaction(amount=400, commission=user.commission_rate * 400, status="expired", user_id=2)

    db.session.add_all([admin_user, user, transaction_test, transaction_test1, transaction_test2, transaction_test3])

    db.session.commit()
    logger.info("Админ Создан")


# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Укажите маршрут для перенаправления при необходимости входа


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Создаем экземпляр формы
    if form.validate_on_submit():  # Проверяем, была ли форма отправлена и валидна ли она
        username = form.username.data
        # password = form.password.data
        user = User.query.filter_by(username=username).first()  # Получаем пользователя из базы данных

        if user:  # Здесь вы можете добавить хеширование паролей
            login_user(user)  # Входим в систему
            return redirect(url_for('dashboard'))  # Перенаправляем на дашборд после успешного входа
        else:
            flash('Неверное имя пользователя или пароль.')  # Сообщение об ошибке

    return render_template('login.html', form=form)  # Передаем форму в шаблон
#

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))  # Перенаправление на страницу входа после выхода


@app.route("/")
@login_required
def dashboard() -> str:
    """Dashboard с транзакциями. Транзакции отмененные или с истекшим сроком не считает

    :return: HTML шаблон дашборда (строка).
    """
    total_users = User.query.count()

    if current_user.is_admin:
        # Если пользователь администратор, показываем все транзакции
        total_transactions = Transaction.query.count()

        today_transactions = Transaction.query.filter(
            Transaction.created_at >= datetime.now().date()
        ).all()

        total_amount_today = sum(
            transaction.amount for transaction in today_transactions
            if transaction.status not in ['canceled', 'expired']
        )

        recent_transactions = Transaction.query.order_by(Transaction.id.desc()).limit(5).all()
    else:
        # Если пользователь обычный, показываем только его транзакции
        total_transactions = Transaction.query.filter_by(user_id=current_user.id).count()

        today_transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.created_at >= datetime.now().date()
        ).all()

        total_amount_today = sum(
            transaction.amount for transaction in today_transactions
            if transaction.status not in ['canceled', 'expired']
        )

        recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(
            Transaction.id.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_transactions=total_transactions,
        total_amount_today=total_amount_today,
        recent_transactions=recent_transactions,
    )


@app.route("/users", methods=["GET", "POST"])
@login_required
def users() -> Response | tuple[str, int] | str:
    """Страница создания и получения пользователей.

    :return: HTML шаблон страницы пользователей (строка).
    """
    if not current_user.is_admin:
        flash("You do not have permission to view this page.")
        return redirect(url_for('dashboard'))
    if request.method == "POST":
        username = request.form["username"]
        balance = request.form.get("balance")
        commission_rate = request.form.get("commission_rate")

        new_user = User(username=username)

        if balance:
            new_user.balance = float(balance)
        if commission_rate:
            new_user.commission_rate = float(commission_rate)
        try:
            db.session.add(new_user)
            db.session.commit()
            logger.info("Создан пользователь")
            new_user.webhook_url = f'http://localhost:5000/user/{new_user.id}'
            db.session.commit()
            return redirect(url_for("users"))
        except IntegrityError:
            logger.error("Ошибка добавления пользователя")
            db.session.rollback()  # Откат транзакции в случае ошибки
            error_message = "Пользователь с таким именем уже существует."
            return render_template("error.html", error=error_message), 400

    user_list = User.query.all()
    return render_template("users.html", users=user_list)


@app.route("/transactions", methods=["GET"])
@login_required
def transactions() -> str:
    """Страница со всеми транзакциями.

    :return: HTML шаблон страницы транзакций (строка).
    """
    user_id = request.args.get('user_id')  # Получаем ID пользователя из параметров запроса
    status = request.args.get('status')  # Получаем статус из параметров запроса

    query = Transaction.query

    # Фильтрация по пользователю
    if current_user.is_admin:
        # If the user is an admin, they can filter by user
        if user_id:
            query = query.filter(Transaction.user_id == user_id)

    else:
        # If the user is a regular user, show only their transactions
        query = query.filter(Transaction.user_id == current_user.id)

    # Фильтрация по статусу
    if status:
        query = query.filter(Transaction.status == status)

    transaction_list = query.all()  # Получаем отфильтрованные транзакции
    users = User.query.all()  # Получаем всех пользователей для выпадающего списка фильтра

    return render_template("transactions.html", transactions=transaction_list, users=users)


@app.route("/transactions/<int:transaction_id>", methods=["GET", "PUT", "POST"])
@login_required
def transaction_detail(transaction_id: int) -> str | Response:
    """Детальный просмотр транзакции и обновление статуса транзакций.

    :param transaction_id: ID транзакции (целое число).
    :return: HTML шаблон детального просмотра транзакции (строка).
    """
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == 'PUT':
        if transaction.status == 'pending':
            transaction.status = 'expired'
            db.session.commit()
            return redirect(url_for('transactions'))
    elif request.method == 'POST':
        new_status = request.form.get('status')

        if new_status in ['confirmed', 'canceled']:
            transaction.status = new_status
            db.session.commit()
            return redirect(url_for('transactions'))

    return render_template("transaction_detail.html", transaction=transaction)


@app.route("/create_transaction", methods=["POST"])
def create_transaction() -> tuple:
    """Создать транзакцию.

    :return: JSON ответ с ID созданной транзакции (кортеж).
             Успех (201) или ошибка (400).
    """
    data = request.json

    if ("amount" or "user_id") not in data:
        return jsonify({"error": "Поле 'amount'/'user_id' обязательно для заполнения."}), 400

    amount = data["amount"]
    user_id = data["user_id"]
    check_user = db.session.get(User, user_id)
    if check_user:
        logger.info("Есть такой пользователь")
        transaction = Transaction(amount=amount, user_id=user_id)
    else:
        logger.error("Нет такого пользователь")
        error_message = "Пользователь с таким именем не  существует."
        return render_template("error.html", error=error_message), 400

    # Расчет комиссии
    transaction.calculate_commission()
    # transaction.commission = commission

    # Сохранение транзакции в базе данных
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"id": transaction.id}), 201


@app.route("/cancel_transaction", methods=["POST"])
def cancel_transaction() -> tuple:
    """Отмена транзакции по ID без HTML.

    :return: JSON ответ с сообщением об отмене или ошибкой (кортеж).
             Успех (200) или ошибка (400/404).
    """
    data = request.json

    # Проверка наличия обязательного параметра id
    if "id" not in data:
        return jsonify({"error": "Поле 'id' обязательно для заполнения."}), 400

    transaction_id = data["id"]

    # Получение транзакции из базы данных
    transaction = db.session.get(Transaction, transaction_id)

    if not transaction:
        logger.error("Попытка отменить несуществующую транзакцию")
        return jsonify({"error": "Транзакция не найдена."}), 404

    # Проверка статуса транзакции
    if transaction.status == "pending":
        transaction.status = "canceled"
        db.session.commit()
        return (
            jsonify(
                {"message": "Транзакция отменена.", "transaction_id": transaction.id}
            ),
            200,
        )
    logger.error(f"Попытка отменить транзакцию со статусом {transaction.status} > id {transaction_id}")
    return jsonify({"error": "Невозможно отменить транзакцию с текущим статусом."}), 400


@app.route("/confirm_transaction", methods=["POST"])
def confirm_transaction() -> tuple:
    """Подтвердить транзакции по ID без HTML.

    :return: JSON ответ с сообщением о подтверждении или ошибкой (кортеж).
             Успех (200) или ошибка (400/404).
    """
    data = request.json

    # Проверка наличия обязательного параметра id
    if "id" not in data:
        return jsonify({"error": "Поле 'id' обязательно для заполнения."}), 400

    transaction_id = data["id"]

    # Получение транзакции из базы данных
    transaction = db.session.get(Transaction, transaction_id)

    if not transaction:
        logger.error("Попытка отменить несуществующую транзакцию")
        return jsonify({"error": "Транзакция не найдена."}), 404

    # Проверка статуса транзакции
    if transaction.status == "pending":
        transaction.status = "confirmed"
        db.session.commit()
        return (
            jsonify(
                {"message": "Транзакция подтверждена.", "transaction_id": transaction.id}
            ),
            200,
        )
    logger.error(f"Попытка подтвердить транзакцию со статусом {transaction.status} > id {transaction_id}")
    return jsonify({"error": "Невозможно подтвердить транзакцию с текущим статусом."}), 400


@app.route("/check_transaction/<int:transaction_id>", methods=["GET"])
def check_transaction(transaction_id: int) -> tuple:
    """Проверка статуса транзакции по ID без HTML.

    :param transaction_id: ID транзакции (целое число).
    :return: JSON ответ с информацией о транзакции или ошибкой (кортеж).
             Успех (200) или ошибка (404).
    """
    transaction = db.session.get(Transaction, transaction_id)

    if not transaction:
        return jsonify({"error": "Транзакция не найдена."}), 404

    return (
        jsonify(
            {
                "id": transaction.id,
                "amount": transaction.amount,
                "commission": transaction.commission,
                "status": transaction.status,
                "created_at": transaction.created_at.isoformat(),  # Преобразование даты в ISO формат
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
