from datetime import timedelta
from typing import Dict

import pytest

from pydantic_obstore import BackoffConfig, ClientConfig, Config, RetryConfig


class TestClientConfig:
    """Test ClientConfig model matches obstore ClientConfig structure."""

    def test_client_config_empty(self):
        """Test ClientConfig can be created empty."""
        config = ClientConfig()

        # All fields should be None by default
        assert config.allow_http is None
        assert config.allow_invalid_certificates is None
        assert config.connect_timeout is None
        assert config.default_content_type is None
        assert config.default_headers is None
        assert config.http1_only is None
        assert config.http2_keep_alive_interval is None
        assert config.http2_keep_alive_timeout is None
        assert config.http2_keep_alive_while_idle is None
        assert config.http2_only is None
        assert config.pool_idle_timeout is None
        assert config.pool_max_idle_per_host is None
        assert config.proxy_url is None
        assert config.timeout is None
        assert config.user_agent is None

    def test_client_config_with_values(self):
        """Test ClientConfig with all fields populated."""
        config = ClientConfig(
            allow_http=True,
            allow_invalid_certificates=False,
            connect_timeout=timedelta(seconds=30),
            default_content_type="application/json",
            default_headers={"User-Agent": "test-client"},
            http1_only=False,
            http2_keep_alive_interval="30s",
            http2_keep_alive_timeout=timedelta(seconds=10),
            http2_keep_alive_while_idle="true",
            http2_only=True,
            pool_idle_timeout=timedelta(minutes=5),
            pool_max_idle_per_host="10",
            proxy_url="http://proxy.example.com:8080",
            timeout=timedelta(minutes=2),
            user_agent="my-app/1.0",
        )

        assert config.allow_http is True
        assert config.allow_invalid_certificates is False
        assert config.connect_timeout == timedelta(seconds=30)
        assert config.default_content_type == "application/json"
        assert config.default_headers == {"User-Agent": "test-client"}
        assert config.http1_only is False
        assert config.http2_keep_alive_interval == "30s"
        assert config.http2_keep_alive_timeout == timedelta(seconds=10)
        assert config.http2_keep_alive_while_idle == "true"
        assert config.http2_only is True
        assert config.pool_idle_timeout == timedelta(minutes=5)
        assert config.pool_max_idle_per_host == "10"
        assert config.proxy_url == "http://proxy.example.com:8080"
        assert config.timeout == timedelta(minutes=2)
        assert config.user_agent == "my-app/1.0"

    def test_client_config_timeout_string_values(self):
        """Test ClientConfig accepts string timeout values."""
        config = ClientConfig(
            connect_timeout="30s",
            http2_keep_alive_timeout="10s",
            pool_idle_timeout="5m",
            timeout="2m",
        )

        assert config.connect_timeout == "30s"
        assert config.http2_keep_alive_timeout == "10s"
        assert config.pool_idle_timeout == "5m"
        assert config.timeout == "2m"

    def test_client_config_headers_types(self):
        """Test ClientConfig accepts different header types."""
        # String headers
        config1 = ClientConfig(default_headers={"Content-Type": "application/json"})
        assert config1.default_headers == {"Content-Type": "application/json"}

        # Bytes headers
        config2 = ClientConfig(default_headers={"Content-Type": b"application/json"})
        assert config2.default_headers == {"Content-Type": b"application/json"}

        # Mixed headers - bytes values are preserved
        config3 = ClientConfig(
            default_headers={
                "Content-Type": "application/json",
                "Authorization": b"Bearer token",
            }
        )
        assert config3.default_headers["Content-Type"] == "application/json"
        assert config3.default_headers["Authorization"] == b"Bearer token"

    def test_client_config_validation_errors(self):
        """Test ClientConfig validation for invalid values."""
        # Invalid headers type
        with pytest.raises(ValueError):
            ClientConfig(default_headers=["not", "a", "dict"])

        # Invalid boolean type
        with pytest.raises(ValueError):
            ClientConfig(allow_http="not-a-bool")

    def test_client_config_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValueError):
            ClientConfig(unknown_field="value")

    def test_client_config_serialization(self):
        """Test ClientConfig serialization and deserialization."""
        original = ClientConfig(
            allow_http=True,
            timeout=timedelta(seconds=30),
            default_headers={"User-Agent": "test"},
        )

        # Test model_dump
        as_dict = original.model_dump()
        assert as_dict["allow_http"] is True
        assert as_dict["timeout"] == timedelta(seconds=30)
        assert as_dict["default_headers"] == {"User-Agent": "test"}

        # Test reconstruction
        reconstructed = ClientConfig(**as_dict)
        assert reconstructed.allow_http == original.allow_http
        assert reconstructed.timeout == original.timeout
        assert reconstructed.default_headers == original.default_headers


