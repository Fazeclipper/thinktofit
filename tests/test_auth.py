def register(client, email='test@example.com', password='password123'):
    return client.post('/register', data={
        'name': 'Test User', 'email': email,
        'password': password, 'confirm_password': password,
    }, follow_redirects=True)


def test_register_creates_account(client):
    resp = register(client)
    assert resp.status_code == 200


def test_duplicate_registration_rejected(client):
    register(client, email='dupe@example.com')
    client.get('/logout')
    resp = register(client, email='dupe@example.com')
    assert b'already exists' in resp.data


def test_login_with_correct_credentials(client):
    register(client, email='login@example.com', password='password123')
    client.get('/logout')
    resp = client.post('/login', data={
        'email': 'login@example.com', 'password': 'password123',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Incorrect email or password' not in resp.data


def test_login_with_wrong_password(client):
    register(client, email='wrong@example.com', password='password123')
    client.get('/logout')
    resp = client.post('/login', data={
        'email': 'wrong@example.com', 'password': 'not-the-password',
    }, follow_redirects=True)
    assert b'Incorrect email or password' in resp.data


def test_logout_then_dashboard_requires_login(client):
    register(client, email='logout@example.com')
    client.get('/logout')
    resp = client.get('/dashboard', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']
