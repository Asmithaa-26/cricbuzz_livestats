import sqlite3
import pandas as pd

# Path to your local SQLite database file
SQLITE_DB_PATH = "cricbuzz_db.db"

def create_connection(autocommit=True):
    """
    Create a new SQLite connection. 
    Uses autocommit (isolation_level=None) for lightweight reads,
    but retains standard transaction tracking for write/mutation sequences.
    """
    if autocommit:
        return sqlite3.connect(SQLITE_DB_PATH, isolation_level=None)
    return sqlite3.connect(SQLITE_DB_PATH)

def get_sqlite_schema():
    """
    Returns a nested dict of available tables, views, and columns from the SQLite database.
    Fully compliant with the frontend dictionary expectations.
    """
    conn = create_connection(autocommit=True)
    cursor = conn.cursor()
    
    full_schema_info = {
        "cricbuzz_db": {
            "tables": {},
            "views": {},
            "functions": {},
            "procedures": {}
        }
    }
    
    db_structure = full_schema_info["cricbuzz_db"]
    
    try:
        # Fetch all User Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        for tbl in tables:
            cursor.execute(f"PRAGMA table_info('{tbl}');")
            cols = cursor.fetchall()
            
            # Fix: Checking c[5] > 0 ensures composite primary keys aren't dropped/ignored
            db_structure["tables"][tbl] = [
                {
                    "name": c[1],                               # Column name
                    "type": c[2],                               # Data type
                    "nullable": "NO" if c[3] == 1 else "YES",   # Is Nullable
                    "key": "PRI" if c[5] > 0 else "",           # Primary key identifier (Fixed)
                    "default": c[4],                            # Default value
                    "extra": "",                                
                }
                for c in cols
            ]
            
        # Fetch all User Views
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
        views = [row[0] for row in cursor.fetchall()]
        for v in views:
            db_structure["views"][v] = {}
            
    except Exception as e:
        print(f"Error accessing SQLite Schema: {e}")
    finally:
        cursor.close()
        conn.close()
        
    return full_schema_info

def fetch_table(table, limit=200):
    """Safely streams a target table into a dataframe."""
    conn = create_connection(autocommit=True)
    sql = f'SELECT * FROM "{table}" LIMIT {int(limit)};'
    df = pd.read_sql(sql, conn)
    conn.close()
    return df, sql

def run_select(select_sql):
    """Executes read-only analytical statements."""
    if not select_sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed here.")
    conn = create_connection(autocommit=True)
    df = pd.read_sql(select_sql, conn)
    conn.close()
    return df

def insert_row(table, data):
    """Inserts a row within a secure transaction block using placeholders."""
    cols = [f'"{c}"' for c in data.keys()]
    placeholders = ", ".join(["?"] * len(cols))
    sql = f'INSERT INTO "{table}" ({", ".join(cols)}) VALUES ({placeholders});'
    values = list(data.values())

    # Open transaction connection context (autocommit=False)
    conn = create_connection(autocommit=False)
    try:
        with conn: # Enforces automatic COMMIT on success and ROLLBACK on failure
            cur = conn.cursor()
            cur.execute(sql, values)
            affected = cur.rowcount
    finally:
        conn.close()
    return affected, sql

def delete_rows(table, where_clause):
    """Deletes records ensuring a WHERE filter is present."""
    where = where_clause.strip()
    if not where:
        raise ValueError("Refusing to delete without a WHERE clause.")
    sql = f'DELETE FROM "{table}" WHERE {where};'
    
    conn = create_connection(autocommit=False)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(sql)
            affected = cur.rowcount
    finally:
        conn.close()
    return affected, sql

def execute_update(table, set_clause, where_clause):
    """Updates table records dynamically inside a safe transaction scope."""
    set_part = set_clause.strip()
    where_part = where_clause.strip()
    if not set_part:
        raise ValueError("SET clause cannot be empty.")
    if not where_part:
        raise ValueError("Refusing to update without a WHERE clause.")
    sql = f'UPDATE "{table}" SET {set_part} WHERE {where_part};'
    
    conn = create_connection(autocommit=False)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(sql)
            affected = cur.rowcount
    finally:
        conn.close()
    return affected, sql