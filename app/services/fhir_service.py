"""
FHIR Service for Lab Test Catalog operations
Handles FHIR-compliant data transformation and validation
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import json
import uuid
from app.models.fhir_models import (
    LabTestDefinition, ObservationDefinition, SpecimenDefinition,
    Bundle, BundleEntry, SearchResults, SearchParameters,
    Coding, CodeableConcept, Identifier, Reference, Quantity, Range,
    PublicationStatus, Meta, OperationOutcome
)
from app.core.database import db_manager


class FHIRService:
    """Service for FHIR operations on lab test catalog"""
    
    def __init__(self):
        self.db = db_manager
        
    async def get_lab_test_by_id(self, test_id: str) -> Optional[LabTestDefinition]:
        """Get a lab test definition by ID"""
        db_result = await self.db.get_lab_test_definition(test_id)
        
        if not db_result:
            return None
            
        return self._convert_db_to_fhir(db_result)
    
    async def create_lab_test(self, test_definition: LabTestDefinition) -> LabTestDefinition:
        """Create a new lab test definition"""
        db_data = self._convert_fhir_to_db(test_definition)
        
        # Ensure unique ID
        if not db_data.get("id"):
            db_data["id"] = str(uuid.uuid4())
            
        created_data = await self.db.create_lab_test_definition(db_data)
        return self._convert_db_to_fhir(created_data)
    
    async def update_lab_test(self, test_id: str, test_definition: LabTestDefinition) -> Optional[LabTestDefinition]:
        """Update an existing lab test definition"""
        db_data = self._convert_fhir_to_db(test_definition)
        db_data["id"] = test_id  # Ensure ID consistency
        
        updated_data = await self.db.update_lab_test_definition(test_id, db_data)
        
        if not updated_data:
            return None
            
        return self._convert_db_to_fhir(updated_data)
    
    async def delete_lab_test(self, test_id: str) -> bool:
        """Delete a lab test definition"""
        return await self.db.delete_lab_test_definition(test_id)
    
    async def search_lab_tests(self, search_params: SearchParameters) -> SearchResults:
        """Search lab test definitions"""
        db_results = await self.db.search_lab_test_definitions(
            query=search_params.query,
            category=search_params.category,
            status=search_params.status,
            specimen_type=search_params.specimen_type,
            code_system=search_params.code_system,
            code=search_params.code,
            limit=search_params.limit,
            offset=search_params.offset,
            sort_by=search_params.sort_by,
            sort_order=search_params.sort_order
        )
        
        # Convert results to FHIR format
        fhir_results = []
        for db_result in db_results["results"]:
            fhir_result = self._convert_db_to_fhir(db_result)
            fhir_results.append(fhir_result)
        
        return SearchResults(
            total=db_results["total"],
            count=db_results["count"],
            offset=db_results["offset"],
            results=fhir_results,
            facets=db_results["facets"]
        )
    
    async def get_lab_tests_as_bundle(
        self, 
        search_params: Optional[SearchParameters] = None,
        bundle_type: str = "searchset"
    ) -> Bundle:
        """Get lab tests as a FHIR Bundle"""
        if not search_params:
            search_params = SearchParameters()
            
        search_results = await self.search_lab_tests(search_params)
        
        # Create bundle entries
        entries = []
        for test in search_results.results:
            entry = BundleEntry(
                fullUrl=f"LabTestDefinition/{test.id}",
                resource=test,
                search={"mode": "match"}
            )
            entries.append(entry)
        
        # Create bundle
        bundle = Bundle(
            id=str(uuid.uuid4()),
            type=bundle_type,
            timestamp=datetime.utcnow(),
            total=search_results.total,
            entry=entries
        )
        
        return bundle
    
    async def get_observation_definition(self, test_id: str) -> Optional[ObservationDefinition]:
        """Get the ObservationDefinition for a specific test"""
        test = await self.get_lab_test_by_id(test_id)
        
        if not test:
            return None
            
        return test.observation_definition
    
    async def get_specimen_definition(self, test_id: str) -> Optional[SpecimenDefinition]:
        """Get the SpecimenDefinition for a specific test"""
        test = await self.get_lab_test_by_id(test_id)
        
        if not test or not test.specimen_definition:
            return None
            
        return test.specimen_definition
    
    async def validate_lab_test(self, test_definition: LabTestDefinition) -> List[Dict[str, Any]]:
        """Validate a lab test definition against FHIR specifications"""
        issues = []
        
        # Required fields validation
        if not test_definition.name:
            issues.append({
                "severity": "error",
                "code": "required",
                "details": "Test name is required"
            })
            
        if not test_definition.code or not test_definition.code.coding:
            issues.append({
                "severity": "error",
                "code": "required",
                "details": "Test code is required"
            })
            
        if not test_definition.description:
            issues.append({
                "severity": "error",
                "code": "required",
                "details": "Test description is required"
            })
        
        # Code validation
        if test_definition.code and test_definition.code.coding:
            for coding in test_definition.code.coding:
                if not coding.system:
                    issues.append({
                        "severity": "warning",
                        "code": "incomplete",
                        "details": f"Coding system not specified for code {coding.code}"
                    })
                    
                if not coding.display:
                    issues.append({
                        "severity": "information",
                        "code": "incomplete",
                        "details": f"Display name not provided for code {coding.code}"
                    })
        
        # Category validation
        if not test_definition.category:
            issues.append({
                "severity": "warning",
                "code": "incomplete",
                "details": "Test category should be specified"
            })
        
        # ObservationDefinition validation
        obs_def = test_definition.observation_definition
        if obs_def:
            if obs_def.status not in ["draft", "active", "retired", "unknown"]:
                issues.append({
                    "severity": "error",
                    "code": "invalid",
                    "details": f"Invalid status: {obs_def.status}"
                })
                
            if not obs_def.code:
                issues.append({
                    "severity": "error",
                    "code": "required",
                    "details": "ObservationDefinition code is required"
                })
        
        return issues
    
    async def get_catalog_statistics(self) -> Dict[str, Any]:
        """Get statistics about the lab test catalog"""
        return await self.db.get_test_statistics()
    
    def _convert_fhir_to_db(self, fhir_obj: LabTestDefinition) -> Dict[str, Any]:
        """Convert FHIR LabTestDefinition to database format"""
        db_data = {
            "id": fhir_obj.id,
            "name": fhir_obj.name,
            "version": fhir_obj.version,
            "status": fhir_obj.status.value if isinstance(fhir_obj.status, PublicationStatus) else fhir_obj.status,
            "description": fhir_obj.description,
            "clinical_purpose": fhir_obj.clinical_purpose,
            "created_by": fhir_obj.created_by,
        }
        
        # Convert complex objects to JSON
        db_data["code"] = fhir_obj.code.dict() if fhir_obj.code else None
        db_data["category"] = [cat.dict() for cat in fhir_obj.category] if fhir_obj.category else None
        db_data["observation_definition"] = fhir_obj.observation_definition.dict() if fhir_obj.observation_definition else None
        db_data["specimen_definition"] = fhir_obj.specimen_definition.dict() if fhir_obj.specimen_definition else None
        db_data["reference_ranges"] = fhir_obj.reference_ranges
        db_data["critical_values"] = fhir_obj.critical_values
        db_data["precision"] = fhir_obj.precision
        db_data["accuracy"] = fhir_obj.accuracy
        db_data["turnaround_time"] = fhir_obj.turnaround_time
        db_data["cost"] = fhir_obj.cost
        db_data["ordering_information"] = fhir_obj.ordering_information
        db_data["analytical_method"] = fhir_obj.analytical_method
        db_data["created_date"] = fhir_obj.created_date
        db_data["modified_date"] = fhir_obj.modified_date
        
        return db_data
    
    def _convert_db_to_fhir(self, db_data: Dict[str, Any]) -> LabTestDefinition:
        """Convert database format to FHIR LabTestDefinition"""
        
        # Parse JSON fields
        code = CodeableConcept(**db_data["code"]) if db_data.get("code") else None
        category = [CodeableConcept(**cat) for cat in db_data["category"]] if db_data.get("category") else []
        observation_definition = ObservationDefinition(**db_data["observation_definition"]) if db_data.get("observation_definition") else None
        specimen_definition = SpecimenDefinition(**db_data["specimen_definition"]) if db_data.get("specimen_definition") else None
        
        return LabTestDefinition(
            id=db_data["id"],
            name=db_data["name"],
            version=db_data.get("version", "1.0.0"),
            status=PublicationStatus(db_data.get("status", "active")),
            code=code,
            category=category,
            description=db_data["description"],
            clinical_purpose=db_data.get("clinical_purpose"),
            observation_definition=observation_definition,
            specimen_definition=specimen_definition,
            reference_ranges=db_data.get("reference_ranges"),
            critical_values=db_data.get("critical_values"),
            analytical_method=db_data.get("analytical_method"),
            precision=db_data.get("precision"),
            accuracy=db_data.get("accuracy"),
            turnaround_time=db_data.get("turnaround_time"),
            cost=db_data.get("cost"),
            ordering_information=db_data.get("ordering_information"),
            created_date=db_data.get("created_date", datetime.utcnow()),
            modified_date=db_data.get("modified_date", datetime.utcnow()),
            created_by=db_data.get("created_by")
        )
    
    def create_operation_outcome(
        self, 
        issues: List[Dict[str, Any]],
        outcome_id: Optional[str] = None
    ) -> OperationOutcome:
        """Create a FHIR OperationOutcome resource"""
        if not outcome_id:
            outcome_id = str(uuid.uuid4())
            
        return OperationOutcome(
            id=outcome_id,
            issue=issues
        )
    
    def create_coding(
        self, 
        system: str, 
        code: str, 
        display: Optional[str] = None,
        version: Optional[str] = None
    ) -> Coding:
        """Create a FHIR Coding"""
        return Coding(
            system=system,
            version=version,
            code=code,
            display=display
        )
    
    def create_codeable_concept(
        self, 
        codings: List[Coding], 
        text: Optional[str] = None
    ) -> CodeableConcept:
        """Create a FHIR CodeableConcept"""
        return CodeableConcept(
            coding=codings,
            text=text
        )
    
    def create_loinc_coding(self, loinc_code: str, display: str) -> Coding:
        """Create a LOINC coding"""
        return self.create_coding(
            system="http://loinc.org",
            code=loinc_code,
            display=display
        )
    
    def create_snomed_coding(self, snomed_code: str, display: str) -> Coding:
        """Create a SNOMED CT coding"""
        return self.create_coding(
            system="http://snomed.info/sct",
            code=snomed_code,
            display=display
        )


# Global FHIR service instance
fhir_service = FHIRService()