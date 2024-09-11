import pytest
from todo_project import app, db
from todo_project.models import User, Task
from datetime import datetime


@pytest.fixture(autouse=True)
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False 
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_new_user():
    user = User(username='testuser', password='password123')
    assert user.username == 'testuser'
    assert user.password == 'password123'
    assert user.tasks == []

def test_user_repr():
    user = User(username='testuser', password='password123')
    assert repr(user) == "User('testuser')"

def test_new_task():
    user = User(username='testuser', password='password123')
    task = Task(content='Test task', author=user, date_posted=datetime.utcnow())
    assert task.content == 'Test task'
    assert task.author == user
    assert isinstance(task.date_posted, datetime)

def test_task_repr():
    task = Task(content='Test task', user_id=1)
    assert repr(task) == f"Task('Test task', '{task.date_posted}', '1')"

def test_user_task_relationship():
    user = User(username='testuser', password='password123')
    task1 = Task(content='Task 1', author=user)
    task2 = Task(content='Task 2', author=user)
    assert len(user.tasks) == 2
    assert task1 in user.tasks
    assert task2 in user.tasks



