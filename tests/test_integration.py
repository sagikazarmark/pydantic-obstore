from datetime import datetime, timedelta, timezone

import pytest

from pydantic_obstore import (
    BackoffConfig,
    ClientConfig,
    Config,
    GetOptions,
    ObjectMeta,
    RetryConfig,
)


class TestIntegration:
    """Integration tests verifying pydantic models work with obstore-like data structures."""

    @pytest.fixture
    def sample_obstore_operations_data(self):
        """Sample data that represents what obstore operations would return."""
        return {
            "head_results": [
                {
                    "path": "data/file1.txt",
                    "last_modified": datetime(
                        2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc
                    ),
                    "size": 11,
                    "e_tag": "abc123",
                    "version": None,
                },
                {
                    "path": "data/file2.json",
                    "last_modified": datetime(
                        2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc
                    ),
                    "size": 15,
                    "e_tag": "def456",
                    "version": None,
                },
            ],
            "list_results": [
                [
                    {
                        "path": "data/file1.txt",
                        "last_modified": datetime(
                            2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc
                        ),
                        "size": 11,
                        "e_tag": "abc123",
                        "version": None,
                    },
                    {
                        "path": "data/file2.json",
                        "last_modified": datetime(
                            2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc
                        ),
                        "size": 15,
                        "e_tag": "def456",
                        "version": None,
                    },
                    {
                        "path": "logs/app.log",
                        "last_modified": datetime(
                            2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc
                        ),
                        "size": 27,
                        "e_tag": "ghi789",
                        "version": None,
                    },
                ]
            ],
        }

    def test_object_meta_integration_with_obstore_operations(
        self, sample_obstore_operations_data
    ):
        """Test ObjectMeta works seamlessly with obstore-like operation results."""

        # Test head operation with ObjectMeta
        head_result = sample_obstore_operations_data["head_results"][0]
        obj_meta = ObjectMeta(**head_result)

        assert obj_meta.path == "data/file1.txt"
        assert obj_meta.size == 11
        assert isinstance(obj_meta.last_modified, datetime)
        assert obj_meta.last_modified.tzinfo == timezone.utc

        # Test list operation with ObjectMeta
        all_objects = []
        for batch in sample_obstore_operations_data["list_results"]:
            for item_dict in batch:
                obj_meta = ObjectMeta(**item_dict)
                all_objects.append(obj_meta)

        assert len(all_objects) == 3
        paths = {obj.path for obj in all_objects}
        assert paths == {"data/file1.txt", "data/file2.json", "logs/app.log"}

        # Verify all ObjectMeta instances are valid
        for obj in all_objects:
            assert isinstance(obj.path, str)
            assert isinstance(obj.last_modified, datetime)
            assert isinstance(obj.size, int)
            assert obj.size > 0

    def test_get_options_integration_with_obstore_patterns(self):
        """Test GetOptions works with obstore-like usage patterns."""
        # Simulate obstore metadata
        obj_meta_dict = {
            "path": "test/range_file.txt",
            "last_modified": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "size": 63,  # Length of "This is test content for range requests and conditional gets"
            "e_tag": "sample-etag-123",
            "version": None,
        }
        obj_meta = ObjectMeta(**obj_meta_dict)

        # Test range request with GetOptions
        range_options = GetOptions(range=(0, 10))  # First 10 bytes
        assert range_options.range == (0, 10)

        # Test head request with GetOptions
        head_options = GetOptions(head=True)
        assert head_options.head is True

        # Test conditional request options (structure verification)
        conditional_options = GetOptions(
            if_match=obj_meta.e_tag,
            if_modified_since=obj_meta.last_modified,
        )
        assert conditional_options.if_match == obj_meta.e_tag
        assert conditional_options.if_modified_since == obj_meta.last_modified

    def test_config_models_structure_for_obstore_stores(self):
        """Test that config models produce structures compatible with obstore store constructors."""
        # Create comprehensive config
        config = Config(
            client_options=ClientConfig(
                allow_http=True,
                timeout=timedelta(seconds=60),
                connect_timeout=timedelta(seconds=30),
                default_content_type="application/octet-stream",
                default_headers={"User-Agent": "pydantic-obstore-test/1.0"},
                user_agent="custom-agent/1.0",
                proxy_url="http://proxy.example.com:8080",
            ),
            retry_options=RetryConfig(
                max_retries=5,
                retry_timeout=timedelta(minutes=2),
                backoff=BackoffConfig(
                    base=2.0,
                    init_backoff=timedelta(milliseconds=100),
                    max_backoff=timedelta(seconds=30),
                ),
            ),
        )

        # Convert to format expected by obstore
        client_dict = config.client_options.model_dump(exclude_none=True)
        retry_dict = config.retry_options.model_dump(exclude_none=True)

        # Verify structure matches obstore expectations
        expected_client_keys = {
            "allow_http",
            "timeout",
            "connect_timeout",
            "default_content_type",
            "default_headers",
            "user_agent",
            "proxy_url",
        }
        assert set(client_dict.keys()) == expected_client_keys

        expected_retry_keys = {"max_retries", "retry_timeout", "backoff"}
        assert set(retry_dict.keys()) == expected_retry_keys

        # Verify nested backoff structure
        backoff_dict = retry_dict["backoff"]
        expected_backoff_keys = {"base", "init_backoff", "max_backoff"}
        assert set(backoff_dict.keys()) == expected_backoff_keys

        # Verify types are preserved correctly
        assert isinstance(client_dict["allow_http"], bool)
        assert isinstance(client_dict["timeout"], timedelta)
        assert isinstance(client_dict["default_headers"], dict)
        assert isinstance(retry_dict["max_retries"], int)
        assert isinstance(backoff_dict["base"], float)

    def test_real_world_workflow_simulation(self):
        """Test a complete workflow using pydantic models with obstore-like operations."""
        # Simulate a data processing workflow

        # 1. Setup with configuration
        config = Config(
            client_options=ClientConfig(
                timeout=timedelta(seconds=30),
                default_headers={"X-Application": "data-processor"},
            ),
            retry_options=RetryConfig(
                max_retries=3,
                backoff=BackoffConfig(base=2, init_backoff=timedelta(milliseconds=50)),
            ),
        )

        # 2. Simulate upload metadata results
        upload_metadata_dicts = [
            {
                "path": "input/dataset1.csv",
                "last_modified": datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
                "size": 25,
                "e_tag": "dataset1-hash",
                "version": None,
            },
            {
                "path": "input/dataset2.csv",
                "last_modified": datetime(2023, 1, 1, 10, 1, 0, tzinfo=timezone.utc),
                "size": 13,
                "e_tag": "dataset2-hash",
                "version": None,
            },
            {
                "path": "config/settings.json",
                "last_modified": datetime(2023, 1, 1, 10, 2, 0, tzinfo=timezone.utc),
                "size": 40,
                "e_tag": "settings-hash",
                "version": None,
            },
        ]
        upload_metadata = [
            ObjectMeta(**meta_dict) for meta_dict in upload_metadata_dicts
        ]

        # 3. Simulate list and catalog all files
        all_files_dicts = upload_metadata_dicts  # Same data for this test
        all_files = [ObjectMeta(**item_dict) for item_dict in all_files_dicts]

        # 4. Verify we have all expected files
        assert len(all_files) == 3
        input_files = [f for f in all_files if f.path.startswith("input/")]
        config_files = [f for f in all_files if f.path.startswith("config/")]

        assert len(input_files) == 2
        assert len(config_files) == 1

        # 5. Process files (simulate processing with get options)
        for input_file in input_files:
            # Create get options for conditional processing
            get_opts = GetOptions(
                if_match=input_file.e_tag,  # Ensure file hasn't changed
                range=(0, min(100, input_file.size - 1)),
            )
            assert get_opts.if_match == input_file.e_tag

        # 6. Simulate output files
        output_metadata_dicts = [
            {
                "path": "output/processed_dataset1.json",
                "last_modified": datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
                "size": 30,
                "e_tag": "processed1-hash",
                "version": None,
            },
            {
                "path": "output/processed_dataset2.json",
                "last_modified": datetime(2023, 1, 1, 11, 1, 0, tzinfo=timezone.utc),
                "size": 30,
                "e_tag": "processed2-hash",
                "version": None,
            },
            {
                "path": "output/summary.txt",
                "last_modified": datetime(2023, 1, 1, 11, 2, 0, tzinfo=timezone.utc),
                "size": 32,
                "e_tag": "summary-hash",
                "version": None,
            },
        ]
        output_metadata = [
            ObjectMeta(**meta_dict) for meta_dict in output_metadata_dicts
        ]

        # 7. Verify output
        assert len(output_metadata) == 3
        for obj_meta in output_metadata:
            assert obj_meta.path.startswith("output/")
            assert obj_meta.size > 0
            assert isinstance(obj_meta.last_modified, datetime)

        # 8. Final verification - simulate listing all objects and categorize
        all_metadata_dicts = upload_metadata_dicts + output_metadata_dicts
        final_listing = [ObjectMeta(**meta_dict) for meta_dict in all_metadata_dicts]

        # Should have 6 total objects: 2 input + 1 config + 3 output
        assert len(final_listing) == 6

        # Categorize by prefix
        by_category = {}
        for obj in final_listing:
            prefix = obj.path.split("/")[0]
            by_category.setdefault(prefix, []).append(obj)

        assert len(by_category["input"]) == 2
        assert len(by_category["config"]) == 1
        assert len(by_category["output"]) == 3

    def test_config_serialization_roundtrip_compatibility(self):
        """Test config can be serialized and used with obstore after deserialization."""
        # Create complex config
        original_config = Config(
            client_options=ClientConfig(
                allow_http=False,
                timeout="60s",  # Test string timeout
                connect_timeout=timedelta(seconds=10),
                default_headers={
                    "Authorization": b"Bearer token123",  # Test bytes header
                    "Content-Type": "application/json",  # Test string header
                },
                http2_only=True,
                pool_max_idle_per_host="20",
            ),
            retry_options=RetryConfig(
                max_retries=10,
                retry_timeout=timedelta(minutes=5),
                backoff=BackoffConfig(
                    base=1.5,
                    init_backoff=timedelta(milliseconds=200),
                    max_backoff=timedelta(seconds=60),
                ),
            ),
        )

        # Serialize to JSON
        json_str = original_config.model_dump_json()
        assert isinstance(json_str, str)
        assert (
            "60s" in json_str or "60.0" in json_str
        )  # String timeout should be preserved or converted

        # Deserialize from JSON
        restored_config = Config.model_validate_json(json_str)

        # Verify structure is preserved
        assert (
            restored_config.client_options.allow_http
            == original_config.client_options.allow_http
        )
        assert (
            restored_config.client_options.http2_only
            == original_config.client_options.http2_only
        )
        assert (
            restored_config.retry_options.max_retries
            == original_config.retry_options.max_retries
        )

        # Verify nested objects work
        assert isinstance(restored_config.retry_options.backoff, BackoffConfig)
        assert (
            restored_config.retry_options.backoff.base
            == original_config.retry_options.backoff.base
        )

        # Convert to obstore-compatible format
        client_opts = restored_config.client_options.model_dump(exclude_none=True)
        retry_opts = restored_config.retry_options.model_dump(exclude_none=True)

        # Verify the restored config produces valid obstore parameters
        assert isinstance(client_opts, dict)
        assert isinstance(retry_opts, dict)
        assert "backoff" in retry_opts
        assert isinstance(retry_opts["backoff"], dict)

    def test_error_handling_with_pydantic_models(self):
        """Test that pydantic models handle invalid data gracefully."""
        # Test ObjectMeta with invalid data should raise validation error
        with pytest.raises(ValueError):
            ObjectMeta(path="test", last_modified="invalid-date", size="invalid-size")

        # Test GetOptions with invalid range
        with pytest.raises(ValueError):
            GetOptions(range="invalid-range-type")

        # Test config validation
        with pytest.raises(ValueError):
            ClientConfig(allow_http="not-a-bool")  # Invalid types

    def test_model_compatibility_with_different_obstore_versions(self):
        """Test that models are flexible enough to work across obstore versions."""
        # Test ObjectMeta with minimal required fields (version compatibility)
        minimal_meta_dict = {
            "path": "test/file.txt",
            "last_modified": datetime.now(timezone.utc),
            "size": 1024,
        }

        obj_meta = ObjectMeta(**minimal_meta_dict)
        assert obj_meta.path == "test/file.txt"
        assert obj_meta.size == 1024
        assert obj_meta.e_tag is None  # Optional field defaults to None
        assert obj_meta.version is None  # Optional field defaults to None

        # Test ObjectMeta with extra fields that might be added in future versions
        # Pydantic should handle this gracefully with extra="forbid" raising error
        extended_meta_dict = {
            **minimal_meta_dict,
            "e_tag": "abc123",
            "version": "v1.0",
        }

        extended_meta = ObjectMeta(**extended_meta_dict)
        assert extended_meta.e_tag == "abc123"
        assert extended_meta.version == "v1.0"

        # Test that unknown fields are rejected (maintains data integrity)
        with pytest.raises(ValueError):
            ObjectMeta(**{**minimal_meta_dict, "unknown_field": "value"})

    def test_obstore_store_constructor_compatibility(self):
        """Test that config models can be used like obstore expects for store construction."""
        # Create configuration that matches obstore S3Store constructor expectations
        s3_compatible_config = Config(
            client_options=ClientConfig(
                allow_http=True,
                timeout=timedelta(seconds=30),
                default_headers={"User-Agent": "my-app/1.0"},
                connect_timeout=timedelta(seconds=5),
            ),
            retry_options=RetryConfig(
                max_retries=3,
                retry_timeout=timedelta(minutes=1),
                backoff=BackoffConfig(
                    base=2,
                    init_backoff=timedelta(milliseconds=100),
                    max_backoff=timedelta(seconds=15),
                ),
            ),
        )

        # Convert to the format obstore would expect
        client_config_dict = s3_compatible_config.client_options.model_dump(
            exclude_none=True
        )
        retry_config_dict = s3_compatible_config.retry_options.model_dump(
            exclude_none=True
        )

        # These dictionaries should be directly usable as obstore constructor parameters
        # Verify they have the expected structure
        assert "allow_http" in client_config_dict
        assert "timeout" in client_config_dict
        assert "default_headers" in client_config_dict
        assert "connect_timeout" in client_config_dict

        assert "max_retries" in retry_config_dict
        assert "retry_timeout" in retry_config_dict
        assert "backoff" in retry_config_dict

        # Verify backoff is properly nested
        backoff_dict = retry_config_dict["backoff"]
        assert "base" in backoff_dict
        assert "init_backoff" in backoff_dict
        assert "max_backoff" in backoff_dict

        # Verify types match what obstore expects
        assert isinstance(client_config_dict["allow_http"], bool)
        assert isinstance(client_config_dict["timeout"], timedelta)
        assert isinstance(retry_config_dict["max_retries"], int)
        assert isinstance(backoff_dict["base"], int)  # Should be int (2)
