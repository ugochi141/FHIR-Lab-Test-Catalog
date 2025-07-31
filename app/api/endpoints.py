"""
FastAPI endpoints for FHIR Lab Test Catalog
Implements FHIR R4 compliant REST API
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Path, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import uvicorn
from datetime import datetime
import json

from app.models.fhir_models import (
    LabTestDefinition, ObservationDefinition, SpecimenDefinition,
    Bundle, SearchParameters, SearchResults, OperationOutcome,
    PublicationStatus, Coding, CodeableConcept
)
from app.services.fhir_service import fhir_service
from app.core.database import db_manager


# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="FHIR Lab Test Catalog API",
    description="""
    A FHIR R4 compliant REST API for laboratory test catalog management.
    
    ## Features
    
    * **FHIR R4 Compliant**: Full compliance with FHIR R4 specification
    * **Lab Test Management**: Create, read, update, delete lab test definitions
    * **Advanced Search**: Full-text search with filtering and faceting
    * **FHIR Resources**: ObservationDefinition, SpecimenDefinition support
    * **Validation**: Comprehensive FHIR validation
    * **Bundle Support**: FHIR Bundle responses for collections
    * **Standards Support**: LOINC, SNOMED CT, and other standard terminologies
    
    ## FHIR Resources
    
    This API manages the following FHIR resources:
    - **LabTestDefinition**: Enhanced lab test definitions
    - **ObservationDefinition**: FHIR-compliant observation definitions
    - **SpecimenDefinition**: FHIR-compliant specimen definitions
    - **Bundle**: Collections of resources
    - **OperationOutcome**: Error and validation results
    
    ## Standards Compliance
    
    - FHIR R4 specification
    - LOINC codes for lab tests
    - SNOMED CT for clinical concepts
    - HL7 FHIR terminology services
    """,
    version="1.0.0",
    contact={
        "name": "FHIR Lab Test Catalog",
        "url": "https://github.com/ugochi141/FHIR-Lab-Test-Catalog",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Lab Tests",
            "description": "Operations for lab test definitions",
        },
        {
            "name": "FHIR Resources",
            "description": "FHIR resource operations",
        },
        {
            "name": "Search",
            "description": "Search and discovery operations",
        },
        {
            "name": "Metadata",
            "description": "Catalog metadata and statistics",
        },
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and create tables"""
    await db_manager.connect()
    await db_manager.create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection"""
    await db_manager.disconnect()

# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler with FHIR OperationOutcome"""
    outcome = fhir_service.create_operation_outcome([{
        "severity": "error",
        "code": "not-found",
        "details": "The requested resource could not be found"
    }])
    return JSONResponse(
        status_code=404,
        content=outcome.dict()
    )

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: HTTPException):
    """Custom 400 handler with FHIR OperationOutcome"""
    outcome = fhir_service.create_operation_outcome([{
        "severity": "error",
        "code": "invalid",
        "details": str(exc.detail) if hasattr(exc, 'detail') else "Bad request"
    }])
    return JSONResponse(
        status_code=400,
        content=outcome.dict()
    )

# Root endpoint
@app.get(
    "/",
    summary="API Information",
    description="Get basic information about the FHIR Lab Test Catalog API"
)
async def root():
    """API root endpoint with service information"""
    return {
        "resourceType": "CapabilityStatement",
        "id": "fhir-lab-test-catalog",
        "name": "FHIR Lab Test Catalog API",
        "title": "FHIR Lab Test Catalog API",
        "status": "active",
        "date": datetime.utcnow().isoformat(),
        "publisher": "FHIR Lab Test Catalog",
        "description": "FHIR R4 compliant REST API for laboratory test catalog management",
        "fhirVersion": "4.0.1",
        "format": ["application/fhir+json", "application/json"],
        "rest": [{
            "mode": "server",
            "resource": [
                {
                    "type": "ObservationDefinition",
                    "interaction": [
                        {"code": "read"},
                        {"code": "create"},
                        {"code": "update"},
                        {"code": "delete"},
                        {"code": "search-type"}
                    ]
                },
                {
                    "type": "SpecimenDefinition", 
                    "interaction": [
                        {"code": "read"},
                        {"code": "create"},
                        {"code": "update"},
                        {"code": "delete"},
                        {"code": "search-type"}
                    ]
                }
            ]
        }]
    }

