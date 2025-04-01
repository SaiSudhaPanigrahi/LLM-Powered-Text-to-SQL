import json
from typing import Dict, List


def load_parsed_schema(tables_path: str) -> Dict[str, Dict]:
    with open(tables_path, "r") as f:
        raw = json.load(f)

    db_schemas = {}
    for db in raw:
        db_id = db["db_id"]
        tables = db["table_names_original"]
        columns = db["column_names_original"]
        column_types = db["column_types"]
        foreign_keys = db["foreign_keys"]

        table_columns = {table: [] for table in tables}
        table_column_types = {table: [] for table in tables}

        for (table_idx, column_name), col_type in zip(columns, column_types):
            if column_name == "*":
                continue
            table = tables[table_idx]
            table_columns[table].append(column_name)
            table_column_types[table].append((column_name, col_type))

        fk_relations = []
        for col1, col2 in foreign_keys:
            t1, c1 = columns[col1]
            t2, c2 = columns[col2]
            fk_relations.append({
                "from": f"{tables[t1]}.{c1}",
                "to": f"{tables[t2]}.{c2}"
            })

        db_schemas[db_id] = {
            "tables": tables,
            "table_columns": table_columns,
            "column_types": table_column_types,
            "foreign_keys": fk_relations,
        }

    return db_schemas