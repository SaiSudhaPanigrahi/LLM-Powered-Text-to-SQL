# utils/prompt_formatter.py

from typing import Dict

def format_schema_prompt(db_schema: Dict) -> str:
    """
    Convert parsed schema dict into a structured text prompt for SQL generation.
    This includes table names, columns with types, and foreign key relationships.
    """

    lines = []

    # Add table and column type information
    for table in db_schema["tables"]:
        lines.append(f"Table: {table}")
        columns = db_schema["column_types"].get(table, [])
        for column_name, column_type in columns:
            lines.append(f"  - {column_name} ({column_type})")

    # Add foreign key relationships if present
    if db_schema.get("foreign_keys"):
        lines.append("\nForeign Key Relationships:")
        for fk in db_schema["foreign_keys"]:
            from_key = fk["from"]
            to_key = fk["to"]
            lines.append(f"  - {from_key} → {to_key}")

    return "\n".join(lines)