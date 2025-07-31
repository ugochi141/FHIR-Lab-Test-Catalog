#!/usr/bin/env python3
"""
FHIR Lab Test Catalog API - Main Entry Point
Enhanced version with FHIR R4 compliance and comprehensive lab test management
"""

import uvicorn
import asyncio
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.api.endpoints import app
from app.core.database import db_manager
from data.sample_data import populate_sample_data


async def initialize_application():
    """Initialize the application with database and sample data"""
    print("🚀 Initializing FHIR Lab Test Catalog API...")
    
    try:
        # Connect to database
        print("📊 Connecting to database...")
        await db_manager.connect()
        
        # Create tables
        print("🏗️  Creating database tables...")
        await db_manager.create_tables()
        
        # Check if we need to populate sample data
        stats = await db_manager.get_test_statistics()
        if stats.get("total_tests", 0) == 0:
            print("📝 Database empty, populating with sample data...")
            await populate_sample_data()
            print("✅ Sample data populated successfully!")
        else:
            print(f"📊 Database already contains {stats['total_tests']} lab tests")
        
        print("✅ Application initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return False


async def run_development_server():
    """Run the development server with initialization"""
    success = await initialize_application()
    
    if not success:
        print("❌ Application initialization failed. Exiting.")
        sys.exit(1)
    
    print("\n🌐 Starting FHIR Lab Test Catalog API server...")
    print("📋 Available endpoints:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Alternative Docs: http://localhost:8000/redoc")
    print("   • Health Check: http://localhost:8000/health")
    print("   • Lab Tests: http://localhost:8000/LabTestDefinition")
    print("   • Statistics: http://localhost:8000/metadata/statistics")
    print("\n🔍 Example searches:")
    print("   • http://localhost:8000/LabTestDefinition?query=glucose")
    print("   • http://localhost:8000/LabTestDefinition?category=chemistry")
    print("   • http://localhost:8000/Bundle/lab-tests")
    print("\n🧪 Sample lab tests included:")
    print("   • Complete Blood Count (CBC)")
    print("   • Basic Metabolic Panel (BMP)")
    print("   • Thyroid Stimulating Hormone (TSH)")
    print("   • Hemoglobin A1c")
    print("   • Lipid Panel")
    print("\n" + "="*60)
    
    # Disconnect from database (will reconnect on startup event)
    await db_manager.disconnect()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='FHIR Lab Test Catalog API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--init-only', action='store_true', help='Initialize database and exit')
    
    args = parser.parse_args()
    
    if args.init_only:
        # Just initialize and exit
        asyncio.run(initialize_application())
    else:
        # Initialize and run server
        asyncio.run(run_development_server())
        
        # Start the server
        uvicorn.run(
            "app.api.endpoints:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
            access_log=True
        )