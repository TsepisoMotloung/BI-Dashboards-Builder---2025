from sqlalchemy import Table, Column, Integer, String, Float, Boolean, DateTime, Text, MetaData, Index
from sqlalchemy.sql import text
from typing import Dict, Any, List
from app.core.database import engine
import json


class DynamicTableManager:
    """Manage dynamic table creation and data insertion"""
    
    @staticmethod
    def create_table_from_schema(table_name: str, schema: Dict[str, Any]) -> Table:
        """Create SQLAlchemy Table object from schema definition"""
        metadata = MetaData()
        
        # Type mapping
        type_map = {
            'string': String(255),
            'integer': Integer,
            'float': Float,
            'boolean': Boolean,
            'date': DateTime,
            'datetime': DateTime,
            'text': Text,
        }
        
        columns = [Column('id', Integer, primary_key=True, autoincrement=True)]
        
        # Add fields from schema
        for field in schema.get('fields', []):
            field_name = field['name']
            field_type = field['type']
            
            col_type = type_map.get(field_type, String(255))
            
            # Handle max_length for strings
            if field_type == 'string' and field.get('max_length'):
                col_type = String(field['max_length'])
            
            col = Column(
                field_name,
                col_type,
                nullable=not field.get('required', False),
                unique=field.get('unique', False),
                default=field.get('default')
            )
            columns.append(col)
        
        # Add timestamps
        columns.append(Column('created_at', DateTime, server_default=text('CURRENT_TIMESTAMP')))
        columns.append(Column('updated_at', DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))
        
        table = Table(table_name, metadata, *columns)
        
        # Create indexes
        for index_field in schema.get('indexes', []):
            Index(f'idx_{table_name}_{index_field}', table.c[index_field])
        
        return table
    
    @staticmethod
    def create_physical_table(table_name: str, schema: Dict[str, Any]) -> None:
        """Create actual table in database"""
        table = DynamicTableManager.create_table_from_schema(table_name, schema)
        table.create(engine, checkfirst=True)
    
    @staticmethod
    def drop_table(table_name: str) -> None:
        """Drop table from database"""
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        table.drop(engine)
    
    @staticmethod
    def table_exists(table_name: str) -> bool:
        """Check if table exists"""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    
    @staticmethod
    def insert_data_batch(table_name: str, data: List[Dict[str, Any]]) -> int:
        """Insert batch of data into table"""
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        
        with engine.begin() as conn:
            result = conn.execute(table.insert(), data)
            return result.rowcount
    
    @staticmethod
    def delete_data_by_upload(table_name: str, upload_id: int) -> int:
        """Delete data inserted by specific upload (requires upload_id column)"""
        # This would require adding upload_id to each dynamic table
        # For now, we'll implement a simpler version
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        
        # For rollback, we could use timestamp-based deletion
        # or add an upload_id column to all dynamic tables
        with engine.begin() as conn:
            result = conn.execute(table.delete())
            return result.rowcount
