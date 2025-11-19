from datetime import datetime, timezone

import pytest

from pydantic_obstore import GetOptions


class TestGetOptions:
    """Test GetOptions model matches obstore GetOptions structure."""

    def test_get_options_empty(self):
        """Test GetOptions can be created empty."""
        options = GetOptions()

        # All fields should be None by default
        assert options.head is None
        assert options.if_match is None
        assert options.if_modified_since is None
        assert options.if_none_match is None
        assert options.if_unmodified_since is None
        assert options.range is None
        assert options.version is None

    def test_get_options_with_values(self):
        """Test GetOptions with all fields populated."""
        test_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        options = GetOptions(
            head=True,
            if_match="abc123",
            if_modified_since=test_time,
            if_none_match="def456",
            if_unmodified_since=test_time,
            range=(0, 1024),
            version="v1.0",
        )

        assert options.head is True
        assert options.if_match == "abc123"
        assert options.if_modified_since == test_time
        assert options.if_none_match == "def456"
        assert options.if_unmodified_since == test_time
        assert options.range == (0, 1024)
        assert options.version == "v1.0"

    def test_get_options_range_tuple(self):
        """Test GetOptions range field with tuple."""
        options = GetOptions(range=(100, 200))
        assert options.range == (100, 200)
        assert isinstance(options.range, tuple)

    def test_get_options_range_sequence(self):
        """Test GetOptions range field with sequence."""
        # List as sequence
        options1 = GetOptions(range=[100, 200])
        assert options1.range == [100, 200]

        # Other sequence types (range gets converted to list during validation)
        options2 = GetOptions(range=range(100, 201))
        assert isinstance(options2.range, list)  # Range is converted to list
        assert options2.range == list(range(100, 201))

    def test_get_options_range_dict_offset(self):
        """Test GetOptions range field with dict containing offset."""
        options = GetOptions(range={"offset": 100})
        assert options.range == {"offset": 100}
        assert isinstance(options.range, dict)

    def test_get_options_range_dict_suffix(self):
        """Test GetOptions range field with dict containing suffix."""
        options = GetOptions(range={"suffix": 100})
        assert options.range == {"suffix": 100}
        assert isinstance(options.range, dict)

    def test_get_options_datetime_with_timezone(self):
        """Test GetOptions with timezone-aware datetimes."""
        utc_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        options = GetOptions(
            if_modified_since=utc_time,
            if_unmodified_since=utc_time,
        )

        assert options.if_modified_since.tzinfo == timezone.utc
        assert options.if_unmodified_since.tzinfo == timezone.utc

    def test_get_options_datetime_naive(self):
        """Test GetOptions with naive datetimes (should still work)."""
        naive_time = datetime(2023, 1, 1, 12, 0, 0)

        options = GetOptions(
            if_modified_since=naive_time,
            if_unmodified_since=naive_time,
        )

        assert options.if_modified_since == naive_time
        assert options.if_unmodified_since == naive_time

    def test_get_options_validation_errors(self):
        """Test GetOptions validation for invalid values."""
        # Invalid head type
        with pytest.raises(ValueError):
            GetOptions(head="not-a-bool")

        # Invalid datetime
        with pytest.raises(ValueError):
            GetOptions(if_modified_since="not-a-datetime")

        # Invalid range type
        with pytest.raises(ValueError):
            GetOptions(range="invalid-range")

    def test_get_options_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValueError):
            GetOptions(unknown_field="value")

    def test_get_options_serialization(self):
        """Test GetOptions serialization and deserialization."""
        test_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        original = GetOptions(
            head=True,
            if_match="abc123",
            if_modified_since=test_time,
            range=(0, 1024),
            version="v1.0",
        )

        # Test model_dump
        as_dict = original.model_dump()
        assert as_dict["head"] is True
        assert as_dict["if_match"] == "abc123"
        assert as_dict["if_modified_since"] == test_time
        assert as_dict["range"] == (0, 1024)
        assert as_dict["version"] == "v1.0"

        # Test reconstruction
        reconstructed = GetOptions(**as_dict)
        assert reconstructed.head == original.head
        assert reconstructed.if_match == original.if_match
        assert reconstructed.if_modified_since == original.if_modified_since
        assert reconstructed.range == original.range
        assert reconstructed.version == original.version

    def test_get_options_exclude_none(self):
        """Test GetOptions serialization excluding None values."""
        options = GetOptions(
            head=True,
            if_match="abc123",
            # Other fields left as None
        )

        # Test model_dump with exclude_none
        as_dict = options.model_dump(exclude_none=True)
        expected_keys = {"head", "if_match"}
        assert set(as_dict.keys()) == expected_keys
        assert "if_modified_since" not in as_dict
        assert "range" not in as_dict

    def test_get_options_json_serialization(self):
        """Test GetOptions JSON serialization and deserialization."""
        test_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        original = GetOptions(
            head=True,
            if_match="abc123",
            if_modified_since=test_time,
            range=(0, 1024),
        )

        # Test JSON serialization
        json_str = original.model_dump_json()
        assert isinstance(json_str, str)
        assert "abc123" in json_str
        assert "2023-01-01T12:00:00Z" in json_str

        # Test JSON deserialization
        from_json = GetOptions.model_validate_json(json_str)
        assert from_json.head == original.head
        assert from_json.if_match == original.if_match
        assert from_json.if_modified_since == original.if_modified_since
        # Range tuple becomes list after JSON roundtrip
        assert from_json.range == list(original.range)

    def test_get_options_conditional_requests(self):
        """Test GetOptions for conditional request scenarios."""
        etag = 'W/"abc123"'
        last_modified = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # If-Match scenario (retrieve if etag matches)
        options1 = GetOptions(if_match=etag)
        assert options1.if_match == etag

        # If-None-Match scenario (retrieve if etag doesn't match)
        options2 = GetOptions(if_none_match=etag)
        assert options2.if_none_match == etag

        # If-Modified-Since scenario (retrieve if modified after date)
        options3 = GetOptions(if_modified_since=last_modified)
        assert options3.if_modified_since == last_modified

        # If-Unmodified-Since scenario (retrieve if not modified since date)
        options4 = GetOptions(if_unmodified_since=last_modified)
        assert options4.if_unmodified_since == last_modified

    def test_get_options_head_request(self):
        """Test GetOptions for HEAD request scenario."""
        options = GetOptions(head=True)
        assert options.head is True

        # HEAD request typically used to get metadata only
        # Should be compatible with other options
        options_with_conditions = GetOptions(
            head=True,
            if_match="abc123",
            version="v1.0",
        )
        assert options_with_conditions.head is True
        assert options_with_conditions.if_match == "abc123"
        assert options_with_conditions.version == "v1.0"

    def test_get_options_range_requests(self):
        """Test GetOptions for various range request scenarios."""
        # Byte range
        options1 = GetOptions(range=(0, 1023))  # First 1024 bytes
        assert options1.range == (0, 1023)

        # Offset from beginning
        options2 = GetOptions(range={"offset": 1024})  # Skip first 1024 bytes
        assert options2.range == {"offset": 1024}

        # Suffix range (last N bytes)
        options3 = GetOptions(range={"suffix": 1024})  # Last 1024 bytes
        assert options3.range == {"suffix": 1024}

        # List of ranges
        options4 = GetOptions(range=[0, 1023, 2048, 3071])  # Multiple ranges
        assert options4.range == [0, 1023, 2048, 3071]

    def test_get_options_version_requests(self):
        """Test GetOptions for versioned object requests."""
        # Version string
        options1 = GetOptions(version="v1.2.3")
        assert options1.version == "v1.2.3"

        # Version ID (common in S3)
        options2 = GetOptions(
            version="3/L4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X8gdRQBpUMLUo"
        )
        assert options2.version.startswith("3/L4kqtJlcpXroDTDmJ")

        # Timestamp-based version
        options3 = GetOptions(version="20230101120000")
        assert options3.version == "20230101120000"
