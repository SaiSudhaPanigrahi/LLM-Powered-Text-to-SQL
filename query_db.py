import sqlite3

def main():
    # Path to your SQLite database file
    db_path = "/Users/vatsalvatsyayan/Class/NLP/database/allInOne/final.sqlite"

    # Connect to the SQLite database (it will create a connection object)
    try:
        conn = sqlite3.connect(db_path)
        print(f"Connected to database at {db_path}")
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
        return

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Define your SQL query (adjust table name and query as needed)
    query = "SELECT * FROM farm LIMIT 10;"

    try:
        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Print out the results
        print("Query Results:")
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print("Error executing query:", e)
    finally:
        # Clean up: close the cursor and connection
        cursor.close()
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()