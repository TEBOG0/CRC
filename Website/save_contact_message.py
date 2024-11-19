from db_connection import create_connection, close_connection

def save_contact_message(name, email, subject, message):
    """
    Save contact form data to the 'ContactMessages' table.
    """
    connection = create_connection()
    if not connection:
        print("❌ Failed to connect to the database.")
        return False

    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO ContactMessages (full_name, email, subject, message)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, subject, message))
        connection.commit()
        print("✅ Contact message saved successfully.")
        return True
    except Exception as e:
        print(f"❌ Error saving contact message: {e}")
        return False
    finally:
        cursor.close()
        close_connection(connection)
