from db_connection import create_connection, close_connection

def save_donation(user_id, amount, message=None):
    """
    Save a donation to the database.

    Parameters:
        user_id (int): ID of the user making the donation.
        amount (float): Amount of the donation.
        message (str, optional): Optional message from the donor.
    """
    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO Donations (user_id, amount, message)
            VALUES (%s, %s, %s)
        """, (user_id, amount, message))
        connection.commit()
    except Exception as e:
        print(f"Error saving donation: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)
