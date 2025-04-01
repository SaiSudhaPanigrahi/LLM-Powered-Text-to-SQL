# fine_grained_schema.py

import json


def get_fine_grained_schema(schema_obj):
    """
    Converts a Spider table schema (one entry from tables.json) into a rich text format with:
    - Table-wise columns
    - Column types
    - Foreign key relationships
    """
    table_names = schema_obj["table_names_original"]
    column_names = schema_obj["column_names_original"]
    column_types = schema_obj["column_types"]
    foreign_keys = schema_obj.get("foreign_keys", [])

    table_columns = {name: [] for name in table_names}
    for (table_idx, col_name), col_type in zip(column_names, column_types):
        if col_name != "*" and table_idx >= 0:
            table_columns[table_names[table_idx]].append((col_name, col_type))

    fk_texts = []
    for source_idx, dest_idx in foreign_keys:
        src_tbl_idx, src_col = column_names[source_idx]
        dest_tbl_idx, dest_col = column_names[dest_idx]
        if src_tbl_idx == -1 or dest_tbl_idx == -1:
            continue
        src_tbl = table_names[src_tbl_idx]
        dest_tbl = table_names[dest_tbl_idx]
        fk_texts.append(f"Foreign key: {src_tbl}.{src_col} → {dest_tbl}.{dest_col}")

    lines = []
    for table, cols in table_columns.items():
        col_str = ", ".join([f"{name} ({col_type})" for name, col_type in cols])
        lines.append(f"Table {table}: {col_str}")

    if fk_texts:
        lines.append("\n" + "\n".join(fk_texts))

    return "\n".join(lines)
