"""
Test suite for FHIR Lab Test Catalog API
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime
import json

from app.api.endpoints import app
from app.core.database import db_manager
from app.models.fhir_models import (
    LabTestDefinition, ObservationDefinition, SpecimenDefinition,
    PublicationStatus, Coding, CodeableConcept
)
from app.services.fhir_service import fhir_service


@pytest_asyncio.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Setup test database"""
    await db_manager.connect()
    await db_manager.create_tables()
    yield
    await db_manager.drop_tables()
    await db_manager.disconnect()


@pytest_asyncio.fixture
async def sample_lab_test():
    """Create a sample lab test for testing"""
    
    observation_def = ObservationDefinition(
        id="test-obs-def",
        status=PublicationStatus.ACTIVE,
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("33747-0", "Blood glucose level")
        ], "Blood Glucose"),
        category=[fhir_service.create_codeable_concept([
            fhir_service.create_coding("http://terminology.hl7.org/CodeSystem/observation-category", "laboratory", "Laboratory")
        ])],
        permitted_data_type=["Quantity"],
        multiple_results_allowed=False,
        preferred_report_name="Glucose"
    )
    
    specimen_def = SpecimenDefinition(
        id="test-spec-def",
        status=PublicationStatus.ACTIVE,
        type_collected=fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("119364003", "Serum specimen")
        ], "Serum"),
        patient_preparation=["Fasting for 8-12 hours"],
        time_aspect="Fasting"
    )
    
    test_definition = LabTestDefinition(
        id="test-glucose-001",
        name="Blood Glucose Test",
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("33747-0", "Blood glucose level")
        ], "Blood Glucose"),
        status=PublicationStatus.ACTIVE,
        category=[
            fhir_service.create_codeable_concept([
                fhir_service.create_coding("http://example.org/lab-categories", "chemistry", "Clinical Chemistry")
            ])
        ],
        description="Blood glucose test measures the amount of sugar in the blood",
        clinical_purpose="Diagnosis and monitoring of diabetes mellitus",
        observation_definition=observation_def,
        specimen_definition=specimen_def,
        reference_ranges=[
            {
                "parameter": "Glucose",
                "range": {"low": 70, "high": 100, "unit": "mg/dL"},
                "condition": "Fasting"
            }
        ],
        critical_values={
            "Glucose": {"low": 50, "high": 400, "unit": "mg/dL"}
        }
    )
    
    return test_definition


