from http import HTTPStatus

import pytest
from jwt import (
    DecodeError,
    ExpiredSignatureError,
    InvalidSignatureError,
    decode,
)

from task_manager import security
from task_manager.security import create_access_token, settings


def test_jwt_should_encode_and_decode_token():

    data = {'test': 'test_value'}

    token = create_access_token(data)

    decoded_data = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded_data['test'] == data['test']
    assert 'exp' in decoded_data


def test_jwt_should_invalid_token(client):

    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer invalidtoken'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_should_expire_token(monkeypatch):

    data = {'test': 'test_value'}
    monkeypatch.setattr(security.settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', -1)

    token = create_access_token(data)

    with pytest.raises(ExpiredSignatureError):
        decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_jwt_should_raise_decode_error_for_invalid_token():
    invalid_token = 'invalidtoken'

    with pytest.raises(DecodeError):
        decode(
            invalid_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )


def test_jwt_should_raise_decode_error_for_tampered_token():
    data = {'test': 'test_value'}

    token = create_access_token(data)

    header, payload, signature = token.split('.')
    tampered_signature = ('a' if signature[0] != 'a' else 'b') + signature[1:]
    tampered_token = f'{header}.{payload}.{tampered_signature}'

    with pytest.raises(InvalidSignatureError):
        decode(
            tampered_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )


def test_get_current_should_return_user_not_found(client):

    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_does_not_exists(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
