import pytest
from app.models.job import Job
from datetime import datetime

def test_job_model_creation():
    """Test creating a valid Job model"""
    job = Job(
        id="test-123",
        title="Software Engineer",
        company="Test Corp",
        location="Remote",
        description="<p>Test description</p>",
        url="https://example.com/job",
        source="linkedin"
    )
    
    assert job.id == "test-123"
    assert job.title == "Software Engineer"
    assert job.company == "Test Corp"
    assert job.source == "linkedin"
    assert job.raw_data == {}
    assert job.posted_date is None

def test_job_model_with_optional_fields():
    """Test Job model with optional fields populated"""
    now = datetime.now()
    job = Job(
        id="test-123",
        title="Software Engineer",
        company="Test Corp",
        location="Remote",
        description="Test",
        url="https://example.com/job",
        source="jobright",
        posted_date=now,
        raw_data={"extra": "value"}
    )
    
    assert job.posted_date == now
    assert job.raw_data["extra"] == "value"

def test_job_model_validation_error():
    """Test that missing required fields raises validation error"""
    with pytest.raises(ValueError):
        Job(
            id="test-123",
            # Missing title, company, etc.
        )
