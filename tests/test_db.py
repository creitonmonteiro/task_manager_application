from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero import database
from fastapi_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user_should_create_user_in_db(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='john_doe',
            email='john_doe@example.com',
            password='securepassword',
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'john_doe')
        )
        assert asdict(user) == {
            'id': 1,
            'username': 'john_doe',
            'email': 'john_doe@example.com',
            'password': 'securepassword',
            'created_at': time,
            'updated_at': time,
            'todos': [],
        }


@pytest.mark.asyncio
async def test_get_session_should_return_session():

    session_generator = database.get_session()

    db_session = await anext(session_generator)

    assert isinstance(db_session, AsyncSession)

    await session_generator.aclose()


@pytest.mark.asyncio
async def test_create_todo_should_create_todo_in_db(session, user):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == {
        'description': 'Test Desc',
        'id': 1,
        'state': 'draft',
        'title': 'Test Todo',
        'user_id': 1,
        'created_at': todo.created_at,
        'updated_at': todo.updated_at,
    }


@pytest.mark.asyncio
async def test_user_todo_should_have_relationship(session, user: User):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