class TestBackoffConfig:
    """Test BackoffConfig model matches obstore BackoffConfig structure."""

    def test_backoff_config_empty(self):
        """Test BackoffConfig can be created empty."""
        config = BackoffConfig()

        assert config.base is None
        assert config.init_backoff is None
        assert config.max_backoff is None

    def test_backoff_config_with_values(self):
        """Test BackoffConfig with all fields populated."""
        config = BackoffConfig(
            base=2.0,
            init_backoff=timedelta(milliseconds=100),
            max_backoff=timedelta(seconds=15),
        )

        assert config.base == 2.0
        assert config.init_backoff == timedelta(milliseconds=100)
        assert config.max_backoff == timedelta(seconds=15)

    def test_backoff_config_base_types(self):
        """Test BackoffConfig accepts int and float for base."""
        # Integer base
        config1 = BackoffConfig(base=2)
        assert config1.base == 2

        # Float base
        config2 = BackoffConfig(base=1.5)
        assert config2.base == 1.5

    def test_backoff_config_validation_errors(self):
        """Test BackoffConfig validation for invalid values."""
        with pytest.raises(ValueError):
            BackoffConfig(base="invalid")  # Should be int or float

        with pytest.raises(ValueError):
            BackoffConfig(init_backoff="invalid")  # Should be timedelta

    def test_backoff_config_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValueError):
            BackoffConfig(unknown_field="value")

    def test_backoff_config_serialization(self):
        """Test BackoffConfig serialization and deserialization."""
        original = BackoffConfig(
            base=2.0,
            init_backoff=timedelta(milliseconds=100),
            max_backoff=timedelta(seconds=15),
        )

        # Test model_dump
        as_dict = original.model_dump()
        assert as_dict["base"] == 2.0
        assert as_dict["init_backoff"] == timedelta(milliseconds=100)
        assert as_dict["max_backoff"] == timedelta(seconds=15)

        # Test reconstruction
        reconstructed = BackoffConfig(**as_dict)
        assert reconstructed.base == original.base
        assert reconstructed.init_backoff == original.init_backoff
        assert reconstructed.max_backoff == original.max_backoff


class TestRetryConfig:
    """Test RetryConfig model matches obstore RetryConfig structure."""

    def test_retry_config_empty(self):
        """Test RetryConfig can be created empty."""
        config = RetryConfig()

        assert config.backoff is None
        assert config.max_retries is None
        assert config.retry_timeout is None

    def test_retry_config_with_values(self):
        """Test RetryConfig with all fields populated."""
        backoff = BackoffConfig(base=2, init_backoff=timedelta(milliseconds=100))
        config = RetryConfig(
            backoff=backoff, max_retries=10, retry_timeout=timedelta(minutes=3)
        )

        assert config.backoff == backoff
        assert config.max_retries == 10
        assert config.retry_timeout == timedelta(minutes=3)

    def test_retry_config_nested_backoff(self):
        """Test RetryConfig with nested BackoffConfig."""
        config = RetryConfig(
            backoff=BackoffConfig(
                base=1.5,
                init_backoff=timedelta(milliseconds=50),
                max_backoff=timedelta(seconds=30),
            ),
            max_retries=5,
        )

        assert isinstance(config.backoff, BackoffConfig)
        assert config.backoff.base == 1.5
        assert config.backoff.init_backoff == timedelta(milliseconds=50)
        assert config.backoff.max_backoff == timedelta(seconds=30)
        assert config.max_retries == 5

    def test_retry_config_backoff_from_dict(self):
        """Test RetryConfig can create BackoffConfig from dict."""
        config = RetryConfig(
            backoff={
                "base": 2,
                "init_backoff": timedelta(milliseconds=100),
                "max_backoff": timedelta(seconds=15),
            },
            max_retries=10,
        )

        assert isinstance(config.backoff, BackoffConfig)
        assert config.backoff.base == 2
        assert config.backoff.init_backoff == timedelta(milliseconds=100)
        assert config.backoff.max_backoff == timedelta(seconds=15)

    def test_retry_config_validation_errors(self):
        """Test RetryConfig validation for invalid values."""
        with pytest.raises(ValueError):
            RetryConfig(max_retries="invalid")  # Should be int

        with pytest.raises(ValueError):
            RetryConfig(retry_timeout="invalid")  # Should be timedelta

        with pytest.raises(ValueError):
            RetryConfig(backoff="invalid")  # Should be BackoffConfig or dict

    def test_retry_config_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValueError):
            RetryConfig(unknown_field="value")

    def test_retry_config_serialization(self):
        """Test RetryConfig serialization and deserialization."""
        original = RetryConfig(
            backoff=BackoffConfig(base=2.0),
            max_retries=10,
            retry_timeout=timedelta(minutes=3),
        )

        # Test model_dump
        as_dict = original.model_dump()
        assert isinstance(as_dict["backoff"], dict)
        assert as_dict["backoff"]["base"] == 2.0
        assert as_dict["max_retries"] == 10
        assert as_dict["retry_timeout"] == timedelta(minutes=3)

        # Test reconstruction
        reconstructed = RetryConfig(**as_dict)
        assert isinstance(reconstructed.backoff, BackoffConfig)
        assert reconstructed.backoff.base == original.backoff.base
        assert reconstructed.max_retries == original.max_retries
        assert reconstructed.retry_timeout == original.retry_timeout


