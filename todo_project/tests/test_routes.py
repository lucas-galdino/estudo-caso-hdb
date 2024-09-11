import pytest
from todo_project import app, db
from todo_project.models import User, Task

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

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Manager" in response.data

def test_register(client):
    response = client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Account Created For" in response.data
    assert b"user" in response.data

def test_login_success(client):
    # Register a user
    client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    })
    # Login
    response = client.post('/login', data={
        'username': 'user',
        'password': 'senha'
    }, follow_redirects=True)
    print(response.data)
    assert response.status_code == 200
    assert b"Login Successfull" in response.data

def test_login_unsuccessful(client):
    # Register a user
    client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    })
    
    # Attempt to login with incorrect password
    response = client.post('/login', data={
        'username': 'user',
        'password': 'wrong_password'
    }, follow_redirects=True)
    
    print("Login Response (Incorrect Credentials):", response.data)
    assert response.status_code == 200
    assert b"Login Unsuccessful" in response.data
    assert b"Please check Username Or Password" in response.data

def test_login_user_does_not_exist(client):
    # Register a user
    client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    })
     # Attempt to login with non-existent username
    response = client.post('/login', data={
        'username': 'auser',
        'password': 'senha'
    }, follow_redirects=True)
    
    print("Login Response (Non-existent User):", response.data)
    assert response.status_code == 200
    assert b"Login Unsuccessful" in response.data
    assert b"Please check Username Or Password" in response.data


def test_logout(client):
    # Register and login a user
    register_response = client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    })
    login_response = client.post('/login', data={
        'username': 'user',
        'password': 'senha'
    }, follow_redirects=True)
    print("Login Response:", login_response.data)
    print("Register Response:", register_response.data)
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data



def test_create_task(client):
    # Register and login
    client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    })
    client.post('/login', data={
        'username': 'user',
        'password': 'senha'
    })
    # Create task
    response = client.post('/add_task', data={
        'task_name': 'task'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Task Created" in response.data

def test_update_task(client):

    client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    })
    client.post('/login', data={
        'username': 'user',
        'password': 'senha'
    })
    
    response = client.post('/add_task', data={
        'task_name': 'Original Task'
    }, follow_redirects=True)
    assert b"Task Created" in response.data
    
    task = Task.query.filter_by(content='Original Task').first()
    assert task is not None
    
    response = client.post(f'/all_tasks/{task.id}/update_task', data={
        'task_name': 'Updated Task'
    }, follow_redirects=True)
    assert b"Task Updated" in response.data
    
    updated_task = Task.query.get(task.id)
    assert updated_task.content == 'Updated Task'
    
    response = client.get('/all_tasks')
    assert b"Updated Task" in response.data

def test_delete_task(client):

    client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    })
    client.post('/login', data={
        'username': 'user',
        'password': 'senha'
    })
    
    response = client.post('/add_task', data={
        'task_name': 'Task to be deleted'
    }, follow_redirects=True)
    assert b"Task Created" in response.data
    
    task = Task.query.filter_by(content='Task to be deleted').first()
    assert task is not None
    
    response = client.get(f'/all_tasks/{task.id}/delete_task', follow_redirects=True)
    assert b"Task Deleted" in response.data
    
    deleted_task = Task.query.get(task.id)
    assert deleted_task is None
    
    response = client.get('/all_tasks')
    assert b"Task to be deleted" not in response.data

def test_view_all_tasks(client):

    client.post('/register', data={
        'username': 'user',
        'password': 'senha',
        'confirm_password': 'senha'
    })
    client.post('/login', data={
        'username': 'user',
        'password': 'senha'
    })
    
    tasks = ['Task 1', 'Task 2', 'Task 3']
    for task in tasks:
        client.post('/add_task', data={'task_name': task}, follow_redirects=True)
    
    response = client.get('/all_tasks')
    
    assert response.status_code == 200
    for task in tasks:
        assert task.encode() in response.data
    
    assert response.data.count(b'<tr>') == len(tasks)

    print("All tasks response:", response.data)

def test_update_username(client):

    client.post('/register', data={'username': 'user', 'password': 'senha', 'confirm_password': 'senha'})
    client.post('/login', data={'username': 'user', 'password': 'senha'})
    
    response = client.post('/account', data={'username': 'newuser'}, follow_redirects=True)
    assert b"Username Updated Successfully" in response.data
   
    user = User.query.filter_by(username='newuser').first()
    assert user is not None

def test_invalid_registration(client):
    response = client.post('/register', data={
        'username': 'u',  
        'password': 'senha',
        'confirm_password': 'senh' 
    }, follow_redirects=True)
    assert b"Field must be between 3 and 10 characters long" in response.data
    assert b"Field must be equal to password" in response.data

def test_404_error(client):
    response = client.get('/a')
    assert response.status_code == 404
    assert b"Not Found" in response.data 

def test_protected_route_access(client):
    response = client.get('/all_tasks', follow_redirects=True)
    assert b"Please log in to access this page" in response.data