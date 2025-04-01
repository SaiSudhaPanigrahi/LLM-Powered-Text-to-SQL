# utils/sql_postchecker.py

import sqlparse
from sqlparse.sql import IdentifierList, Identifier, TokenList, Function
from sqlparse.tokens import Keyword, DML
from typing import Dict, Set


def extract_identifiers(token_list) -> Set[str]:
    """
    Recursively extract identifiers (table/column names) from SQL tokens,
    including those wrapped in functions or expressions.
    """
    identifiers = set()
    for token in token_list.tokens:
        if token.is_group:
            identifiers |= extract_identifiers(token)
        elif isinstance(token, Identifier):
            real_name = token.get_real_name()
            if real_name:
                identifiers.add(real_name.lower())
        elif isinstance(token, Function):
            # Handle function like MAX(column) or COUNT(*)
            inner_tokens = token.get_parameters()
            for param in inner_tokens:
                if isinstance(param, Identifier):
                    identifiers.add(param.get_real_name().lower())
        elif token.ttype is Keyword or token.ttype is DML:
            continue
        elif token.ttype is None and isinstance(token, TokenList):
            identifiers |= extract_identifiers(token)
    return identifiers


def get_tables_and_columns_from_sql(sql: str):
    """
    Use sqlparse to extract tables and columns from a SQL query.
    """
    tables = set()
    columns = set()

    parsed = sqlparse.parse(sql)
    if not parsed:
        return tables, columns

    statement = parsed[0]

    from_seen = False
    for token in statement.tokens:
        if token.is_group:
            columns |= extract_identifiers(token)

        if token.ttype is Keyword and token.normalized == "FROM":
            from_seen = True
        elif from_seen and isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                tables.add(identifier.get_real_name().lower())
            from_seen = False
        elif from_seen and isinstance(token, Identifier):
            tables.add(token.get_real_name().lower())
            from_seen = False

    return tables, columns


def validate_sql_against_schema(sql: str, db_schema: Dict) -> bool:
    """
    Validates that all tables and columns used in SQL exist in the schema.
    """
    tables_in_sql, columns_in_sql = get_tables_and_columns_from_sql(sql)

    schema_tables = set(table.lower() for table in db_schema["tables"])
    schema_columns = set()
    for cols in db_schema["table_columns"].values():
        for col in cols:
            schema_columns.add(col.lower())

    tables_valid = tables_in_sql.issubset(schema_tables)
    columns_valid = columns_in_sql.issubset(schema_columns)

    if not tables_valid:
        print(f"❌ Invalid tables used: {tables_in_sql - schema_tables}")
    if not columns_valid:
        print(f"❌ Invalid columns used: {columns_in_sql - schema_columns}")

    return tables_valid and columns_valid