class TestConfig:
    """Test Config model that combines ClientConfig and RetryConfig."""

    def test_config_empty(self):
        """Test Config can be created empty."""
        config = Config()

        assert config.client_options is None
        assert config.retry_options is None

    def test_config_with_values(self):
        """Test Config with both client and retry options."""
        client_config = ClientConfig(allow_http=True, timeout=timedelta(seconds=30))
        retry_config = RetryConfig(max_retries=5)

        config = Config(client_options=client_config, retry_options=retry_config)

        assert config.client_options == client_config
        assert config.retry_options == retry_config
        assert isinstance(config.client_options, ClientConfig)
        assert isinstance(config.retry_options, RetryConfig)

    def test_config_from_dicts(self):
        """Test Config can create nested configs from dicts."""
        config = Config(
            client_options={"allow_http": True, "timeout": timedelta(seconds=30)},
            retry_options={
                "max_retries": 5,
                "backoff": {"base": 2, "init_backoff": timedelta(milliseconds=100)},
            },
        )

        assert isinstance(config.client_options, ClientConfig)
        assert config.client_options.allow_http is True
        assert config.client_options.timeout == timedelta(seconds=30)

        assert isinstance(config.retry_options, RetryConfig)
        assert config.retry_options.max_retries == 5
        assert isinstance(config.retry_options.backoff, BackoffConfig)
        assert config.retry_options.backoff.base == 2

    def test_config_serialization(self):
        """Test Config serialization and deserialization."""
        original = Config(
            client_options=ClientConfig(allow_http=True),
            retry_options=RetryConfig(max_retries=10),
        )

        # Test model_dump
        as_dict = original.model_dump()
        assert isinstance(as_dict["client_options"], dict)
        assert isinstance(as_dict["retry_options"], dict)
        assert as_dict["client_options"]["allow_http"] is True
        assert as_dict["retry_options"]["max_retries"] == 10

        # Test reconstruction
        reconstructed = Config(**as_dict)
        assert isinstance(reconstructed.client_options, ClientConfig)
        assert isinstance(reconstructed.retry_options, RetryConfig)
        assert (
            reconstructed.client_options.allow_http
            == original.client_options.allow_http
        )
        assert (
            reconstructed.retry_options.max_retries
            == original.retry_options.max_retries
        )

    def test_config_partial_options(self):
        """Test Config with only one type of options."""
        # Only client options
        config1 = Config(client_options=ClientConfig(allow_http=True))
        assert isinstance(config1.client_options, ClientConfig)
        assert config1.retry_options is None

        # Only retry options
        config2 = Config(retry_options=RetryConfig(max_retries=5))
        assert config2.client_options is None
        assert isinstance(config2.retry_options, RetryConfig)

    def test_config_matches_obstore_usage_pattern(self):
        """Test that Config can be used in the same way as obstore expects."""
        # This tests the pattern used in obstore store constructors
        config = Config(
            client_options=ClientConfig(
                allow_http=True,
                timeout=timedelta(seconds=60),
                default_headers={"User-Agent": "pydantic-obstore/1.0"},
            ),
            retry_options=RetryConfig(
                max_retries=3,
                retry_timeout=timedelta(minutes=1),
                backoff=BackoffConfig(
                    base=2,
                    init_backoff=timedelta(milliseconds=100),
                    max_backoff=timedelta(seconds=10),
                ),
            ),
        )

        # Convert to dict format that obstore would expect
        client_dict = (
            config.client_options.model_dump(exclude_none=True)
            if config.client_options
            else {}
        )
        retry_dict = (
            config.retry_options.model_dump(exclude_none=True)
            if config.retry_options
            else {}
        )

        # Verify the structure matches what obstore expects
        assert "allow_http" in client_dict
        assert "timeout" in client_dict
        assert "default_headers" in client_dict

        assert "max_retries" in retry_dict
        assert "retry_timeout" in retry_dict
        assert "backoff" in retry_dict
        assert isinstance(retry_dict["backoff"], dict)
        assert "base" in retry_dict["backoff"]
        assert "init_backoff" in retry_dict["backoff"]
        assert "max_backoff" in retry_dict["backoff"]
