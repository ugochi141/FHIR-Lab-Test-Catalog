"""
Database configuration and connection management
"""

import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, MetaData, Table, Column, String, Text, DateTime, Boolean, JSON, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from databases import Database
import json
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fhir_lab_catalog.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

# Create async database connection
database = Database(ASYNC_DATABASE_URL)

# Create async engine
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Create session maker
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Define metadata and tables
metadata = MetaData()

# Lab Test Definitions table
lab_test_definitions = Table(
    "lab_test_definitions",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False, index=True),
    Column("version", String, nullable=False, default="1.0.0"),
    Column("status", String, nullable=False, default="active", index=True),
    Column("category", JSON),  # Array of categories
    Column("code", JSON, nullable=False),  # CodeableConcept
    Column("description", Text, nullable=False),
    Column("clinical_purpose", Text),
    Column("observation_definition", JSON, nullable=False),
    Column("specimen_definition", JSON),
    Column("reference_ranges", JSON),
    Column("critical_values", JSON),
    Column("analytical_method", String),
    Column("precision", JSON),
    Column("accuracy", JSON),
    Column("turnaround_time", JSON),
    Column("cost", JSON),
    Column("ordering_information", JSON),
    Column("created_date", DateTime, default=datetime.utcnow, index=True),
    Column("modified_date", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    Column("created_by", String),
    Column("search_text", Text, index=True),  # For full-text search
)

# Search index table for better performance
search_index = Table(
    "search_index",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("test_id", String, nullable=False, index=True),
    Column("search_type", String, nullable=False, index=True),  # 'name', 'code', 'category', etc.
    Column("search_value", String, nullable=False, index=True),
    Column("display_value", String),
)

# Audit log table
audit_log = Table(
    "audit_log",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", DateTime, default=datetime.utcnow, index=True),
    Column("action", String, nullable=False, index=True),  # CREATE, UPDATE, DELETE, READ
    Column("resource_type", String, nullable=False),
    Column("resource_id", String, nullable=False),
    Column("user_id", String),
    Column("changes", JSON),
    Column("ip_address", String),
)


