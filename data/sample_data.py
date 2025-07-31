"""
Sample FHIR-compliant lab test data for testing and demonstration
"""

from datetime import datetime
from app.models.fhir_models import (
    LabTestDefinition, ObservationDefinition, SpecimenDefinition,
    Coding, CodeableConcept, PublicationStatus, Quantity, Range
)
from app.services.fhir_service import fhir_service


def create_sample_lab_tests():
    """Create sample lab test definitions"""
    
    sample_tests = []
    
    # 1. Complete Blood Count (CBC)
    cbc_observation_def = ObservationDefinition(
        id="obs-def-cbc",
        status=PublicationStatus.ACTIVE,
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("57021-8", "CBC W Auto Differential panel - Blood")
        ], "Complete Blood Count with Automated Differential"),
        category=[fhir_service.create_codeable_concept([
            fhir_service.create_coding("http://terminology.hl7.org/CodeSystem/observation-category", "laboratory", "Laboratory")
        ])],
        permitted_data_type=["Quantity"],
        multiple_results_allowed=True,
        preferred_report_name="Complete Blood Count"
    )
    
    cbc_specimen_def = SpecimenDefinition(
        id="spec-def-cbc",
        status=PublicationStatus.ACTIVE,
        type_collected=fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("119297000", "Blood specimen")
        ], "Whole blood"),
        patient_preparation=["No special preparation required"],
        time_aspect="Random",
        collection=[fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("28520004", "Venipuncture")
        ])]
    )
    
    cbc_test = LabTestDefinition(
        id="test-cbc-001",
        name="Complete Blood Count with Automated Differential",
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("57021-8", "CBC W Auto Differential panel - Blood"),
            fhir_service.create_snomed_coding("26604007", "Complete blood count")
        ], "Complete Blood Count with Automated Differential"),
        status=PublicationStatus.ACTIVE,
        category=[
            fhir_service.create_codeable_concept([
                fhir_service.create_coding("http://example.org/lab-categories", "hematology", "Hematology")
            ])
        ],
        description="A complete blood count (CBC) is a blood test used to evaluate your overall health and detect a wide range of disorders, including anemia, infection and leukemia.",
        clinical_purpose="Screening for blood disorders, monitoring treatment response, routine health assessment",
        observation_definition=cbc_observation_def,
        specimen_definition=cbc_specimen_def,
        reference_ranges=[
            {
                "parameter": "WBC",
                "range": {"low": 4.5, "high": 11.0, "unit": "10^3/uL"},
                "age_range": "Adult"
            },
            {
                "parameter": "RBC",
                "range": {"low": 4.2, "high": 5.4, "unit": "10^6/uL"},
                "age_range": "Adult",
                "gender": "Female"
            },
            {
                "parameter": "Hemoglobin",
                "range": {"low": 12.0, "high": 16.0, "unit": "g/dL"},
                "age_range": "Adult",
                "gender": "Female"
            }
        ],
        critical_values={
            "WBC": {"low": 2.0, "high": 50.0, "unit": "10^3/uL"},
            "Hemoglobin": {"low": 7.0, "high": 20.0, "unit": "g/dL"},
            "Platelets": {"low": 50.0, "high": 1000.0, "unit": "10^3/uL"}
        },
        analytical_method="Flow cytometry with impedance counting",
        turnaround_time={"routine": 2, "stat": 1, "unit": "hours"},
        cost={"routine": 45.00, "stat": 75.00, "currency": "USD"},
        ordering_information={
            "order_code": "CBC",
            "minimum_volume": "3 mL",
            "container": "EDTA tube (lavender top)",
            "stability": "24 hours at room temperature"
        }
    )
    sample_tests.append(cbc_test)
    
    # 2. Basic Metabolic Panel (BMP)
    bmp_observation_def = ObservationDefinition(
        id="obs-def-bmp",
        status=PublicationStatus.ACTIVE,
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("80048-0", "Basic metabolic panel - Serum or Plasma")
        ], "Basic Metabolic Panel"),
        category=[fhir_service.create_codeable_concept([
            fhir_service.create_coding("http://terminology.hl7.org/CodeSystem/observation-category", "laboratory", "Laboratory")
        ])],
        permitted_data_type=["Quantity"],
        multiple_results_allowed=True,
        preferred_report_name="Basic Metabolic Panel"
    )
    
    bmp_specimen_def = SpecimenDefinition(
        id="spec-def-bmp",
        status=PublicationStatus.ACTIVE,
        type_collected=fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("119364003", "Serum specimen")
        ], "Serum"),
        patient_preparation=["Fasting for 8-12 hours preferred but not required"],
        time_aspect="Random or fasting",
        collection=[fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("28520004", "Venipuncture")
        ])]
    )
    
    bmp_test = LabTestDefinition(
        id="test-bmp-001",
        name="Basic Metabolic Panel",
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("80048-0", "Basic metabolic panel - Serum or Plasma"),
            fhir_service.create_snomed_coding("166312007", "Basic metabolic panel")
        ], "Basic Metabolic Panel"),
        status=PublicationStatus.ACTIVE,
        category=[
            fhir_service.create_codeable_concept([
                fhir_service.create_coding("http://example.org/lab-categories", "chemistry", "Clinical Chemistry")
            ])
        ],
        description="A basic metabolic panel is a group of blood tests that provides information about your body's metabolism, kidney function, and electrolyte balance.",
        clinical_purpose="Assessment of kidney function, electrolyte balance, blood sugar levels, and acid-base balance",
        observation_definition=bmp_observation_def,
        specimen_definition=bmp_specimen_def,
        reference_ranges=[
            {
                "parameter": "Glucose",
                "range": {"low": 70, "high": 100, "unit": "mg/dL"},
                "condition": "Fasting"
            },
            {
                "parameter": "Sodium",
                "range": {"low": 136, "high": 145, "unit": "mmol/L"}
            },
            {
                "parameter": "Potassium",
                "range": {"low": 3.5, "high": 5.0, "unit": "mmol/L"}
            },
            {
                "parameter": "Creatinine",
                "range": {"low": 0.6, "high": 1.2, "unit": "mg/dL"},
                "age_range": "Adult"
            }
        ],
        critical_values={
            "Glucose": {"low": 50, "high": 400, "unit": "mg/dL"},
            "Potassium": {"low": 2.5, "high": 6.5, "unit": "mmol/L"},
            "Sodium": {"low": 120, "high": 160, "unit": "mmol/L"},
            "Creatinine": {"high": 4.0, "unit": "mg/dL"}
        },
        analytical_method="Ion-selective electrode and enzymatic methods",
        turnaround_time={"routine": 4, "stat": 1, "unit": "hours"},
        cost={"routine": 35.00, "stat": 60.00, "currency": "USD"},
        ordering_information={
            "order_code": "BMP",
            "minimum_volume": "2 mL",
            "container": "Gold top (SST) or red top tube",
            "stability": "7 days refrigerated"
        }
    )
    sample_tests.append(bmp_test)
    
    # 3. Thyroid Stimulating Hormone (TSH)
    tsh_observation_def = ObservationDefinition(
        id="obs-def-tsh",
        status=PublicationStatus.ACTIVE,
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("3016-3", "Thyrotropin [Units/volume] in Serum or Plasma")
        ], "Thyroid Stimulating Hormone"),
        category=[fhir_service.create_codeable_concept([
            fhir_service.create_coding("http://terminology.hl7.org/CodeSystem/observation-category", "laboratory", "Laboratory")
        ])],
        permitted_data_type=["Quantity"],
        multiple_results_allowed=False,
        preferred_report_name="TSH"
    )
    
    tsh_specimen_def = SpecimenDefinition(
        id="spec-def-tsh",
        status=PublicationStatus.ACTIVE,
        type_collected=fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("119364003", "Serum specimen")
        ], "Serum"),
        patient_preparation=["No special preparation required"],
        time_aspect="Random",
        collection=[fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("28520004", "Venipuncture")
        ])]
    )
    
    tsh_test = LabTestDefinition(
        id="test-tsh-001",
        name="Thyroid Stimulating Hormone",
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("3016-3", "Thyrotropin [Units/volume] in Serum or Plasma"),
            fhir_service.create_snomed_coding("61167004", "Thyroid stimulating hormone measurement")
        ], "Thyroid Stimulating Hormone (TSH)"),
        status=PublicationStatus.ACTIVE,
        category=[
            fhir_service.create_codeable_concept([
                fhir_service.create_coding("http://example.org/lab-categories", "endocrinology", "Endocrinology")
            ])
        ],
        description="TSH is a hormone produced by the pituitary gland that regulates thyroid function. This test is used to diagnose thyroid disorders.",
        clinical_purpose="Diagnosis of hyperthyroidism and hypothyroidism, monitoring thyroid hormone replacement therapy",
        observation_definition=tsh_observation_def,
        specimen_definition=tsh_specimen_def,
        reference_ranges=[
            {
                "parameter": "TSH",
                "range": {"low": 0.4, "high": 4.0, "unit": "mIU/L"},
                "age_range": "Adult"
            }
        ],
        critical_values={
            "TSH": {"low": 0.01, "high": 100.0, "unit": "mIU/L"}
        },
        analytical_method="Chemiluminescent immunoassay (CLIA)",
        turnaround_time={"routine": 24, "stat": 4, "unit": "hours"},
        cost={"routine": 75.00, "stat": 125.00, "currency": "USD"},
        ordering_information={
            "order_code": "TSH",
            "minimum_volume": "1 mL",
            "container": "Gold top (SST) or red top tube",
            "stability": "7 days refrigerated, 2 days at room temperature"
        }
    )
    sample_tests.append(tsh_test)
    
    # 4. Hemoglobin A1c
    hba1c_observation_def = ObservationDefinition(
        id="obs-def-hba1c",
        status=PublicationStatus.ACTIVE,
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood")
        ], "Hemoglobin A1c"),
        category=[fhir_service.create_codeable_concept([
            fhir_service.create_coding("http://terminology.hl7.org/CodeSystem/observation-category", "laboratory", "Laboratory")
        ])],
        permitted_data_type=["Quantity"],
        multiple_results_allowed=False,
        preferred_report_name="Hemoglobin A1c"
    )
    
    hba1c_specimen_def = SpecimenDefinition(
        id="spec-def-hba1c",
        status=PublicationStatus.ACTIVE,
        type_collected=fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("119297000", "Blood specimen")
        ], "Whole blood"),
        patient_preparation=["No fasting required"],
        time_aspect="Random",
        collection=[fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("28520004", "Venipuncture")
        ])]
    )
    
    hba1c_test = LabTestDefinition(
        id="test-hba1c-001",
        name="Hemoglobin A1c",
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood"),
            fhir_service.create_snomed_coding("43396009", "Hemoglobin A1c measurement")
        ], "Hemoglobin A1c (HbA1c)"),
        status=PublicationStatus.ACTIVE,
        category=[
            fhir_service.create_codeable_concept([
                fhir_service.create_coding("http://example.org/lab-categories", "chemistry", "Clinical Chemistry")
            ])
        ],
        description="Hemoglobin A1c reflects average blood glucose levels over the past 2-3 months and is used for diabetes diagnosis and monitoring.",
        clinical_purpose="Diagnosis of diabetes mellitus, monitoring long-term glycemic control in diabetic patients",
        observation_definition=hba1c_observation_def,
        specimen_definition=hba1c_specimen_def,
        reference_ranges=[
            {
                "parameter": "HbA1c",
                "range": {"low": 4.0, "high": 5.6, "unit": "%"},
                "interpretation": "Normal"
            },
            {
                "parameter": "HbA1c",
                "range": {"low": 5.7, "high": 6.4, "unit": "%"},
                "interpretation": "Prediabetes"
            },
            {
                "parameter": "HbA1c",
                "range": {"low": 6.5, "unit": "%"},
                "interpretation": "Diabetes"
            }
        ],
        critical_values={
            "HbA1c": {"high": 15.0, "unit": "%"}
        },
        analytical_method="High-performance liquid chromatography (HPLC)",
        turnaround_time={"routine": 24, "stat": 4, "unit": "hours"},
        cost={"routine": 85.00, "stat": 140.00, "currency": "USD"},
        ordering_information={
            "order_code": "HBA1C",
            "minimum_volume": "2 mL",
            "container": "EDTA tube (lavender top)",
            "stability": "7 days refrigerated"
        }
    )
    sample_tests.append(hba1c_test)
    
    # 5. Lipid Panel
    lipid_observation_def = ObservationDefinition(
        id="obs-def-lipid",
        status=PublicationStatus.ACTIVE,
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("57698-3", "Lipid panel with direct LDL - Serum or Plasma")
        ], "Lipid Panel"),
        category=[fhir_service.create_codeable_concept([
            fhir_service.create_coding("http://terminology.hl7.org/CodeSystem/observation-category", "laboratory", "Laboratory")
        ])],
        permitted_data_type=["Quantity"],
        multiple_results_allowed=True,
        preferred_report_name="Lipid Panel"
    )
    
    lipid_specimen_def = SpecimenDefinition(
        id="spec-def-lipid",
        status=PublicationStatus.ACTIVE,
        type_collected=fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("119364003", "Serum specimen")
        ], "Serum"),
        patient_preparation=["Fasting for 9-12 hours required"],
        time_aspect="Fasting",
        collection=[fhir_service.create_codeable_concept([
            fhir_service.create_snomed_coding("28520004", "Venipuncture")
        ])]
    )
    
    lipid_test = LabTestDefinition(
        id="test-lipid-001",
        name="Lipid Panel",
        code=fhir_service.create_codeable_concept([
            fhir_service.create_loinc_coding("57698-3", "Lipid panel with direct LDL - Serum or Plasma"),
            fhir_service.create_snomed_coding("252253000", "Lipid studies")
        ], "Lipid Panel"),
        status=PublicationStatus.ACTIVE,
        category=[
            fhir_service.create_codeable_concept([
                fhir_service.create_coding("http://example.org/lab-categories", "chemistry", "Clinical Chemistry")
            ])
        ],
        description="A lipid panel measures cholesterol and triglycerides in the blood to assess cardiovascular disease risk.",
        clinical_purpose="Assessment of cardiovascular disease risk, monitoring lipid-lowering therapy",
        observation_definition=lipid_observation_def,
        specimen_definition=lipid_specimen_def,
        reference_ranges=[
            {
                "parameter": "Total Cholesterol",
                "range": {"high": 200, "unit": "mg/dL"},
                "interpretation": "Desirable"
            },
            {
                "parameter": "LDL Cholesterol",
                "range": {"high": 100, "unit": "mg/dL"},
                "interpretation": "Optimal"
            },
            {
                "parameter": "HDL Cholesterol",
                "range": {"low": 40, "unit": "mg/dL"},
                "interpretation": "Low (Male)"
            },
            {
                "parameter": "Triglycerides",
                "range": {"high": 150, "unit": "mg/dL"},
                "interpretation": "Normal"
            }
        ],
        analytical_method="Enzymatic methods",
        turnaround_time={"routine": 24, "stat": 4, "unit": "hours"},
        cost={"routine": 55.00, "stat": 90.00, "currency": "USD"},
        ordering_information={
            "order_code": "LIPID",
            "minimum_volume": "2 mL",
            "container": "Gold top (SST) or red top tube",
            "stability": "7 days refrigerated",
            "special_instructions": "Patient must fast 9-12 hours"
        }
    )
    sample_tests.append(lipid_test)
    
    return sample_tests


async def populate_sample_data():
    """Populate the database with sample lab test data"""
    sample_tests = create_sample_lab_tests()
    
    created_tests = []
    for test in sample_tests:
        try:
            created_test = await fhir_service.create_lab_test(test)
            created_tests.append(created_test)
            print(f"Created test: {created_test.name}")
        except Exception as e:
            print(f"Failed to create test {test.name}: {str(e)}")
    
    return created_tests


if __name__ == "__main__":
    import asyncio
    from app.core.database import db_manager
    
    async def main():
        await db_manager.connect()
        await db_manager.create_tables()
        
        print("Populating sample data...")
        tests = await populate_sample_data()
        print(f"Created {len(tests)} sample lab tests")
        
        await db_manager.disconnect()
    
    asyncio.run(main())