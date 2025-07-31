"""
FHIR-compliant data models for Lab Test Catalog
Based on FHIR R4 specification
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class FHIRResourceType(str, Enum):
    """FHIR Resource Types relevant to lab testing"""
    OBSERVATION_DEFINITION = "ObservationDefinition"
    SPECIMEN_DEFINITION = "SpecimenDefinition"
    PLAN_DEFINITION = "PlanDefinition"
    ACTIVITY_DEFINITION = "ActivityDefinition"
    SERVICE_REQUEST = "ServiceRequest"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    OBSERVATION = "Observation"
    SPECIMEN = "Specimen"


class PublicationStatus(str, Enum):
    """Publication status for FHIR resources"""
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"
    UNKNOWN = "unknown"


class ObservationStatus(str, Enum):
    """Status of observations"""
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class SpecimenStatus(str, Enum):
    """Status of specimens"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNSATISFACTORY = "unsatisfactory"
    ENTERED_IN_ERROR = "entered-in-error"


class Coding(BaseModel):
    """FHIR Coding datatype"""
    system: Optional[str] = Field(None, description="Identity of the terminology system")
    version: Optional[str] = Field(None, description="Version of the system")
    code: Optional[str] = Field(None, description="Symbol in syntax defined by the system")
    display: Optional[str] = Field(None, description="Representation defined by the system")
    user_selected: Optional[bool] = Field(None, alias="userSelected", description="If this coding was chosen directly by the user")


class CodeableConcept(BaseModel):
    """FHIR CodeableConcept datatype"""
    coding: Optional[List[Coding]] = Field(None, description="Code defined by a terminology system")
    text: Optional[str] = Field(None, description="Plain text representation of the concept")


class Identifier(BaseModel):
    """FHIR Identifier datatype"""
    use: Optional[str] = Field(None, description="usual | official | temp | secondary | old")
    type: Optional[CodeableConcept] = Field(None, description="Description of identifier")
    system: Optional[str] = Field(None, description="The namespace for the identifier value")
    value: Optional[str] = Field(None, description="The value that is unique")
    period: Optional[Dict[str, Any]] = Field(None, description="Time period when id is/was valid for use")
    assigner: Optional[Dict[str, Any]] = Field(None, description="Organization that issued id")


class Reference(BaseModel):
    """FHIR Reference datatype"""
    reference: Optional[str] = Field(None, description="Literal reference, Relative, internal or absolute URL")
    type: Optional[str] = Field(None, description="Type the reference refers to")
    identifier: Optional[Identifier] = Field(None, description="Logical reference, when literal reference is not known")
    display: Optional[str] = Field(None, description="Text alternative for the resource")


class Quantity(BaseModel):
    """FHIR Quantity datatype"""
    value: Optional[float] = Field(None, description="Numerical value")
    comparator: Optional[str] = Field(None, description="< | <= | >= | > - how to understand the value")
    unit: Optional[str] = Field(None, description="Unit representation")
    system: Optional[str] = Field(None, description="System that defines coded unit form")
    code: Optional[str] = Field(None, description="Coded form of the unit")


class Range(BaseModel):
    """FHIR Range datatype"""
    low: Optional[Quantity] = Field(None, description="Low limit")
    high: Optional[Quantity] = Field(None, description="High limit")


class Ratio(BaseModel):
    """FHIR Ratio datatype"""
    numerator: Optional[Quantity] = Field(None, description="Numerator value")
    denominator: Optional[Quantity] = Field(None, description="Denominator value")


class Period(BaseModel):
    """FHIR Period datatype"""
    start: Optional[datetime] = Field(None, description="Starting time with inclusive boundary")
    end: Optional[datetime] = Field(None, description="End time with inclusive boundary")