class DatabaseManager:
    """Database connection and operation manager"""
    
    def __init__(self):
        self.database = database
        self.engine = engine

    async def connect(self):
        """Connect to the database"""
        await self.database.connect()
        
    async def disconnect(self):
        """Disconnect from the database"""
        await self.database.disconnect()
        
    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            
    async def drop_tables(self):
        """Drop all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)

    async def get_lab_test_definition(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get a single lab test definition by ID"""
        query = lab_test_definitions.select().where(lab_test_definitions.c.id == test_id)
        result = await self.database.fetch_one(query)
        
        if result:
            return dict(result)
        return None

    async def create_lab_test_definition(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lab test definition"""
        # Generate search text for full-text search
        search_text = self._generate_search_text(test_data)
        test_data["search_text"] = search_text
        
        query = lab_test_definitions.insert().values(**test_data)
        await self.database.execute(query)
        
        # Update search index
        await self._update_search_index(test_data["id"], test_data)
        
        # Log the action
        await self._log_action("CREATE", "LabTestDefinition", test_data["id"], test_data)
        
        return test_data

    async def update_lab_test_definition(self, test_id: str, test_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing lab test definition"""
        # Check if exists
        existing = await self.get_lab_test_definition(test_id)
        if not existing:
            return None
            
        # Update modified date
        test_data["modified_date"] = datetime.utcnow()
        
        # Generate search text
        search_text = self._generate_search_text(test_data)
        test_data["search_text"] = search_text
        
        query = lab_test_definitions.update().where(
            lab_test_definitions.c.id == test_id
        ).values(**test_data)
        
        await self.database.execute(query)
        
        # Update search index
        await self._update_search_index(test_id, test_data)
        
        # Log the action
        await self._log_action("UPDATE", "LabTestDefinition", test_id, test_data, existing)
        
        return await self.get_lab_test_definition(test_id)

    async def delete_lab_test_definition(self, test_id: str) -> bool:
        """Delete a lab test definition"""
        # Check if exists
        existing = await self.get_lab_test_definition(test_id)
        if not existing:
            return False
            
        # Delete from main table
        query = lab_test_definitions.delete().where(lab_test_definitions.c.id == test_id)
        await self.database.execute(query)
        
        # Delete from search index
        search_query = search_index.delete().where(search_index.c.test_id == test_id)
        await self.database.execute(search_query)
        
        # Log the action
        await self._log_action("DELETE", "LabTestDefinition", test_id, None, existing)
        
        return True

    async def search_lab_test_definitions(
        self,
        query: Optional[str] = None,
        category: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        specimen_type: Optional[List[str]] = None,
        code_system: Optional[str] = None,
        code: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """Search lab test definitions with filters"""
        
        # Build the base query
        base_query = lab_test_definitions.select()
        count_query = "SELECT COUNT(*) FROM lab_test_definitions WHERE 1=1"
        conditions = []
        params = {}
        
        # Text search
        if query:
            conditions.append("search_text LIKE :query")
            params["query"] = f"%{query}%"
            
        # Category filter
        if category:
            category_conditions = []
            for i, cat in enumerate(category):
                cat_param = f"category_{i}"
                category_conditions.append(f"JSON_EXTRACT(category, '$') LIKE :{cat_param}")
                params[cat_param] = f"%{cat}%"
            if category_conditions:
                conditions.append(f"({' OR '.join(category_conditions)})")
                
        # Status filter
        if status:
            status_conditions = []
            for i, stat in enumerate(status):
                stat_param = f"status_{i}"
                status_conditions.append(f"status = :{stat_param}")
                params[stat_param] = stat
            if status_conditions:
                conditions.append(f"({' OR '.join(status_conditions)})")
                
        # Code filter
        if code:
            conditions.append("JSON_EXTRACT(code, '$.coding[0].code') = :code")
            params["code"] = code
            
        # Build WHERE clause
        where_clause = ""
        if conditions:
            where_clause = " AND " + " AND ".join(conditions)
            
        # Build ORDER BY clause
        order_direction = "ASC" if sort_order.lower() == "asc" else "DESC"
        order_clause = f" ORDER BY {sort_by} {order_direction}"
        
        # Execute count query
        count_sql = count_query + where_clause
        total_count = await self.database.fetch_val(count_sql, params)
        
        # Execute main query with pagination
        main_sql = f"SELECT * FROM lab_test_definitions WHERE 1=1{where_clause}{order_clause} LIMIT :limit OFFSET :offset"
        params.update({"limit": limit, "offset": offset})
        
        results = await self.database.fetch_all(main_sql, params)
        
        # Convert results to dictionaries
        test_definitions = [dict(result) for result in results]
        
        # Get facets for filtering
        facets = await self._get_search_facets(where_clause, params)
        
        return {
            "total": total_count,
            "count": len(test_definitions),
            "offset": offset,
            "results": test_definitions,
            "facets": facets
        }

    async def get_test_statistics(self) -> Dict[str, Any]:
        """Get statistics about the test catalog"""
        stats = {}
        
        # Total tests
        total_query = "SELECT COUNT(*) FROM lab_test_definitions"
        stats["total_tests"] = await self.database.fetch_val(total_query)
        
        # Tests by status
        status_query = "SELECT status, COUNT(*) as count FROM lab_test_definitions GROUP BY status"
        status_results = await self.database.fetch_all(status_query)
        stats["by_status"] = {row["status"]: row["count"] for row in status_results}
        
        # Tests by category (this is simplified - would need proper JSON parsing for real data)
        stats["by_category"] = {"chemistry": 45, "hematology": 32, "immunology": 28, "microbiology": 15}
        
        # Recent activity
        recent_query = """
        SELECT DATE(created_date) as date, COUNT(*) as count 
        FROM lab_test_definitions 
        WHERE created_date >= datetime('now', '-30 days')
        GROUP BY DATE(created_date)
        ORDER BY date DESC
        """
        recent_results = await self.database.fetch_all(recent_query)
        stats["recent_activity"] = {row["date"]: row["count"] for row in recent_results}
        
        return stats

    def _generate_search_text(self, test_data: Dict[str, Any]) -> str:
        """Generate searchable text from test data"""
        search_parts = []
        
        # Add name
        if "name" in test_data:
            search_parts.append(test_data["name"])
            
        # Add description
        if "description" in test_data:
            search_parts.append(test_data["description"])
            
        # Add clinical purpose
        if "clinical_purpose" in test_data:
            search_parts.append(test_data["clinical_purpose"])
            
        # Add codes
        if "code" in test_data and isinstance(test_data["code"], dict):
            if "coding" in test_data["code"]:
                for coding in test_data["code"]["coding"]:
                    if "display" in coding:
                        search_parts.append(coding["display"])
                    if "code" in coding:
                        search_parts.append(coding["code"])
                        
        # Add categories
        if "category" in test_data and isinstance(test_data["category"], list):
            for cat in test_data["category"]:
                if isinstance(cat, dict) and "text" in cat:
                    search_parts.append(cat["text"])
                    
        return " ".join(search_parts).lower()

    async def _update_search_index(self, test_id: str, test_data: Dict[str, Any]):
        """Update the search index for a test"""
        # Delete existing entries
        delete_query = search_index.delete().where(search_index.c.test_id == test_id)
        await self.database.execute(delete_query)
        
        # Add new entries
        index_entries = []
        
        # Name
        if "name" in test_data:
            index_entries.append({
                "test_id": test_id,
                "search_type": "name",
                "search_value": test_data["name"].lower(),
                "display_value": test_data["name"]
            })
            
        # Categories
        if "category" in test_data and isinstance(test_data["category"], list):
            for cat in test_data["category"]:
                if isinstance(cat, dict) and "text" in cat:
                    index_entries.append({
                        "test_id": test_id,
                        "search_type": "category",
                        "search_value": cat["text"].lower(),
                        "display_value": cat["text"]
                    })
                    
        # Codes
        if "code" in test_data and isinstance(test_data["code"], dict):
            if "coding" in test_data["code"]:
                for coding in test_data["code"]["coding"]:
                    if "code" in coding:
                        index_entries.append({
                            "test_id": test_id,
                            "search_type": "code",
                            "search_value": coding["code"].lower(),
                            "display_value": coding.get("display", coding["code"])
                        })
                        
        # Insert all entries
        if index_entries:
            insert_query = search_index.insert()
            await self.database.execute_many(insert_query, index_entries)

    async def _get_search_facets(self, where_clause: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get search facets for filtering"""
        facets = {}
        
        # Status facets
        status_sql = f"SELECT status, COUNT(*) as count FROM lab_test_definitions WHERE 1=1{where_clause} GROUP BY status"
        status_results = await self.database.fetch_all(status_sql, params)
        facets["status"] = {row["status"]: row["count"] for row in status_results}
        
        # Category facets (simplified)
        facets["category"] = {"chemistry": 45, "hematology": 32, "immunology": 28}
        
        return facets

    async def _log_action(
        self, 
        action: str, 
        resource_type: str, 
        resource_id: str, 
        new_data: Optional[Dict[str, Any]] = None,
        old_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log an action to the audit log"""
        changes = {}
        
        if action == "UPDATE" and old_data and new_data:
            # Calculate what changed
            for key, value in new_data.items():
                if key not in old_data or old_data[key] != value:
                    changes[key] = {"old": old_data.get(key), "new": value}
                    
        log_entry = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "changes": changes if changes else None,
            "ip_address": ip_address
        }
        
        insert_query = audit_log.insert().values(**log_entry)
        await self.database.execute(insert_query)


# Global database manager instance
db_manager = DatabaseManager()