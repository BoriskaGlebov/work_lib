from flask import current_app
from flask.cli import AppGroup
from models import db, User

admin_commands = AppGroup('admin')

@admin_commands.command('create-admin')
def create_admin():
    """Создание дефолтного администратора."""
    with current_app.app_context():
        # Проверьте, существует ли администратор
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Администратор уже существует.")
            return

        # Создание нового администратора
        new_admin = User(
            username='admin',
            email='admin@example.com',
            balance=0.0,
            commission_rate=0.0,
            webhook_url=None,
        )
        new_admin.set_password('admin_password')  # Установите пароль для администратора

        db.session.add(new_admin)
        db.session.commit()
        print(new_admin)
        print("Дефолтный администратор создан.")