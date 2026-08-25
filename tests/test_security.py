from models import User


def test_password_is_hashed_not_plaintext(client):
    client.post('/register', data={
        'name': 'Hash Check', 'email': 'hash@example.com',
        'password': 'password123', 'confirm_password': 'password123',
    })
    user = User.query.filter_by(email='hash@example.com').first()
    assert user is not None
    assert user.password_hash != 'password123'
    assert user.check_password('password123')
    assert not user.check_password('wrong-password')


def test_admin_route_blocks_non_admin(client):
    client.post('/register', data={
        'name': 'Regular User', 'email': 'regular@example.com',
        'password': 'password123', 'confirm_password': 'password123',
    })
    resp = client.get('/admin')
    assert resp.status_code == 403


def test_admin_route_blocks_anonymous(client):
    resp = client.get('/admin', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_profile_requires_login(client):
    resp = client.get('/profile', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']
