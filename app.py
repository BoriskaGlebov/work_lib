from datetime import datetime

from flask import Flask, request, redirect, url_for, render_template, jsonify

from models import db, User, Transaction
from config import Config
from commands import admin_commands

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    user1 = User(balance=100,
                 username="testUser",
                 commission_rate=10,
                 email="user@email.ru",
                 password_hash=123,
                 webhook_url="http://localhosts")  # Создание базы данных и таблиц
    user1.set_password(password='123')
    tranz = Transaction(amount=100, commission=10, status='confirmed', user_id=1)
    db.session.add_all([user1, tranz])
    db.session.commit()

app.cli.add_command(admin_commands)


@app.route('/')
def dashboard():
    """Дашборд."""
    total_users = User.query.count()
    total_transactions = Transaction.query.count()

    today_transactions = Transaction.query.filter(Transaction.created_at >= datetime.now().date()).all()
    total_amount_today = sum(transaction.amount for transaction in today_transactions)

    recent_transactions = Transaction.query.order_by(Transaction.id.desc()).limit(5).all()

    return render_template('dashboard.html', total_users=total_users,
                           total_transactions=total_transactions,
                           total_amount_today=total_amount_today,
                           recent_transactions=recent_transactions)


@app.route('/users', methods=['GET', 'POST'])
def users():
    """Страница пользователей."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('users'))
    #
    user_list = User.query.all()
    return render_template('users.html', users=user_list)


@app.route('/transactions', methods=['GET'])
def transactions():
    """Страница транзакций."""
    transaction_list = Transaction.query.all()
    return render_template('transactions.html', transactions=transaction_list)


@app.route('/transactions/<int:transaction_id>', methods=['GET', 'POST'])
def transaction_detail(transaction_id):
    """Детальный просмотр транзакции."""
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == 'POST':
        status = request.form['status']
        if status in ['confirmed', 'canceled'] and transaction.status == 'pending':
            transaction.status = status
            db.session.commit()
            return redirect(url_for('transactions'))

    return render_template('transaction_detail.html', transaction=transaction)


@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.json

    # Проверка наличия обязательного параметра amount
    if 'amount' not in data:
        return jsonify({"error": "Поле 'amount' обязательно для заполнения."}), 400

    amount = data['amount']
    user = data['user_id']

    # Создание новой транзакции
    transaction = Transaction(amount=amount, user_id=user)

    # Расчет комиссии
    transaction.calculate_commission()

    # Сохранение транзакции в базе данных
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"id": transaction.id}), 201


@app.route('/cancel_transaction', methods=['POST'])
def cancel_transaction():
    """Отмена транзакции по ID."""
    data = request.json

    # Проверка наличия обязательного параметра id
    if 'id' not in data:
        return jsonify({"error": "Поле 'id' обязательно для заполнения."}), 400

    transaction_id = data['id']

    # Получение транзакции из базы данных
    transaction = Transaction.query.get(transaction_id)

    if not transaction:
        return jsonify({"error": "Транзакция не найдена."}), 404

    # Проверка статуса транзакции
    if transaction.status == 'pending':
        transaction.status = 'canceled'
        db.session.commit()
        return jsonify({"message": "Транзакция отменена.", "transaction_id": transaction.id}), 200

    return jsonify({"error": "Невозможно отменить транзакцию с текущим статусом."}), 400


@app.route('/check_transaction/<int:transaction_id>', methods=['GET'])
def check_transaction(transaction_id):
    """Проверка статуса транзакции по ID."""
    transaction = Transaction.query.get(transaction_id)

    if not transaction:
        return jsonify({"error": "Транзакция не найдена."}), 404

    return jsonify({
        "id": transaction.id,
        "amount": transaction.amount,
        "commission": transaction.commission,
        "status": transaction.status,
        "created_at": transaction.created_at.isoformat()  # Преобразование даты в ISO формат
    }), 200


if __name__ == "__main__":
    app.run(debug=True)