class TestAPIEndpoints:
    """Test API endpoints"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns capability statement"""
        response = await client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "CapabilityStatement"
        assert data["name"] == "FHIR Lab Test Catalog API"
        assert data["status"] == "active"
        assert "rest" in data
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_search_lab_tests_empty(self, client: AsyncClient, setup_database):
        """Test search with empty database"""
        response = await client.get("/LabTestDefinition")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert data["count"] == 0
        assert data["results"] == []
    
    @pytest.mark.asyncio
    async def test_create_lab_test(self, client: AsyncClient, setup_database, sample_lab_test):
        """Test creating a lab test definition"""
        test_data = sample_lab_test.dict()
        
        response = await client.post("/LabTestDefinition", json=test_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["id"] == sample_lab_test.id
        assert data["name"] == sample_lab_test.name
        assert data["status"] == sample_lab_test.status.value
    
    @pytest.mark.asyncio
    async def test_get_lab_test_by_id(self, client: AsyncClient, setup_database, sample_lab_test):
        """Test getting a lab test by ID"""
        # First create the test
        test_data = sample_lab_test.dict()
        create_response = await client.post("/LabTestDefinition", json=test_data)
        assert create_response.status_code == 201
        
        # Then retrieve it
        response = await client.get(f"/LabTestDefinition/{sample_lab_test.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_lab_test.id
        assert data["name"] == sample_lab_test.name
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_lab_test(self, client: AsyncClient, setup_database):
        """Test getting a non-existent lab test"""
        response = await client.get("/LabTestDefinition/nonexistent-id")
        assert response.status_code == 404
        
        # Should return FHIR OperationOutcome
        data = response.json()
        assert data["resourceType"] == "OperationOutcome"
    
    @pytest.mark.asyncio
    async def test_update_lab_test(self, client: AsyncClient, setup_database, sample_lab_test):
        """Test updating a lab test definition"""
        # First create the test
        test_data = sample_lab_test.dict()
        create_response = await client.post("/LabTestDefinition", json=test_data)
        assert create_response.status_code == 201
        
        # Update the test
        updated_data = test_data.copy()
        updated_data["description"] = "Updated description for blood glucose test"
        
        response = await client.put(f"/LabTestDefinition/{sample_lab_test.id}", json=updated_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["description"] == "Updated description for blood glucose test"
    
    @pytest.mark.asyncio
    async def test_delete_lab_test(self, client: AsyncClient, setup_database, sample_lab_test):
        """Test deleting a lab test definition"""
        # First create the test
        test_data = sample_lab_test.dict()
        create_response = await client.post("/LabTestDefinition", json=test_data)
        assert create_response.status_code == 201
        
        # Delete the test
        response = await client.delete(f"/LabTestDefinition/{sample_lab_test.id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = await client.get(f"/LabTestDefinition/{sample_lab_test.id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, client: AsyncClient, setup_database, sample_lab_test):
        """Test search with various filters"""
        # Create a test
        test_data = sample_lab_test.dict()
        create_response = await client.post("/LabTestDefinition", json=test_data)
        assert create_response.status_code == 201
        
        # Search by query
        response = await client.get("/LabTestDefinition?query=glucose")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        # Search by category
        response = await client.get("/LabTestDefinition?category=chemistry")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        # Search by status
        response = await client.get("/LabTestDefinition?status=active")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_observation_definition(self, client: AsyncClient, setup_database, sample_lab_test):
        """Test getting ObservationDefinition for a test"""
        # First create the test
        test_data = sample_lab_test.dict()
        create_response = await client.post("/LabTestDefinition", json=test_data)
        assert create_response.status_code == 201
        
        # Get the ObservationDefinition
        response = await client.get(f"/ObservationDefinition/{sample_lab_test.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "ObservationDefinition"
        assert data["id"] == "test-obs-def"
    
    @pytest.mark.asyncio
    async def test_get_specimen_definition(self, client: AsyncClient, setup_database, sample_lab_test):
        """Test getting SpecimenDefinition for a test"""
        # First create the test
        test_data = sample_lab_test.dict()
        create_response = await client.post("/LabTestDefinition", json=test_data)
        assert create_response.status_code == 201
        
        # Get the SpecimenDefinition
        response = await client.get(f"/SpecimenDefinition/{sample_lab_test.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "SpecimenDefinition"
        assert data["id"] == "test-spec-def"
    
    @pytest.mark.asyncio
    async def test_get_bundle(self, client: AsyncClient, setup_database, sample_lab_test):
        """Test getting lab tests as a Bundle"""
        # First create the test
        test_data = sample_lab_test.dict()
        create_response = await client.post("/LabTestDefinition", json=test_data)
        assert create_response.status_code == 201
        
        # Get the Bundle
        response = await client.get("/Bundle/lab-tests")
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert "entry" in data
        assert len(data["entry"]) >= 1
    
    @pytest.mark.asyncio
    async def test_validate_lab_test(self, client: AsyncClient, sample_lab_test):
        """Test lab test validation"""
        test_data = sample_lab_test.dict()
        
        response = await client.post("/LabTestDefinition/$validate", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "OperationOutcome"
        assert "issue" in data
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, client: AsyncClient, setup_database):
        """Test getting catalog statistics"""
        response = await client.get("/metadata/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "Parameters"
        assert "parameter" in data
    
    @pytest.mark.asyncio
    async def test_get_categories(self, client: AsyncClient):
        """Test getting available categories"""
        response = await client.get("/metadata/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "ValueSet"
        assert data["name"] == "LabTestCategories"
        assert "compose" in data


class TestValidation:
    """Test FHIR validation"""
    
    @pytest.mark.asyncio
    async def test_create_invalid_test(self, client: AsyncClient, setup_database):
        """Test creating an invalid lab test"""
        invalid_test = {
            "id": "invalid-test",
            "name": "",  # Empty name should be invalid
            "status": "active",
            "description": ""  # Empty description should be invalid
        }
        
        response = await client.post("/LabTestDefinition", json=invalid_test)
        assert response.status_code == 400
        
        data = response.json()
        assert data["resourceType"] == "OperationOutcome"
    
    @pytest.mark.asyncio
    async def test_validation_endpoint(self, client: AsyncClient):
        """Test the validation endpoint"""
        invalid_test = {
            "id": "test-invalid",
            "name": "Test",
            "status": "invalid-status",  # Invalid status
            "description": "Test description"
        }
        
        response = await client.post("/LabTestDefinition/$validate", json=invalid_test)
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "OperationOutcome"
        # Should have validation issues
        assert len(data["issue"]) > 0


class TestPagination:
    """Test pagination and search limits"""
    
    @pytest.mark.asyncio
    async def test_pagination_parameters(self, client: AsyncClient, setup_database):
        """Test pagination parameters"""
        # Test with count and offset
        response = await client.get("/LabTestDefinition?_count=10&_offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] <= 10
        assert data["offset"] == 0
    
    @pytest.mark.asyncio
    async def test_sort_parameters(self, client: AsyncClient, setup_database):
        """Test sorting parameters"""
        response = await client.get("/LabTestDefinition?_sort=name&_order=desc")
        assert response.status_code == 200
        
        # Should return results without error
        data = response.json()
        assert "results" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])