class Meta(BaseModel):
    """FHIR Meta datatype"""
    version_id: Optional[str] = Field(None, alias="versionId", description="Version specific identifier")
    last_updated: Optional[datetime] = Field(None, alias="lastUpdated", description="When the resource version last changed")
    source: Optional[str] = Field(None, description="Identifies where the resource comes from")
    profile: Optional[List[str]] = Field(None, description="Profiles this resource claims to conform to")
    security: Optional[List[Coding]] = Field(None, description="Security Labels applied to this resource")
    tag: Optional[List[Coding]] = Field(None, description="Tags applied to this resource")


class ObservationDefinition(BaseModel):
    """FHIR ObservationDefinition Resource"""
    resource_type: Literal["ObservationDefinition"] = Field("ObservationDefinition", alias="resourceType")
    id: Optional[str] = Field(None, description="Logical id of this artifact")
    meta: Optional[Meta] = Field(None, description="Metadata about the resource")
    implicit_rules: Optional[str] = Field(None, alias="implicitRules", description="A set of rules under which this content was created")
    language: Optional[str] = Field(None, description="Language of the resource content")
    
    # ObservationDefinition specific fields
    url: Optional[str] = Field(None, description="Canonical identifier for this observation definition")
    identifier: Optional[List[Identifier]] = Field(None, description="Additional identifier for the observation definition")
    version: Optional[str] = Field(None, description="Business version of the observation definition")
    name: Optional[str] = Field(None, description="Name for this observation definition (computer friendly)")
    title: Optional[str] = Field(None, description="Name for this observation definition (human friendly)")
    status: PublicationStatus = Field(..., description="draft | active | retired | unknown")
    experimental: Optional[bool] = Field(None, description="For testing purposes, not real usage")
    date: Optional[datetime] = Field(None, description="Date last changed")
    publisher: Optional[str] = Field(None, description="Name of the publisher")
    contact: Optional[List[Dict[str, Any]]] = Field(None, description="Contact details for the publisher")
    description: Optional[str] = Field(None, description="Natural language description of the observation definition")
    use_context: Optional[List[Dict[str, Any]]] = Field(None, alias="useContext", description="The context that the content is intended to support")
    jurisdiction: Optional[List[CodeableConcept]] = Field(None, description="Intended jurisdiction for observation definition")
    purpose: Optional[str] = Field(None, description="Why this observation definition is defined")
    copyright: Optional[str] = Field(None, description="Use and/or publishing restrictions")
    approval_date: Optional[datetime] = Field(None, alias="approvalDate", description="When the observation definition was approved by publisher")
    last_review_date: Optional[datetime] = Field(None, alias="lastReviewDate", description="When the observation definition was last reviewed")
    effective_period: Optional[Period] = Field(None, alias="effectivePeriod", description="When the observation definition is expected to be used")
    
    # Core observation definition content
    category: Optional[List[CodeableConcept]] = Field(None, description="Classification of type of observation")
    code: CodeableConcept = Field(..., description="Type of observation (code / type)")
    permitted_data_type: Optional[List[str]] = Field(None, alias="permittedDataType", description="Quantity | CodeableConcept | string | boolean | integer | Range | Ratio | SampledData | time | dateTime | Period")
    multiple_results_allowed: Optional[bool] = Field(None, alias="multipleResultsAllowed", description="Multiple results allowed")
    method: Optional[CodeableConcept] = Field(None, description="Method used to produce the observation")
    preferred_report_name: Optional[str] = Field(None, alias="preferredReportName", description="Preferred report name")
    
    # Reference ranges and critical values
    quantitative_details: Optional[Dict[str, Any]] = Field(None, alias="quantitativeDetails", description="Characteristics of quantitative results")
    qualified_interval: Optional[List[Dict[str, Any]]] = Field(None, alias="qualifiedInterval", description="Qualified range for continuous and ordinal observation")
    valid_coded_value_set: Optional[Reference] = Field(None, alias="validCodedValueSet", description="Value set of valid coded values for the observations conforming to this ObservationDefinition")
    normal_coded_value_set: Optional[Reference] = Field(None, alias="normalCodedValueSet", description="Value set of normal coded values for the observations conforming to this ObservationDefinition")
    abnormal_coded_value_set: Optional[Reference] = Field(None, alias="abnormalCodedValueSet", description="Value set of abnormal coded values for the observations conforming to this ObservationDefinition")
    critical_coded_value_set: Optional[Reference] = Field(None, alias="criticalCodedValueSet", description="Value set of critical coded values for the observations conforming to this ObservationDefinition")


