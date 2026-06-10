"""
Database initialization and management script.

Usage:
    python scripts/init_db.py setup              # Create tables in current database
    python scripts/init_db.py health             # Check database connectivity
    python scripts/init_db.py reset              # Drop and recreate tables (WARNING: data loss!)
    python scripts/init_db.py export-schema      # Export database schema to SQL
"""

import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.review_store import (
    init_store, healthcheck, get_engine, 
    reviews_table, prediction_logs_table, metadata
)
from src.settings import get_settings
from sqlalchemy import text, inspect


def setup_database():
    """Initialize database tables."""
    print("\nInitializing database...")
    settings = get_settings()
    print(f"Database URL: {settings.database_url[:50]}...")
    
    try:
        init_store()
        print("✓ Database tables created successfully!")
        
        # Verify tables exist
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nCreated tables: {tables}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)


def check_health():
    """Check database connectivity."""
    print("\nChecking database health...")
    
    settings = get_settings()
    print(f"Database: {settings.database_url.split('://')[0]}")
    print(f"Backend label: ", end='')
    
    health = healthcheck()
    if health.get('ok'):
        print(f"✓ {health.get('backend')}")
        print("✓ Connection successful")
    else:
        print(f"✗ {health.get('backend')}")
        print(f"✗ Error: {health.get('error')}")
        sys.exit(1)


def reset_database():
    """Drop and recreate all tables (WARNING: DATA LOSS!)."""
    response = input("\n⚠️  WARNING: This will DELETE all reviews and prediction logs!\nType 'yes' to confirm: ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("\nResetting database...")
    settings = get_settings()
    
    try:
        engine = get_engine()
        
        # Drop all tables
        metadata.drop_all(engine)
        print("✓ Tables dropped")
        
        # Recreate tables
        metadata.create_all(engine)
        print("✓ Tables recreated")
        
        print("✓ Database reset complete")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        sys.exit(1)


def export_schema():
    """Export database schema to SQL file."""
    print("\nExporting database schema...")
    
    try:
        engine = get_engine()
        output_file = ROOT / 'reports' / 'database_schema.sql'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Get schema information
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        sql_commands = []
        
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            constraints = inspector.get_pk_constraint(table_name)
            
            col_defs = []
            for col in columns:
                col_type = str(col['type'])
                null_clause = 'NOT NULL' if not col['nullable'] else 'NULL'
                col_defs.append(f"  {col['name']} {col_type} {null_clause}")
            
            create_sql = f"CREATE TABLE {table_name} (\n"
            create_sql += ",\n".join(col_defs)
            create_sql += "\n);"
            
            sql_commands.append(create_sql)
        
        with open(output_file, 'w') as f:
            f.write("-- Database Schema Export\n")
            f.write(f"-- Generated from {type(engine).__name__}\n\n")
            f.write("\n\n".join(sql_commands))
        
        print(f"✓ Schema exported to {output_file}")
        
    except Exception as e:
        print(f"❌ Error exporting schema: {e}")
        sys.exit(1)


def show_table_counts():
    """Show row counts in each table."""
    print("\nTable Statistics:")
    print("-" * 50)
    
    try:
        engine = get_engine()
        
        for table_name in ['reviews', 'prediction_logs']:
            result = engine.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"{table_name:20} {count:>10} rows")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Database management utility.')
    parser.add_argument('command', choices=['setup', 'health', 'reset', 'export-schema', 'stats'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_database()
    elif args.command == 'health':
        check_health()
    elif args.command == 'reset':
        reset_database()
    elif args.command == 'export-schema':
        export_schema()
    elif args.command == 'stats':
        show_table_counts()


if __name__ == '__main__':
    main()
