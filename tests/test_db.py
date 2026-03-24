from dataclasses import asdict

from sqlalchemy import select

from fastapi_zero.models import User


def test_create_user_should_create_user_in_db(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='john_doe',
            email='john_doe@example.com',
            password='securepassword',
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'john_doe'))
        assert asdict(user) == {
            'id': 1,
            'username': 'john_doe',
            'email': 'john_doe@example.com',
            'password': 'securepassword',
            'created_at': time,
        }
