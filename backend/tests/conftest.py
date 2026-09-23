"""Pytest fixtures and configuration for AlfaazStudio backend."""

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.base import Base
from app.db.models import VoiceProfile
from app.db.session import get_db
from app.main import app

# Use isolated in-memory SQLite database for test suite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session", autouse=True)
def set_test_env() -> None:
    """Configure environment for testing."""
    os.environ["APP_ENV"] = "testing"
    os.environ["DEBUG"] = "true"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean, isolated database session per test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an AsyncClient with database dependency overridden."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_voice(db_session: AsyncSession) -> VoiceProfile:
    """Fixture providing a saved sample VoiceProfile."""
    voice = VoiceProfile(
        name="Mirza Ghalib Voice",
        description="Classical deep baritone for historical Urdu ghazals",
        gender="male",
        language="ur",
        engine="f5-tts",
        is_preset=True,
    )
    db_session.add(voice)
    await db_session.commit()
    await db_session.refresh(voice)
    return voice
