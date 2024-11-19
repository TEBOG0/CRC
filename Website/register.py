import db_connection
import hashlib

def register_user(full_name, email, password, phone_number=None):
    connection = db_connection.create_connection()
    cursor = connection.cursor()
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        query = """INSERT INTO Users (full_name, email, password, phone_number)
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (full_name, email, hashed_password, phone_number))
        connection.commit()
        print("User registered successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_connection.close_connection(connection)
