from datetime import datetime
from typing import Any, Sequence, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ObjectMeta(BaseModel):
    """
    The metadata that describes an object.

    See https://developmentseed.org/obstore/latest/api/list/#obstore.ObjectMeta
    """

    model_config = ConfigDict(extra="forbid")

    path: str = Field(description="The full path to the object")

    last_modified: datetime = Field(description="The last modified time")

    size: int = Field(description="The size in bytes of the object")

    e_tag: str | None = Field(
        default=None, description="The unique identifier for the object (RFC 9110)"
    )

    version: str | None = Field(
        default=None, description="A version indicator for this object"
    )


class GetOptions(BaseModel):
    """
    Options for a get request.

    See https://developmentseed.org/obstore/latest/api/get/#obstore.GetOptions
    """

    model_config = ConfigDict(extra="forbid")

    head: bool | None = Field(
        default=None,
        description="Request transfer of no content (RFC 9110)",
    )

    if_match: str | None = Field(
        default=None,
        description="Request will succeed if the ObjectMeta::e_tag matches otherwise returning PreconditionError",
    )

    if_modified_since: datetime | None = Field(
        default=None,
        description="Request will succeed if the object has not been modified since otherwise returning PreconditionError",
    )

    if_none_match: str | None = Field(
        default=None,
        description="Request will succeed if the ObjectMeta::e_tag does not match otherwise returning NotModifiedError",
    )

    if_unmodified_since: datetime | None = Field(
        default=None,
        description="Request will succeed if the object has been modified since",
    )

    range: Union[tuple[int, int], Sequence[int], dict[str, int], None] = Field(
        default=None,
        description="Request transfer of only the specified range of bytes. Can be (start, end), sequence of ints, or dict with 'offset' or 'suffix' key",
    )

    version: str | None = Field(
        default=None,
        description="Request a particular object version",
    )

    @field_serializer("range")
    def serialize_range(self, value: Any) -> Any:
        """Serialize range field, converting range objects to lists for JSON compatibility."""
        if isinstance(value, range):
            return list(value)
        return value