class SpecimenDefinition(BaseModel):
    """FHIR SpecimenDefinition Resource"""
    resource_type: Literal["SpecimenDefinition"] = Field("SpecimenDefinition", alias="resourceType")
    id: Optional[str] = Field(None, description="Logical id of this artifact")
    meta: Optional[Meta] = Field(None, description="Metadata about the resource")
    
    # SpecimenDefinition specific fields  
    url: Optional[str] = Field(None, description="Canonical identifier for this specimen definition")
    identifier: Optional[List[Identifier]] = Field(None, description="Additional identifier for the specimen definition")
    version: Optional[str] = Field(None, description="Business version of the specimen definition")
    name: Optional[str] = Field(None, description="Name for this specimen definition")
    title: Optional[str] = Field(None, description="Name for this specimen definition (human friendly)")
    status: PublicationStatus = Field(..., description="draft | active | retired | unknown")
    experimental: Optional[bool] = Field(None, description="For testing purposes, not real usage")
    subject_codeable_concept: Optional[CodeableConcept] = Field(None, alias="subjectCodeableConcept", description="Type of subject for the specimen definition")
    subject_reference: Optional[Reference] = Field(None, alias="subjectReference", description="Type of subject for the specimen definition")
    date: Optional[datetime] = Field(None, description="Date last changed")
    publisher: Optional[str] = Field(None, description="Name of the publisher")
    contact: Optional[List[Dict[str, Any]]] = Field(None, description="Contact details for the publisher")
    description: Optional[str] = Field(None, description="Natural language description of the specimen definition")
    use_context: Optional[List[Dict[str, Any]]] = Field(None, alias="useContext", description="The context that the content is intended to support")
    jurisdiction: Optional[List[CodeableConcept]] = Field(None, description="Intended jurisdiction for specimen definition")
    purpose: Optional[str] = Field(None, description="Why this specimen definition is defined")
    copyright: Optional[str] = Field(None, description="Use and/or publishing restrictions")
    
    # Specimen collection and handling
    type_collected: Optional[CodeableConcept] = Field(None, alias="typeCollected", description="Kind of material to collect")
    patient_preparation: Optional[List[str]] = Field(None, alias="patientPreparation", description="Patient preparation for collection")
    time_aspect: Optional[str] = Field(None, alias="timeAspect", description="Time aspect for collection")
    collection: Optional[List[CodeableConcept]] = Field(None, description="Specimen collection procedure")
    type_tested: Optional[List[Dict[str, Any]]] = Field(None, alias="typeTested", description="Specimen in container intended for testing by lab")


