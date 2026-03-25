from http import HTTPStatus


def test_get_token_should_return_access_token(client, user):

    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clear_password},
    )

    resp_token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in resp_token
    assert 'token_type' in resp_token
    assert resp_token['token_type'] == 'bearer'


def test_get_token_should_return_error_invalid_email(client, user):

    response = client.post(
        '/auth/token',
        data={
            'username': 'invaliduser@example.com',
            'password': user.clear_password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_should_return_error_invalid_password(client, user):

    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'invalidpassword'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
