from datetime import datetime, timezone

import pytest

from pydantic_obstore import ObjectMeta


class TestObjectMeta:
    """Test ObjectMeta model matches obstore metadata structure."""

    @pytest.fixture
    def sample_obstore_metadata(self):
        """Sample metadata dictionary that obstore would return."""
        return {
            "path": "test/sample.txt",
            "last_modified": datetime(2023, 1, 15, 12, 30, 45, tzinfo=timezone.utc),
            "size": 1024,
            "e_tag": "abc123def456",
            "version": None,
        }

    @pytest.fixture
    def sample_obstore_list_items(self):
        """Sample list of metadata items that obstore list() would return."""
        return [
            {
                "path": "data/file1.txt",
                "last_modified": datetime(2023, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
                "size": 512,
                "e_tag": "file1hash",
                "version": None,
            },
            {
                "path": "data/file2.json",
                "last_modified": datetime(2023, 1, 15, 11, 0, 0, tzinfo=timezone.utc),
                "size": 256,
                "e_tag": "file2hash",
                "version": "v1.0",
            },
            {
                "path": "logs/app.log",
                "last_modified": datetime(2023, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
                "size": 2048,
                "e_tag": "loghash",
                "version": None,
            },
        ]

    def test_object_meta_from_head_result(self, sample_obstore_metadata):
        """Test that ObjectMeta can be created from obstore head() result."""
        # Create ObjectMeta from obstore metadata dict
        obj_meta = ObjectMeta(**sample_obstore_metadata)

        # Verify all fields are populated correctly
        assert obj_meta.path == "test/sample.txt"
        assert isinstance(obj_meta.last_modified, datetime)
        assert obj_meta.last_modified.tzinfo == timezone.utc
        assert obj_meta.size == 1024
        assert obj_meta.e_tag == "abc123def456"
        assert obj_meta.version is None

    def test_object_meta_from_list_result(self, sample_obstore_list_items):
        """Test that ObjectMeta can be created from obstore list() results."""
        # Convert each list result to ObjectMeta
        object_metas = [ObjectMeta(**item) for item in sample_obstore_list_items]

        # Verify we have the right number of objects
        assert len(object_metas) == 3

        # Verify each ObjectMeta is valid
        for obj_meta in object_metas:
            assert obj_meta.path in [
                "data/file1.txt",
                "data/file2.json",
                "logs/app.log",
            ]
            assert isinstance(obj_meta.last_modified, datetime)
            assert obj_meta.last_modified.tzinfo == timezone.utc
            assert obj_meta.size > 0
            assert obj_meta.e_tag is not None

        # Verify specific items
        file1_meta = next(obj for obj in object_metas if obj.path == "data/file1.txt")
        assert file1_meta.size == 512
        assert file1_meta.version is None

        file2_meta = next(obj for obj in object_metas if obj.path == "data/file2.json")
        assert file2_meta.version == "v1.0"

    def test_object_meta_required_fields(self):
        """Test that ObjectMeta requires the correct fields."""
        # Test with all required fields
        valid_meta = ObjectMeta(
            path="test/file.txt",
            last_modified=datetime.now(timezone.utc),
            size=100,
        )
        assert valid_meta.path == "test/file.txt"
        assert valid_meta.size == 100

        # Test missing required field raises validation error
        with pytest.raises(ValueError):
            ObjectMeta(
                last_modified=datetime.now(timezone.utc),
                size=100,
                # Missing 'path'
            )

    def test_object_meta_optional_fields(self):
        """Test that ObjectMeta handles optional fields correctly."""
        # Test with only required fields (optional fields should be None)
        minimal_meta = ObjectMeta(
            path="test/file.txt",
            last_modified=datetime.now(timezone.utc),
            size=100,
        )
        assert minimal_meta.e_tag is None
        assert minimal_meta.version is None

        # Test with all fields
        full_meta = ObjectMeta(
            path="test/file.txt",
            last_modified=datetime.now(timezone.utc),
            size=100,
            e_tag="abc123",
            version="v1.0",
        )
        assert full_meta.e_tag == "abc123"
        assert full_meta.version == "v1.0"

    def test_object_meta_field_types(self):
        """Test that ObjectMeta enforces correct field types."""
        base_time = datetime.now(timezone.utc)

        # Test correct types
        valid_meta = ObjectMeta(
            path="test/file.txt",
            last_modified=base_time,
            size=100,
            e_tag="abc123",
            version="v1.0",
        )
        assert isinstance(valid_meta.path, str)
        assert isinstance(valid_meta.last_modified, datetime)
        assert isinstance(valid_meta.size, int)
        assert isinstance(valid_meta.e_tag, str)
        assert isinstance(valid_meta.version, str)

        # Test invalid types raise validation errors
        with pytest.raises(ValueError):
            ObjectMeta(
                path=123,  # Should be string
                last_modified=base_time,
                size=100,
            )

        with pytest.raises(ValueError):
            ObjectMeta(
                path="test/file.txt",
                last_modified="not-a-datetime",  # Should be datetime
                size=100,
            )

        with pytest.raises(ValueError):
            ObjectMeta(
                path="test/file.txt",
                last_modified=base_time,
                size="not-an-int",  # Should be int
            )

    def test_object_meta_matches_obstore_structure(self, sample_obstore_metadata):
        """Test that ObjectMeta fields exactly match obstore metadata dict keys."""
        # Create ObjectMeta
        pydantic_meta = ObjectMeta(**sample_obstore_metadata)

        # Verify all obstore dict keys are handled by ObjectMeta
        for key, value in sample_obstore_metadata.items():
            assert hasattr(pydantic_meta, key), f"ObjectMeta missing field: {key}"
            assert getattr(pydantic_meta, key) == value, f"Field {key} value mismatch"

        # Verify ObjectMeta doesn't have extra fields (beyond what obstore provides)
        pydantic_dict = pydantic_meta.model_dump(exclude_none=True)
        for key in pydantic_dict:
            assert key in sample_obstore_metadata, f"ObjectMeta has extra field: {key}"

    def test_object_meta_serialization(self):
        """Test that ObjectMeta can be serialized and deserialized."""
        original = ObjectMeta(
            path="test/serialize.txt",
            last_modified=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            size=1024,
            e_tag="def456",
            version="v2.0",
        )

        # Test model_dump
        as_dict = original.model_dump()
        expected_keys = {"path", "last_modified", "size", "e_tag", "version"}
        assert set(as_dict.keys()) == expected_keys

        # Test reconstruction from dict
        reconstructed = ObjectMeta(**as_dict)
        assert reconstructed.path == original.path
        assert reconstructed.last_modified == original.last_modified
        assert reconstructed.size == original.size
        assert reconstructed.e_tag == original.e_tag
        assert reconstructed.version == original.version

        # Test JSON serialization
        json_str = original.model_dump_json()
        assert isinstance(json_str, str)
        assert "test/serialize.txt" in json_str

        # Test JSON deserialization
        from_json = ObjectMeta.model_validate_json(json_str)
        assert from_json.path == original.path
        assert from_json.size == original.size

    def test_object_meta_handles_real_obstore_data_patterns(self):
        """Test ObjectMeta with realistic data patterns from obstore."""
        # Test with S3-like data
        s3_like_data = {
            "path": "bucket/folder/subfolder/document.pdf",
            "last_modified": datetime(
                2023, 12, 1, 9, 15, 30, 123456, tzinfo=timezone.utc
            ),
            "size": 2097152,  # 2MB
            "e_tag": '"d41d8cd98f00b204e9800998ecf8427e"',  # S3 ETags have quotes
            "version": "3/L4kqtJlcpXroDVBH40Nr8X8gdRQBpUMLUo",  # S3 version ID
        }
        s3_meta = ObjectMeta(**s3_like_data)
        assert s3_meta.path == "bucket/folder/subfolder/document.pdf"
        assert s3_meta.e_tag == '"d41d8cd98f00b204e9800998ecf8427e"'

        # Test with GCS-like data
        gcs_like_data = {
            "path": "my-bucket/images/photo.jpg",
            "last_modified": datetime(2023, 11, 15, 14, 22, 0, tzinfo=timezone.utc),
            "size": 1048576,  # 1MB
            "e_tag": "CKih3PLblPsCEAE=",  # GCS generation/metageneration
            "version": "1699878320000000",  # GCS generation
        }
        gcs_meta = ObjectMeta(**gcs_like_data)
        assert gcs_meta.size == 1048576

        # Test with minimal data (like from MemoryStore)
        memory_like_data = {
            "path": "temp/test.txt",
            "last_modified": datetime.now(timezone.utc),
            "size": 42,
            "e_tag": "0",  # MemoryStore uses simple incrementing ETags
            "version": None,
        }
        memory_meta = ObjectMeta(**memory_like_data)
        assert memory_meta.version is None
        assert memory_meta.e_tag == "0"
