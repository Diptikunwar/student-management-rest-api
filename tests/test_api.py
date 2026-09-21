from new import app


def test_login_success():
    client = app.test_client()

    response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    assert response.status_code == 200
    assert 'token' in response.get_json()


def test_login_invalid_password():
    client = app.test_client()

    response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'wrongpassword'
        }
    )

    assert response.status_code == 401
    assert response.get_json()['error'] == 'Invalid username or password'


def test_fetch_all_without_token():
    client = app.test_client()

    response = client.get('/fetchAll')

    assert response.status_code == 401
    assert response.get_json()['error'] == 'Token is missing'

def test_fetch_all_with_token():
    client = app.test_client()

    login_response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    token = login_response.get_json()['token']

    response = client.get(
        '/fetchAll',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code == 200   

def test_add_student_invalid_mark():
    client = app.test_client()

    login_response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    token = login_response.get_json()['token']

    response = client.post(
        '/addStudent',
        json={
            'name': 'Invalid Student',
            'mark': 150
        },
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Mark must be between 0 and 100' 

def test_fetch_student_not_found():
    client = app.test_client()

    login_response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    token = login_response.get_json()['token']

    response = client.get(
        '/fetchById/99999',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code == 404
    assert response.get_json()['error'] == 'Student not found'       
def test_delete_student_not_found():
    client = app.test_client()

    login_response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    token = login_response.get_json()['token']

    response = client.delete(
        '/delete/99999',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code == 404
    assert response.get_json()['error'] == 'Student not found'

def test_search_without_name():
    client = app.test_client()

    login_response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    token = login_response.get_json()['token']

    response = client.get(
        '/search',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Search name is required'    
def test_add_student_success():
    client = app.test_client()

    login_response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    token = login_response.get_json()['token']

    response = client.post(
        '/addStudent',
        json={
            'name': 'Pytest Student',
            'mark': 88
        },
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code == 201
    assert response.get_json()['message'] == 'Student added successfully'

def test_update_student_not_found():
    client = app.test_client()

    login_response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    token = login_response.get_json()['token']

    response = client.put(
        '/update',
        json={
            'id': 99999,
            'name': 'Updated Student',
            'mark': 90
        },
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code == 404
    assert response.get_json()['error'] == 'Student not found'

def test_post_list_invalid_mark():
    client = app.test_client()

    login_response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    token = login_response.get_json()['token']

    response = client.post(
        '/postList',
        json=[
            {
                'name': 'Invalid Bulk Student',
                'mark': 150
            }
        ],
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Mark must be between 0 and 100'    