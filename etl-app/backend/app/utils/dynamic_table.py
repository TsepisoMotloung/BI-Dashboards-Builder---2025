from sqlalchemy import Table, Column, Integer, String, Float, Boolean, DateTime, Text, MetaData, Index
from sqlalchemy.sql import text
from typing import Dict, Any, List
from app.core.database import engine
import json
from sqlalchemy import inspect
from typing import Optional


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
    def insert_data_batch_with_upload(table_name: str, data: List[Dict[str, Any]], upload_id: Optional[int] = None) -> int:
        """Insert batch of data into table and tag rows with upload_id if provided"""
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        if upload_id is not None:
            # ensure upload_id column exists
            DynamicTableManager.ensure_upload_id_column(table_name)
            for row in data:
                row['upload_id'] = upload_id

        with engine.begin() as conn:
            result = conn.execute(table.insert(), data)
            return result.rowcount

    @staticmethod
    def get_table_columns(table_name: str) -> List[str]:
        """Return list of column names for a table"""
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            return []
        cols = inspector.get_columns(table_name)
        return [c['name'] for c in cols]

    @staticmethod
    def ensure_upload_id_column(table_name: str) -> None:
        """Ensure the dynamic table has an `upload_id` integer column for tagging inserts."""
        cols = DynamicTableManager.get_table_columns(table_name)
        if 'upload_id' in cols:
            return
        # add column
        sql = text(f"ALTER TABLE `{table_name}` ADD COLUMN upload_id INTEGER NULL")
        with engine.begin() as conn:
            conn.execute(sql)
            # add index
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_upload_id ON `{table_name}` (upload_id)"))

    @staticmethod
    def add_missing_columns(table_name: str, columns: Dict[str, str]) -> List[str]:
        """Add missing columns to an existing table.
        `columns` is a mapping column_name -> simple_type (string, integer, float, boolean, datetime, text)
        Returns list of actually added columns.
        """
        added = []
        existing = set(DynamicTableManager.get_table_columns(table_name))
        type_map_sql = {
            'string': 'VARCHAR(255)',
            'integer': 'INTEGER',
            'float': 'FLOAT',
            'boolean': 'BOOLEAN',
            'date': 'DATETIME',
            'datetime': 'DATETIME',
            'text': 'TEXT',
        }

        with engine.begin() as conn:
            for col_name, col_type in columns.items():
                if col_name in existing:
                    continue
                sql_type = type_map_sql.get(col_type, 'VARCHAR(255)')
                sql = text(f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {sql_type} NULL")
                conn.execute(sql)
                added.append(col_name)

        return added

    @staticmethod
    def drop_columns(table_name: str, columns: List[str]) -> List[str]:
        """Drop columns from an existing table. Returns list of actually dropped columns."""
        dropped = []
        existing = set(DynamicTableManager.get_table_columns(table_name))
        with engine.begin() as conn:
            for col in columns:
                if col not in existing:
                    continue
                # Drop column (note: some DBs may restrict dropping if constraints exist)
                sql = text(f"ALTER TABLE `{table_name}` DROP COLUMN `{col}`")
                conn.execute(sql)
                dropped.append(col)

        return dropped
    
    @staticmethod
    def delete_data_by_upload(table_name: str, upload_id: int) -> int:
        """Delete data inserted by specific upload (requires upload_id column)"""
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        # ensure upload_id exists
        cols = DynamicTableManager.get_table_columns(table_name)
        if 'upload_id' not in cols:
            # nothing to delete scoped to upload
            return 0

        with engine.begin() as conn:
            stmt = table.delete().where(table.c.upload_id == upload_id)
            result = conn.execute(stmt)
            return result.rowcount