class LabTestDefinition(BaseModel):
    """Enhanced Lab Test Definition combining ObservationDefinition and SpecimenDefinition"""
    # Basic Information
    id: str = Field(..., description="Unique identifier for the lab test")
    name: str = Field(..., description="Human-readable name of the test")
    code: CodeableConcept = Field(..., description="Coded representation of the test")
    status: PublicationStatus = Field(PublicationStatus.ACTIVE, description="Publication status")
    version: str = Field("1.0.0", description="Version of this test definition")
    
    # Clinical Information
    category: List[CodeableConcept] = Field(..., description="Test categories (e.g., chemistry, hematology)")
    description: str = Field(..., description="Clinical description of the test")
    clinical_purpose: Optional[str] = Field(None, description="Clinical purpose and indications")
    
    # Technical Specifications
    observation_definition: ObservationDefinition = Field(..., description="FHIR ObservationDefinition")
    specimen_definition: Optional[SpecimenDefinition] = Field(None, description="FHIR SpecimenDefinition")
    
    # Reference Ranges and Critical Values
    reference_ranges: Optional[List[Dict[str, Any]]] = Field(None, description="Normal reference ranges")
    critical_values: Optional[Dict[str, Any]] = Field(None, description="Critical value thresholds")
    
    # Quality and Validation
    analytical_method: Optional[str] = Field(None, description="Analytical method used")
    precision: Optional[Dict[str, float]] = Field(None, description="Precision specifications")
    accuracy: Optional[Dict[str, float]] = Field(None, description="Accuracy specifications")
    
    # Operational Information
    turnaround_time: Optional[Dict[str, int]] = Field(None, description="Expected turnaround times")
    cost: Optional[Dict[str, float]] = Field(None, description="Cost information")
    ordering_information: Optional[Dict[str, Any]] = Field(None, description="How to order this test")
    
    # Metadata
    created_date: datetime = Field(default_factory=datetime.utcnow, description="When this definition was created")
    modified_date: datetime = Field(default_factory=datetime.utcnow, description="When this definition was last modified")
    created_by: Optional[str] = Field(None, description="Who created this definition")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchParameters(BaseModel):
    """Search parameters for lab test catalog"""
    query: Optional[str] = Field(None, description="Text search across test names and descriptions")
    category: Optional[List[str]] = Field(None, description="Filter by test categories")
    status: Optional[List[PublicationStatus]] = Field(None, description="Filter by publication status")
    specimen_type: Optional[List[str]] = Field(None, description="Filter by specimen types")
    code_system: Optional[str] = Field(None, description="Filter by coding system (LOINC, SNOMED, etc.)")
    code: Optional[str] = Field(None, description="Filter by specific test codes")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: Optional[str] = Field("name", description="Field to sort by")
    sort_order: Optional[str] = Field("asc", description="Sort order: asc or desc")


class SearchResults(BaseModel):
    """Search results response"""
    total: int = Field(..., description="Total number of matching tests")
    count: int = Field(..., description="Number of tests in this response")
    offset: int = Field(..., description="Offset used for this search")
    results: List[LabTestDefinition] = Field(..., description="Matching lab test definitions")
    facets: Optional[Dict[str, Any]] = Field(None, description="Search facets for filtering")


class BundleEntry(BaseModel):
    """FHIR Bundle entry"""
    fullUrl: Optional[str] = Field(None, description="URI for resource (Absolute or relative)")
    resource: Union[ObservationDefinition, SpecimenDefinition, LabTestDefinition] = Field(..., description="A resource in the bundle")
    search: Optional[Dict[str, Any]] = Field(None, description="Search related information")
    request: Optional[Dict[str, Any]] = Field(None, description="Additional execution information")
    response: Optional[Dict[str, Any]] = Field(None, description="Results of execution")


class Bundle(BaseModel):
    """FHIR Bundle Resource"""
    resourceType: Literal["Bundle"] = Field("Bundle")
    id: Optional[str] = Field(None, description="Logical id of this artifact")
    meta: Optional[Meta] = Field(None, description="Metadata about the resource")
    identifier: Optional[Identifier] = Field(None, description="Persistent identifier for the bundle")
    type: str = Field(..., description="document | message | transaction | transaction-response | batch | batch-response | history | searchset | collection")
    timestamp: Optional[datetime] = Field(None, description="When the bundle was assembled")
    total: Optional[int] = Field(None, description="If search, the total number of matches")
    link: Optional[List[Dict[str, str]]] = Field(None, description="Links related to this Bundle")
    entry: Optional[List[BundleEntry]] = Field(None, description="Entry in the bundle - will have a resource or information")
    signature: Optional[Dict[str, Any]] = Field(None, description="Digital Signature")


class OperationOutcome(BaseModel):
    """FHIR OperationOutcome Resource"""
    resourceType: Literal["OperationOutcome"] = Field("OperationOutcome")
    id: Optional[str] = Field(None, description="Logical id of this artifact")
    meta: Optional[Meta] = Field(None, description="Metadata about the resource")
    issue: List[Dict[str, Any]] = Field(..., description="A single issue associated with the action")