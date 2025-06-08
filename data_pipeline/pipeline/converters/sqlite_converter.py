import sqlite3
import os
from typing import List, Dict, Any, Optional, Type, Union
from pathlib import Path
import logging
from data_pipeline.pipeline.converters.base_converter import BaseConverter


class SQLiteConverter(BaseConverter[str]):
    """Converter that creates and populates SQLite database from tabular data"""
    
    def __init__(self, 
                 db_path: str,
                 table_name: str = "data",
                 overwrite: bool = False,
                 batch_size: int = 1000,
                 auto_create_schema: bool = True,
                 primary_key_field: Optional[str] = None):
        """
        Initialize SQLite converter
        
        Args:
            db_path: Path to SQLite database file
            table_name: Name of the table to create/populate
            overwrite: Whether to overwrite existing table
            batch_size: Number of records to insert in each batch
            auto_create_schema: Whether to automatically create table schema
            primary_key_field: Field to use as primary key (auto-detected if None)
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.overwrite = overwrite
        self.batch_size = batch_size
        self.auto_create_schema = auto_create_schema
        self.primary_key_field = primary_key_field
        self._schema = None
        self._connection = None
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def convert(self, data: List[Dict[str, Any]], **kwargs) -> List[str]:
        """
        Convert tabular data to SQLite database
        
        Returns:
            List containing the database path as a string
        """
        if not data:
            logging.warning("No data provided to convert")
            return [str(self.db_path)]
        
        self.overwrite = kwargs.get('overwrite', self.overwrite)
        self.batch_size = kwargs.get('batch_size', self.batch_size)
        self.auto_create_schema = kwargs.get('auto_create_schema', self.auto_create_schema)
        self.primary_key_field = kwargs.get('primary_key_field', self.primary_key_field)
        
        try:
            # Connect to database
            self._connect()
            
            # Analyze data structure if auto-creating schema
            if self.auto_create_schema:
                self._schema = self._analyze_data_structure(data)
                self._create_table()
            
            # Insert data
            self._insert_data(data)
            
            # Close connection
            self._disconnect()
            
            logging.info(f"Successfully created SQLite database: {self.db_path}")
            logging.info(f"Inserted {len(data)} records into table '{self.table_name}'")
            
            return [str(self.db_path), f"Table '{self.table_name}' created with schema: {self._schema}"]
            
        except Exception as e:
            logging.error(f"Failed to create SQLite database: {e}")
            if self._connection:
                self._disconnect()
            raise
    
    def _connect(self) -> None:
        """Establish database connection"""
        self._connection = sqlite3.connect(self.db_path)
        self._connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    
    def _disconnect(self) -> None:
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def _analyze_data_structure(self, data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze data to determine SQLite column types"""
        schema = {}
        sample_size = min(100, len(data))
        
        # Get all unique column names
        all_columns = set()
        for row in data[:sample_size]:
            all_columns.update(row.keys())
        
        for column in all_columns:
            # Collect sample values for this column
            values = []
            for row in data[:sample_size]:
                if column in row and row[column] is not None and row[column] != '':
                    values.append(row[column])
            
            # Determine SQLite type
            sqlite_type = self._infer_sqlite_type(values)
            schema[column] = sqlite_type
        
        return schema
    
    def _infer_sqlite_type(self, values: List[Any]) -> str:
        """Infer SQLite column type from sample values"""
        if not values:
            return "TEXT"
        
        # Count types in samples
        type_counts = {"INTEGER": 0, "REAL": 0, "TEXT": 0, "BLOB": 0}
        
        for value in values:
            if isinstance(value, bool):
                type_counts["INTEGER"] += 1  # SQLite stores bools as integers
            elif isinstance(value, int):
                type_counts["INTEGER"] += 1
            elif isinstance(value, float):
                type_counts["REAL"] += 1
            elif isinstance(value, (str, list, dict)):
                # Check if string represents a number
                if isinstance(value, str):
                    stripped = value.strip()
                    if self._is_integer_string(stripped):
                        type_counts["INTEGER"] += 1
                    elif self._is_float_string(stripped):
                        type_counts["REAL"] += 1
                    else:
                        type_counts["TEXT"] += 1
                else:
                    type_counts["TEXT"] += 1  # Lists/dicts stored as TEXT (JSON)
            elif isinstance(value, bytes):
                type_counts["BLOB"] += 1
            else:
                type_counts["TEXT"] += 1
        
        # Return most common type, with preference for more specific types
        total_values = sum(type_counts.values())
        if total_values == 0:
            return "TEXT"
        
        # Calculate percentages
        percentages = {t: count/total_values for t, count in type_counts.items()}
        
        # If 80%+ are integers, use INTEGER
        if percentages["INTEGER"] >= 0.8:
            return "INTEGER"
        # If 80%+ are numbers (int or float), use REAL
        elif percentages["INTEGER"] + percentages["REAL"] >= 0.8:
            return "REAL"
        # If significant BLOB data, use BLOB
        elif percentages["BLOB"] >= 0.5:
            return "BLOB"
        # Default to TEXT
        else:
            return "TEXT"
    
    def _is_integer_string(self, value: str) -> bool:
        """Check if string represents an integer"""
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def _is_float_string(self, value: str) -> bool:
        """Check if string represents a float"""
        try:
            float(value)
            return '.' in value or 'e' in value.lower()
        except ValueError:
            return False
    
    def _create_table(self) -> None:
        """Create table with inferred schema"""
        if not self._schema:
            raise ValueError("No schema available for table creation")
        
        # Drop table if overwriting
        if self.overwrite:
            self._connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        
        # Determine primary key
        pk_field = self._determine_primary_key()
        
        # Build CREATE TABLE statement
        columns = []
        for column_name, column_type in self._schema.items():
            clean_name = self._clean_column_name(column_name)
            
            # Add primary key constraint if this is the PK field
            if pk_field and clean_name == self._clean_column_name(pk_field):
                if column_type == "INTEGER":
                    columns.append(f"{clean_name} {column_type} PRIMARY KEY AUTOINCREMENT")
                else:
                    columns.append(f"{clean_name} {column_type} PRIMARY KEY")
            else:
                columns.append(f"{clean_name} {column_type}")
        
        # Create table
        create_sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(columns)})"
        
        logging.info(f"Creating table with SQL: {create_sql}")
        self._connection.execute(create_sql)
        self._connection.commit()
    
    def _determine_primary_key(self) -> Optional[str]:
        """Determine which field should be the primary key"""
        if self.primary_key_field:
            return self.primary_key_field
        
        # Look for common ID field patterns
        id_patterns = ['id', 'identifier', 'key', 'pk', 'primary_key', 'uid', 'uuid']
        
        for column in self._schema.keys():
            if column.lower().strip() in id_patterns:
                return column
        
        return None
    
    def _clean_column_name(self, name: str) -> str:
        """Clean column name for SQLite compatibility"""
        import re
        # Replace spaces and special chars with underscores
        clean = re.sub(r'[^\w]', '_', str(name))
        # Remove consecutive underscores
        clean = re.sub(r'_+', '_', clean)
        # Remove leading/trailing underscores
        clean = clean.strip('_')
        # Ensure it doesn't start with a number
        if clean and clean[0].isdigit():
            clean = f"col_{clean}"
        # Handle reserved SQLite keywords
        reserved_words = ['order', 'group', 'where', 'select', 'insert', 'update', 'delete', 'from', 'table']
        if clean.lower() in reserved_words:
            clean = f"{clean}_field"
        
        return clean or "unknown_column"
    
    def _insert_data(self, data: List[Dict[str, Any]]) -> None:
        """Insert data into the table in batches"""
        if not data:
            return
        
        # Prepare column mapping (original -> clean names)
        column_mapping = {
            col: self._clean_column_name(col) 
            for col in self._schema.keys()
        }
        
        clean_columns = list(column_mapping.values())
        placeholders = ', '.join(['?' for _ in clean_columns])
        
        insert_sql = f"INSERT INTO {self.table_name} ({', '.join(clean_columns)}) VALUES ({placeholders})"
        
        # Process data in batches
        batch = []
        for i, row in enumerate(data):
            # Convert row to match clean column names and handle data types
            clean_row = []
            for original_col, clean_col in column_mapping.items():
                value = row.get(original_col)
                converted_value = self._convert_value_for_sqlite(value, self._schema[original_col])
                clean_row.append(converted_value)
            
            batch.append(clean_row)
            
            # Insert batch when it reaches batch_size or at the end
            if len(batch) >= self.batch_size or i == len(data) - 1:
                self._connection.executemany(insert_sql, batch)
                self._connection.commit()
                logging.debug(f"Inserted batch of {len(batch)} records")
                batch = []
    
    def _convert_value_for_sqlite(self, value: Any, column_type: str) -> Any:
        """Convert value to appropriate SQLite type"""
        if value is None or value == '':
            return None
        
        try:
            if column_type == "INTEGER":
                if isinstance(value, bool):
                    return int(value)
                elif isinstance(value, str):
                    return int(float(value.strip()))  # Handle "123.0" -> 123
                else:
                    return int(value)
            
            elif column_type == "REAL":
                return float(value)
            
            elif column_type == "TEXT":
                if isinstance(value, (list, dict)):
                    import json
                    return json.dumps(value)  # Store complex types as JSON
                else:
                    return str(value)
            
            elif column_type == "BLOB":
                if isinstance(value, bytes):
                    return value
                else:
                    return str(value).encode('utf-8')
            
            else:
                return str(value)
                
        except (ValueError, TypeError) as e:
            logging.warning(f"Failed to convert value {value} to {column_type}: {e}")
            return str(value) if value is not None else None
    
    def get_target_type(self) -> Type[str]:
        """Return the target type (database path as string)"""
        return str
    
    def suggest_field_mapping(self, available_columns: List[str]) -> Dict[str, str]:
        """Return mapping from clean column names to original column names"""
        return {
            self._clean_column_name(col): col 
            for col in available_columns
        }
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get information about the created table"""
        if not self.db_path.exists():
            return {"error": "Database file does not exist"}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            row_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "database_path": str(self.db_path),
                "table_name": self.table_name,
                "columns": [{"name": col[1], "type": col[2], "nullable": not col[3], "primary_key": bool(col[5])} for col in columns],
                "row_count": row_count,
                "file_size_bytes": self.db_path.stat().st_size
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file does not exist: {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            # Convert sqlite3.Row objects to dictionaries
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_available_configs(self) -> Dict[str, Any]:
        """Return available configuration options for this converter"""
        return {
            "overwrite": "True or False, whether to overwrite existing table",
            "batch_size": "Number of records to insert in each batch",
            "auto_create_schema": "True or False, whether to automatically create table schema based on data",
            "primary_key_field": "Field to use as primary key (auto-detected if None)",
        }