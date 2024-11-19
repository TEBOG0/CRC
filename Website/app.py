from flask import Flask, render_template, request, redirect, flash, session, url_for
import os
from db_connection import create_connection
from db_connection import close_connection
from save_contact_message import save_contact_message
from donation_logic import save_donation
import hashlib

app = Flask(__name__)
app.secret_key = 'KeGan012'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to manage projects (Admin only)
@app.route('/admin/projects', methods=['GET'])
def manage_projects():
    if not session.get('is_admin'):
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('home'))

    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Fetch all projects from the database
        cursor.execute("SELECT * FROM Projects")
        projects = cursor.fetchall()

    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        projects = []

    finally:
        close_connection(connection)

    # Render the admin dashboard with the list of projects
    return render_template('admin_dashboard.html', projects=projects)


# Route to donations
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash("You need to log in to make a donation.", "danger")
            return redirect(url_for('login'))

        user_id = session['user_id']
        amount = request.form.get('donation-amount')
        message = request.form.get('donation-message', '')  # Optional message field

        try:
            save_donation(user_id, amount, message)
            flash("Thank you for your donation!", "success")
            return redirect(url_for('donate'))
        except Exception as e:
            flash("An error occurred while processing your donation. Please try again.", "danger")
            print(f"Error: {e}")

    return render_template('donate.html')


@app.route('/admin/projects/new', methods=['GET', 'POST'])
def create_project():
    if not session.get('is_admin'):
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        project_name = request.form['project_name']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']
        image_file = request.files['project_image']

        # Save uploaded image
        if image_file and image_file.filename != '':
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(image_path)
            image_relative_path = f"uploads/{image_file.filename}"
        else:
            image_relative_path = "uploads/placeholder.png"

        # Insert into database
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Projects (project_name, description, start_date, end_date, status, project_image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (project_name, description, start_date, end_date, status, image_relative_path))
        connection.commit()
        close_connection(connection)

        flash("Project added successfully!", "success")
        return redirect(url_for('manage_projects'))

    return render_template('create_project.html')


@app.route('/about_us')
def about_us():
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT project_name, description 
                FROM Projects 
                WHERE status = 'Completed' 
                ORDER BY end_date DESC 
                LIMIT 3
            """
            cursor.execute(query)
            projects = cursor.fetchall()
    finally:
        connection.close()

    return render_template('about_us.html', projects=projects)

# Route to view projects (Public)
@app.route('/projects')
def view_projects():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Projects")
    projects = cursor.fetchall()
    close_connection(connection)

    return render_template('projects.html', projects=projects)


# Route for account page
@app.route('/account')
def account():
    return render_template('Account.html')

# Registration route
@app.route('/register', methods=['POST'])
def register():
    full_name = request.form['full_name']
    email = request.form['email']
    password = request.form['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO Users (full_name, email, password) VALUES (%s, %s, %s)",
                       (full_name, email, hashed_password))
        conn.commit()
        flash("Registration successful!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect('/account')

# Login Route and check for Admin
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch user by email and hashed password
    cursor.execute("SELECT * FROM Users WHERE email=%s AND password=%s", (email, hashed_password))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        # Set session variables for the logged-in user
        session['user_id'] = user['user_id']
        session['full_name'] = user['full_name']
        session['is_admin'] = user['is_admin']

        flash(f"Welcome back, {user['full_name']}!", "success")

        # Redirect based on user role
        if user['is_admin']:
            return redirect(url_for('manage_projects'))  # Admin dashboard
        else:
            return redirect(url_for('home'))  # Regular user homepage
    else:
        flash("Invalid credentials. Please try again.", "danger")
        return redirect(url_for('account'))


# Route for home page
@app.route('/home')
def home():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('account'))
    return render_template('Home.html', user_name=session['full_name'])


# Route for logging out
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('account'))


# Route for contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        # Save the message to the database
        if save_contact_message(name, email, subject, message):
            flash("Thank you for reaching out! We'll get back to you shortly.", "success")
        else:
            flash("There was an error submitting your message. Please try again.", "danger")
        
        # Redirect to the contact page to show the flash message
        return redirect(url_for('contact'))
    
    return render_template('contact-us.html')

if __name__ == '__main__':
    app.run(debug=True)