# Lab Test Definition endpoints
@app.get(
    "/LabTestDefinition",
    response_model=SearchResults,
    tags=["Lab Tests", "Search"],
    summary="Search Lab Test Definitions",
    description="Search for lab test definitions using various filters and parameters"
)
async def search_lab_tests(
    query: Optional[str] = Query(None, description="Text search across test names and descriptions"),
    category: Optional[List[str]] = Query(None, description="Filter by test categories"),
    status: Optional[List[PublicationStatus]] = Query(None, description="Filter by publication status"),
    specimen_type: Optional[List[str]] = Query(None, description="Filter by specimen types"),
    code_system: Optional[str] = Query(None, description="Filter by coding system"),
    code: Optional[str] = Query(None, description="Filter by specific test codes"),
    _count: int = Query(50, ge=1, le=1000, alias="_count", description="Maximum number of results"),
    _offset: int = Query(0, ge=0, alias="_offset", description="Number of results to skip"),
    _sort: Optional[str] = Query("name", alias="_sort", description="Field to sort by"),
    _order: Optional[str] = Query("asc", alias="_order", description="Sort order: asc or desc")
):
    """Search lab test definitions with comprehensive filtering"""
    
    search_params = SearchParameters(
        query=query,
        category=category,
        status=[s.value if isinstance(s, PublicationStatus) else s for s in status] if status else None,
        specimen_type=specimen_type,
        code_system=code_system,
        code=code,
        limit=_count,
        offset=_offset,
        sort_by=_sort,
        sort_order=_order
    )
    
    try:
        results = await fhir_service.search_lab_tests(search_params)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get(
    "/LabTestDefinition/{test_id}",
    response_model=LabTestDefinition,
    tags=["Lab Tests"],
    summary="Get Lab Test Definition",
    description="Get a specific lab test definition by ID"
)
async def get_lab_test(
    test_id: str = Path(..., description="Unique identifier for the lab test")
):
    """Get a lab test definition by ID"""
    
    test = await fhir_service.get_lab_test_by_id(test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail=f"Lab test with ID {test_id} not found")
    
    return test

@app.post(
    "/LabTestDefinition",
    response_model=LabTestDefinition,
    status_code=status.HTTP_201_CREATED,
    tags=["Lab Tests"],
    summary="Create Lab Test Definition",
    description="Create a new lab test definition"
)
async def create_lab_test(test_definition: LabTestDefinition):
    """Create a new lab test definition"""
    
    # Validate the test definition
    issues = await fhir_service.validate_lab_test(test_definition)
    error_issues = [issue for issue in issues if issue["severity"] == "error"]
    
    if error_issues:
        outcome = fhir_service.create_operation_outcome(error_issues)
        raise HTTPException(status_code=400, detail=outcome.dict())
    
    try:
        created_test = await fhir_service.create_lab_test(test_definition)
        return created_test
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create lab test: {str(e)}")

@app.put(
    "/LabTestDefinition/{test_id}",
    response_model=LabTestDefinition,
    tags=["Lab Tests"],
    summary="Update Lab Test Definition",
    description="Update an existing lab test definition"
)
async def update_lab_test(
    test_id: str = Path(..., description="Unique identifier for the lab test"),
    test_definition: LabTestDefinition = None
):
    """Update a lab test definition"""
    
    # Validate the test definition
    issues = await fhir_service.validate_lab_test(test_definition)
    error_issues = [issue for issue in issues if issue["severity"] == "error"]
    
    if error_issues:
        outcome = fhir_service.create_operation_outcome(error_issues)
        raise HTTPException(status_code=400, detail=outcome.dict())
    
    try:
        updated_test = await fhir_service.update_lab_test(test_id, test_definition)
        
        if not updated_test:
            raise HTTPException(status_code=404, detail=f"Lab test with ID {test_id} not found")
        
        return updated_test
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update lab test: {str(e)}")

