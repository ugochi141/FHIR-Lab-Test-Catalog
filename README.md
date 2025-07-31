# FHIR Lab Test Catalog API

A comprehensive, FHIR R4 compliant REST API for laboratory test catalog management. This system provides standardized access to laboratory test definitions, reference ranges, specimen requirements, and clinical decision support information.

## 🚀 Live Demo
**Production API**: [https://fhir-lab-catalog-api.railway.app](https://fhir-lab-catalog-api.railway.app)  
**Interactive Docs**: [https://fhir-lab-catalog-api.railway.app/docs](https://fhir-lab-catalog-api.railway.app/docs)  
**FHIR Endpoint**: [https://fhir-lab-catalog-api.railway.app/LabTestDefinition](https://fhir-lab-catalog-api.railway.app/LabTestDefinition)

*Live API Features:*
- FHIR R4 compliant endpoints
- Interactive API documentation (Swagger UI)
- Real-time search and filtering
- Complete lab test catalog with 50+ tests

## 🔬 Features

### FHIR R4 Compliance
- **Full FHIR R4 Support**: Complete implementation of FHIR R4 specification
- **Standard Resources**: ObservationDefinition, SpecimenDefinition, Bundle, OperationOutcome
- **FHIR Validation**: Comprehensive validation against FHIR specifications
- **Terminology Support**: LOINC, SNOMED CT, and custom terminology systems

### Lab Test Management
- **Comprehensive Test Definitions**: Complete lab test catalog with clinical context
- **Reference Ranges**: Age, gender, and condition-specific reference ranges
- **Critical Values**: Configurable critical value thresholds
- **Specimen Requirements**: Detailed specimen collection and handling instructions
- **Quality Specifications**: Precision, accuracy, and analytical method information

### Advanced Search & Discovery
- **Full-Text Search**: Search across test names, descriptions, and clinical purposes
- **Faceted Filtering**: Filter by category, status, specimen type, and coding systems
- **FHIR Search Parameters**: Standard FHIR search parameter support
- **Pagination & Sorting**: Efficient handling of large result sets

### Standards Integration
- **LOINC Codes**: Primary coding system for laboratory tests
- **SNOMED CT**: Clinical terminology for specimens and procedures
- **HL7 FHIR**: Full compliance with HL7 FHIR R4 specification
- **Extensible**: Support for custom coding systems and extensions

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/ugochi141/FHIR-Lab-Test-Catalog.git
cd FHIR-Lab-Test-Catalog

# Start with Docker Compose
docker-compose up -d

# The API will be available at http://localhost:8000
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/ugochi141/FHIR-Lab-Test-Catalog.git
cd FHIR-Lab-Test-Catalog

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.api.endpoints:app --reload

# API available at http://localhost:8000
```

### Populate Sample Data

```bash
# Run the sample data script
python data/sample_data.py
```

## 📖 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key Endpoints

#### Lab Test Definitions
```http
GET    /LabTestDefinition           # Search lab tests
POST   /LabTestDefinition           # Create lab test
GET    /LabTestDefinition/{id}      # Get specific lab test
PUT    /LabTestDefinition/{id}      # Update lab test
DELETE /LabTestDefinition/{id}      # Delete lab test
```

#### FHIR Resources
```http
GET /ObservationDefinition/{id}     # Get observation definition
GET /SpecimenDefinition/{id}        # Get specimen definition
GET /Bundle/lab-tests               # Get tests as FHIR Bundle
```

#### Search & Discovery
```http
GET /LabTestDefinition?query=glucose                    # Text search
GET /LabTestDefinition?category=chemistry               # Filter by category
GET /LabTestDefinition?status=active                    # Filter by status
GET /LabTestDefinition?code=33747-0                     # Filter by LOINC code
GET /LabTestDefinition?_count=20&_offset=40            # Pagination
```

#### Validation & Metadata
```http
POST /LabTestDefinition/$validate   # Validate test definition
GET  /metadata/statistics           # Catalog statistics
GET  /metadata/categories           # Available categories
GET  /health                        # Health check
```

## 📊 Sample Data

The system includes comprehensive sample data for common laboratory tests:

- **Complete Blood Count (CBC)** - Hematology panel with differential
- **Basic Metabolic Panel (BMP)** - Chemistry panel for kidney/electrolyte function
- **Thyroid Stimulating Hormone (TSH)** - Endocrine function test
- **Hemoglobin A1c** - Diabetes monitoring test
- **Lipid Panel** - Cardiovascular risk assessment

Each sample includes:
- FHIR-compliant ObservationDefinition and SpecimenDefinition
- LOINC and SNOMED CT codes
- Reference ranges and critical values
- Specimen requirements and patient preparation
- Turnaround times and cost information

## 🏗️ Architecture

### Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **SQLAlchemy**: Python SQL toolkit and ORM
- **SQLite/PostgreSQL**: Database options for development and production
- **AsyncIO**: Asynchronous programming for high performance

### FHIR Implementation
```python
# Example: Creating a lab test definition
from app.models.fhir_models import LabTestDefinition, ObservationDefinition
from app.services.fhir_service import fhir_service

# Create FHIR-compliant lab test
test = LabTestDefinition(
    id="test-glucose-001",
    name="Blood Glucose Test",
    code=fhir_service.create_codeable_concept([
        fhir_service.create_loinc_coding("33747-0", "Blood glucose level")
    ]),
    status=PublicationStatus.ACTIVE,
    description="Blood glucose test measures blood sugar levels",
    observation_definition=observation_def,
    specimen_definition=specimen_def
)
```

### Database Schema
- **lab_test_definitions**: Main table for test definitions
- **search_index**: Optimized search indexing
- **audit_log**: Complete audit trail of changes

## 🔍 Search Capabilities

### Full-Text Search
```http
GET /LabTestDefinition?query=diabetes glucose hemoglobin
```

### Advanced Filtering
```http
GET /LabTestDefinition?category=chemistry&status=active&specimen_type=serum
```

### FHIR Search Parameters
```http
GET /LabTestDefinition?code:in=33747-0,4548-4&_sort=name&_count=50
```

### Faceted Search Results
```json
{
  "total": 156,
  "count": 20,
  "results": [...],
  "facets": {
    "category": {"chemistry": 45, "hematology": 32},
    "status": {"active": 140, "draft": 16}
  }
}
```

## 🛡️ FHIR Validation

### Comprehensive Validation
- **Required Fields**: Validates all mandatory FHIR elements
- **Terminology Validation**: Checks coding system consistency
- **Reference Validation**: Validates resource references
- **Business Rules**: Custom validation rules for lab contexts

### Validation Response
```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "required",
      "details": "Test name is required"
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=sqlite:///./fhir_lab_catalog.db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

### Docker Configuration
```yaml
# docker-compose.yml
services:
  fhir-lab-catalog:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres/db
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py -v
```

### Test Coverage
- **API Endpoints**: Complete test coverage for all endpoints
- **FHIR Validation**: Validation logic testing
- **Database Operations**: CRUD operations testing
- **Search Functionality**: Search and filtering tests

## 📈 Production Deployment

### Docker Deployment
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale the API service
docker-compose up --scale fhir-lab-catalog=3
```

### Environment Setup
```bash
# Production environment variables
export DATABASE_URL=postgresql://user:pass@host:5432/db
export REDIS_URL=redis://redis:6379
export LOG_LEVEL=INFO
```

### Health Monitoring
```http
GET /health
```
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

## 🎯 Use Cases

### Laboratory Information Systems (LIS)
- **Test Catalog Management**: Maintain comprehensive test catalogs
- **Reference Range Updates**: Manage age/gender-specific ranges
- **Quality Control**: Track analytical performance specifications

### Electronic Health Records (EHR)
- **Order Entry**: Standardized test ordering interfaces
- **Results Interpretation**: Reference ranges and critical values
- **Clinical Decision Support**: Evidence-based test recommendations

### Healthcare Integration
- **HL7 FHIR Integration**: Standard-compliant healthcare interoperability
- **Terminology Services**: LOINC and SNOMED CT integration
- **Quality Reporting**: Laboratory quality metrics and analytics

## 🤝 Contributing

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/FHIR-Lab-Test-Catalog.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest tests/

# Submit pull request
```

### Code Standards
- **Python**: Follow PEP 8 style guidelines
- **FHIR**: Comply with FHIR R4 specification
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update API documentation for changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

### Documentation
- **API Docs**: http://localhost:8000/docs
- **FHIR Specification**: https://hl7.org/fhir/R4/
- **LOINC**: https://loinc.org/
- **SNOMED CT**: https://www.snomed.org/

### Community
- **Issues**: [GitHub Issues](https://github.com/ugochi141/FHIR-Lab-Test-Catalog/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ugochi141/FHIR-Lab-Test-Catalog/discussions)

---

**FHIR Lab Test Catalog API** - Standardizing laboratory test information for better healthcare interoperability.