import random
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
from faker import Faker

# Configuration
DATABASE_URI = "postgresql://postgres:password@localhost:5432/consolidated_db"
ROWS_PER_TABLE = 10  # Adjust as needed

engine = create_engine(DATABASE_URI)
metadata = MetaData()
metadata.reflect(bind=engine)
sorted_tables = metadata.sorted_tables  # Parent tables first
fake = Faker()

# Dictionary to store inserted primary key values for each table
inserted_keys = {}

def generate_value(col):
    """Generate synthetic data based on the column type."""
    col_type = str(col.type).lower()
    if 'int' in col_type:
        return random.randint(1, 1000)
    elif 'char' in col_type or 'text' in col_type:
        if 'name' in col.name:
            return fake.name()
        elif 'email' in col.name:
            return fake.email()
        elif 'phone' in col.name:
            return fake.phone_number()
        else:
            return fake.word()
    elif 'date' in col_type:
        return fake.date_this_decade().isoformat()
    elif 'time' in col_type:
        return fake.time()
    elif 'bool' in col_type:
        return random.choice([True, False])
    elif 'float' in col_type or 'numeric' in col_type:
        return round(random.uniform(1, 1000), 2)
    else:
        return fake.word()

def generate_row(table, connection):
    """Generate a dictionary for a new row, handling foreign keys specially."""
    row = {}
    for col in table.columns:
        # Skip auto-increment primary key columns
        if col.autoincrement:
            continue

        # Check if this column is a foreign key
        if col.foreign_keys:
            fk_obj = list(col.foreign_keys)[0]
            ref_table = fk_obj.column.table.name
            valid_keys = inserted_keys.get(ref_table, [])
            if valid_keys:
                row[col.name] = random.choice(valid_keys)
            else:
                # If no keys exist in the parent, you might choose to insert NULL
                row[col.name] = None
        else:
            row[col.name] = generate_value(col)
    return row

def populate_table(table):
    print(f"Populating table {table.name}...")
    with engine.begin() as connection:
        for _ in range(ROWS_PER_TABLE):
            row = generate_row(table, connection)
            try:
                result = connection.execute(table.insert(), row)
                # If the table has a single auto-generated primary key, record it.
                pk_columns = list(table.primary_key.columns)
                if len(pk_columns) == 1:
                    pk_value = result.inserted_primary_key[0]
                    inserted_keys.setdefault(table.name, []).append(pk_value)
            except SQLAlchemyError as e:
                print(f"Error inserting into {table.name}: {e}")

def main():
    for table in sorted_tables:
        # Optionally, skip tables that already have data:
        with engine.connect() as connection:
            res = connection.execute(table.select().limit(1))
            if res.fetchone():
                print(f"Table {table.name} already has data; skipping.")
                continue
        populate_table(table)
    print("Data generation complete.")

if __name__ == "__main__":
    main()