@app.delete(
    "/LabTestDefinition/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Lab Tests"],
    summary="Delete Lab Test Definition",
    description="Delete a lab test definition"
)
async def delete_lab_test(
    test_id: str = Path(..., description="Unique identifier for the lab test")
):
    """Delete a lab test definition"""
    
    success = await fhir_service.delete_lab_test(test_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Lab test with ID {test_id} not found")

# FHIR Resource endpoints
@app.get(
    "/ObservationDefinition/{test_id}",
    response_model=ObservationDefinition,
    tags=["FHIR Resources"],
    summary="Get Observation Definition",
    description="Get the FHIR ObservationDefinition for a specific lab test"
)
async def get_observation_definition(
    test_id: str = Path(..., description="Unique identifier for the lab test")
):
    """Get ObservationDefinition for a lab test"""
    
    obs_def = await fhir_service.get_observation_definition(test_id)
    
    if not obs_def:
        raise HTTPException(status_code=404, detail=f"ObservationDefinition for test {test_id} not found")
    
    return obs_def

@app.get(
    "/SpecimenDefinition/{test_id}",
    response_model=SpecimenDefinition,
    tags=["FHIR Resources"],
    summary="Get Specimen Definition",
    description="Get the FHIR SpecimenDefinition for a specific lab test"
)
async def get_specimen_definition(
    test_id: str = Path(..., description="Unique identifier for the lab test")
):
    """Get SpecimenDefinition for a lab test"""
    
    spec_def = await fhir_service.get_specimen_definition(test_id)
    
    if not spec_def:
        raise HTTPException(status_code=404, detail=f"SpecimenDefinition for test {test_id} not found")
    
    return spec_def

# Bundle endpoints
@app.get(
    "/Bundle/lab-tests",
    response_model=Bundle,
    tags=["FHIR Resources"],
    summary="Get Lab Tests Bundle",
    description="Get lab test definitions as a FHIR Bundle"
)
async def get_lab_tests_bundle(
    query: Optional[str] = Query(None, description="Text search query"),
    category: Optional[List[str]] = Query(None, description="Filter by categories"),
    status: Optional[List[PublicationStatus]] = Query(None, description="Filter by status"),
    _count: int = Query(50, ge=1, le=1000, alias="_count", description="Maximum number of results"),
    _offset: int = Query(0, ge=0, alias="_offset", description="Number of results to skip")
):
    """Get lab tests as a FHIR Bundle"""
    
    search_params = SearchParameters(
        query=query,
        category=category,
        status=[s.value if isinstance(s, PublicationStatus) else s for s in status] if status else None,
        limit=_count,
        offset=_offset
    )
    
    try:
        bundle = await fhir_service.get_lab_tests_as_bundle(search_params)
        return bundle
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bundle: {str(e)}")

# Validation endpoint
@app.post(
    "/LabTestDefinition/$validate",
    response_model=OperationOutcome,
    tags=["Lab Tests"],
    summary="Validate Lab Test Definition",
    description="Validate a lab test definition against FHIR specifications"
)
async def validate_lab_test(test_definition: LabTestDefinition):
    """Validate a lab test definition"""
    
    issues = await fhir_service.validate_lab_test(test_definition)
    outcome = fhir_service.create_operation_outcome(issues)
    
    return outcome

# Metadata endpoints
@app.get(
    "/metadata/statistics",
    tags=["Metadata"],
    summary="Get Catalog Statistics",
    description="Get statistics about the lab test catalog"
)
async def get_catalog_statistics():
    """Get catalog statistics"""
    
    try:
        stats = await fhir_service.get_catalog_statistics()
        return {
            "resourceType": "Parameters",
            "parameter": [
                {"name": "totalTests", "valueInteger": stats.get("total_tests", 0)},
                {"name": "byStatus", "part": [
                    {"name": status_name, "valueInteger": count}
                    for status_name, count in stats.get("by_status", {}).items()
                ]},
                {"name": "byCategory", "part": [
                    {"name": category_name, "valueInteger": count}
                    for category_name, count in stats.get("by_category", {}).items()
                ]},
                {"name": "lastUpdated", "valueDateTime": datetime.utcnow().isoformat()},
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get(
    "/metadata/categories",
    tags=["Metadata"],
    summary="Get Available Categories",
    description="Get list of available test categories"
)
async def get_available_categories():
    """Get available test categories"""
    
    # This would typically come from the database
    categories = [
        {"code": "chemistry", "display": "Clinical Chemistry"},
        {"code": "hematology", "display": "Hematology"},
        {"code": "immunology", "display": "Immunology"},
        {"code": "microbiology", "display": "Microbiology"},
        {"code": "molecular", "display": "Molecular Diagnostics"},
        {"code": "pathology", "display": "Anatomic Pathology"},
        {"code": "toxicology", "display": "Toxicology"},
        {"code": "endocrinology", "display": "Endocrinology"}
    ]
    
    return {
        "resourceType": "ValueSet",
        "id": "lab-test-categories",
        "name": "LabTestCategories",
        "title": "Laboratory Test Categories",
        "status": "active",
        "compose": {
            "include": [{
                "system": "http://example.org/lab-categories",
                "concept": categories
            }]
        }
    }

# Health check endpoint
@app.get(
    "/health",
    tags=["Metadata"],
    summary="Health Check",
    description="Check API health status"
)
async def health_check():
    """Health check endpoint"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": "connected"
    }

# Custom OpenAPI schema
def custom_openapi():
    """Custom OpenAPI schema with FHIR-specific documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="FHIR Lab Test Catalog API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add FHIR-specific schema extensions
    openapi_schema["info"]["x-fhir-version"] = "4.0.1"
    openapi_schema["info"]["x-fhir-profile"] = "http://hl7.org/fhir/R4/"
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app.api.endpoints:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )