"""Tests for config.py Settings validation."""

from pathlib import Path


class TestSettings:
    def test_defaults_without_env_file(self, monkeypatch: object, tmp_path: Path) -> None:
        """Settings should load with all defaults when no .env is present."""
        import config

        s = config.Settings(_env_file=str(tmp_path / "nonexistent.env"))  # type: ignore[call-arg]
        assert s.app_env == "development"
        assert s.debug is False
        assert s.database_url is None
        assert s.secret_key is None
        assert s.allowed_origins == ["http://localhost:8000"]

    def test_debug_defaults_to_false(self) -> None:
        from config import Settings

        s = Settings(_env_file="nonexistent")  # type: ignore[call-arg]
        assert s.debug is False

    def test_database_url_is_optional(self) -> None:
        from config import Settings

        s = Settings(_env_file="nonexistent")  # type: ignore[call-arg]
        assert s.database_url is None

    def test_secret_key_is_optional(self) -> None:
        from config import Settings

        s = Settings(_env_file="nonexistent")  # type: ignore[call-arg]
        assert s.secret_key is None

    def test_allowed_origins_default(self) -> None:
        from config import Settings

        s = Settings(_env_file="nonexistent")  # type: ignore[call-arg]
        assert "http://localhost:8000" in s.allowed_origins

    def test_allowed_origins_from_env(self, monkeypatch: object) -> None:
        import pytest

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("ALLOWED_ORIGINS", '["https://example.com","https://staging.example.com"]')
            from config import Settings

            s = Settings(_env_file="nonexistent")  # type: ignore[call-arg]
        assert "https://example.com" in s.allowed_origins
        assert "https://staging.example.com" in s.allowed_origins

    def test_app_env_override(self, monkeypatch: object) -> None:
        import pytest

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("APP_ENV", "production")
            from config import Settings

            s = Settings(_env_file="nonexistent")  # type: ignore[call-arg]
        assert s.app_env == "production"

    def test_debug_override(self, monkeypatch: object) -> None:
        import pytest

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("DEBUG", "true")
            from config import Settings

            s = Settings(_env_file="nonexistent")  # type: ignore[call-arg]
        assert s.debug is True
