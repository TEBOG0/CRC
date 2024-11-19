import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='crc_database',
	        port='3308'
        )
        if connection.is_connected():
            print("✅ Connected to 'crc_database' database")
            return connection
    except Error as e:
        print(f"❌ Connection Error: {e}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("🔒 MySQL connection closed")
