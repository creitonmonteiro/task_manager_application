from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_create_user_should_create_user(client):

    user_data = {
        'username': 'john_doe',
        'email': 'john_doe@example.com',
        'password': 'securepassword',
    }

    response = client.post('/users', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'john_doe',
        'email': 'john_doe@example.com',
    }


def test_create_user_should_return_error_if_username_exists(client, user):

    user_data = {
        'username': user.username,
        'email': 'new_email@example.com',
        'password': 'securepassword',
    }

    response = client.post('/users', json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_should_return_error_if_email_exists(client, user):

    user_data = {
        'username': 'new_username',
        'email': user.email,
        'password': 'securepassword',
    }

    response = client.post('/users', json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users_should_return_list_of_users(client):

    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_should_return_list_of_users_with_data(client, user):

    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user_should_be_user_updated(client, user, token):

    updated_user_data = {
        'username': 'john_doe_updated',
        'email': 'john_doe_updated@example.com',
        'password': 'newsecurepassword',
    }

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json=updated_user_data,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'john_doe_updated',
        'email': 'john_doe_updated@example.com',
    }


def test_update_integrity_error(client, user, token):

    client.post(
        '/users',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or email already exists'
    }


def test_update_invalid_user_id(client, token):

    invalid_user_id = 999

    response = client.put(
        f'/users/{invalid_user_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'john_doe_updated',
            'email': 'john_doe_updated@example.com',
            'password': 'newsecurepassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user_should_be_user_deleted(client, user, token):

    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_invalid_user_id(client, token):

    invalid_user_id = 999

    response = client.delete(
        f'/users/{invalid_user_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_read_user_should_return_user_by_id(client, user):

    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def test_read_user_should_return_error_if_user_does_not_exist(client):

    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
