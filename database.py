
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load database settings from the .env file
load_dotenv()


def get_db_connection():
    """Connect to the Job Application Tracker database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "job_tracker")
    )


def test_connection():
    """Verify that Python can communicate with MySQL."""
    connection = None

    try:
        connection = get_db_connection()

        if connection.is_connected():
            print("Successfully connected to MySQL!")

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")

            print("Tables in job_tracker:")

            for table in cursor.fetchall():
                print("-", table[0])

            cursor.close()

    except Error as error:
        print("Database connection error:", error)

    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print("Connection closed.")


if __name__ == "__main__":
    test_connection()
