import os

import pytest
from app import app, db
from models import User


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY']='test_key'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def create_admin_user(client):
    """Create an admin user for testing."""
    admin_user = User(username='admin', is_admin=True)
    db.session.add(admin_user)
    db.session.commit()
    return admin_user