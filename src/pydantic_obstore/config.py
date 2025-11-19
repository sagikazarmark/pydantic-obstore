from datetime import timedelta
from typing import Dict, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientConfig(BaseModel):
    """
    HTTP client configuration for Obstore.

    See https://developmentseed.org/obstore/latest/api/store/config/#obstore.store.ClientConfig
    """

    model_config = ConfigDict(extra="forbid")

    allow_http: bool | None = Field(
        default=None,
        description="Allow non-TLS, i.e. non-HTTPS connections",
    )

    allow_invalid_certificates: bool | None = Field(
        default=None,
        description="Skip certificate validation on https connections",
    )

    connect_timeout: str | timedelta | None = Field(
        default=None,
        description="Timeout for only the connect phase of a Client",
    )

    default_content_type: str | None = Field(
        default=None,
        description="Default `CONTENT_TYPE` for uploads",
    )

    default_headers: Dict[str, Union[str, bytes]] | None = Field(
        default=None,
        description="Default headers to be sent with each request",
    )

    http1_only: bool | None = Field(
        default=None,
        description="Only use http1 connections.",
    )

    http2_keep_alive_interval: str | None = Field(
        default=None,
        description="Interval for HTTP2 Ping frames should be sent to keep a connection alive",
    )

    http2_keep_alive_timeout: str | timedelta | None = Field(
        default=None,
        description="Timeout for receiving an acknowledgement of the keep-alive ping",
    )

    http2_keep_alive_while_idle: str | None = Field(
        default=None,
        description="Enable HTTP2 keep alive pings for idle connections",
    )

    http2_only: bool | None = Field(
        default=None,
        description="Only use http2 connections",
    )

    pool_idle_timeout: str | timedelta | None = Field(
        default=None,
        description=(
            "The pool max idle timeout."
            "This is the length of time an idle connection will be kept alive."
        ),
    )

    pool_max_idle_per_host: str | None = Field(
        default=None,
        description="Maximum number of idle connections per host",
    )

    proxy_url: str | None = Field(
        default=None,
        description="HTTP proxy to use for requests.",
    )

    timeout: str | timedelta | None = Field(
        default=None,
        description=(
            "Request timeout."
            "The timeout is applied from when the request starts connecting until the "
            "response body has finished."
        ),
    )

    user_agent: str | None = Field(
        default=None,
        description="User-Agent header to be used by this client",
    )

    @field_validator(
        "connect_timeout",
        "http2_keep_alive_timeout",
        "pool_idle_timeout",
        "timeout",
        mode="before",
    )
    @classmethod
    def validate_timeout_fields(cls, v):
        """Validate timeout fields accept both timedelta and string values."""
        if v is None:
            return v
        if isinstance(v, (str, timedelta)):
            return v
        raise ValueError("Timeout fields must be string, timedelta, or None")


class BackoffConfig(BaseModel):
    """
    Exponential backoff with jitter configuration for Obstore.

    See https://developmentseed.org/obstore/latest/api/store/config/#obstore.store.BackoffConfig
    """

    model_config = ConfigDict(extra="forbid")

    base: int | float | None = Field(
        default=None,
        description="The base of the exponential to use. Defaults to 2",
    )

    init_backoff: timedelta | None = Field(
        default=None,
        description="The initial backoff duration. Defaults to 100 milliseconds",
    )

    max_backoff: timedelta | None = Field(
        default=None,
        description="The maximum backoff duration. Defaults to 15 seconds",
    )


class RetryConfig(BaseModel):
    """
    Configuration for how to respond to request errors in Obstore.

    The following categories of error will be retried:
    - 5xx server errors
    - Connection errors
    - Dropped connections
    - Timeouts for safe / read-only requests

    See https://developmentseed.org/obstore/latest/api/store/config/#obstore.store.RetryConfig
    """

    model_config = ConfigDict(extra="forbid")

    backoff: BackoffConfig | None = Field(
        default=None,
        description="The backoff configuration. Defaults to the values listed above if not provided",
    )

    max_retries: int | None = Field(
        default=None,
        description="The maximum number of times to retry a request. Set to 0 to disable retries. Defaults to 10",
    )

    retry_timeout: timedelta | None = Field(
        default=None,
        description=(
            "The maximum length of time from the initial request after which no further "
            "retries will be attempted. Defaults to 3 minutes"
        ),
    )


class Config(BaseModel):
    """
    Configuration for Obstore.
    """

    client_options: ClientConfig | None = None
    retry_options: RetryConfig | None = None
