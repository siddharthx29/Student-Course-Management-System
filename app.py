# =============================================================================
# Student Course Management System
# Python DB-API Assignment - Using sqlite3
# Author : Siddharth Mv
# Roll No: 54
# =============================================================================

import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
# Secret key required for Flask flash (session-based) messages
app.secret_key = 'scms_secret_2026'

DATABASE = 'students.db'

# =============================================================================
# DATABASE HELPER: Get a DB connection (Python DB-API: sqlite3.connect)
# =============================================================================
def get_connection():
    """
    Establish and return a database connection using sqlite3.connect().
    This is the Python DB-API connection object.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row   # Allows column access by name
    return conn

# =============================================================================
# DATABASE INITIALISATION: Create table if it does not exist
# =============================================================================
def init_db():
    """
    Create the students table if it does not already exist.
    Uses try/except/finally for proper resource management.
    """
    conn = None
    cursor = None
    try:
        # DB-API: Establish connection
        conn = get_connection()
        # DB-API: Create cursor object
        cursor = conn.cursor()
        # DB-API: Execute SQL - CREATE TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                name   TEXT    NOT NULL,
                email  TEXT    NOT NULL UNIQUE,
                course TEXT    NOT NULL,
                age    INTEGER NOT NULL
            )
        ''')
        # DB-API: Commit the transaction
        conn.commit()
    except sqlite3.Error as e:
        print(f"[DB INIT ERROR] {e}")
    finally:
        # DB-API: Always close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# =============================================================================
# ROUTE: Home - READ operation (SELECT all students)
# =============================================================================
@app.route('/')
def index():
    """
    Home page: Reads all student records from the database.
    Demonstrates the READ (SELECT) DB-API operation.
    """
    conn = None
    cursor = None
    students = []
    try:
        # DB-API: Connection
        conn = get_connection()
        # DB-API: Cursor
        cursor = conn.cursor()
        # DB-API: Execute READ (SELECT) query
        cursor.execute('SELECT * FROM students ORDER BY id ASC')
        students = cursor.fetchall()
    except sqlite3.Error as e:
        flash(f'Database error: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template('index.html', students=students)

# =============================================================================
# ROUTE: Add Student - GET shows form, POST performs CREATE (INSERT)
# =============================================================================
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """
    Add Student page: Inserts a new student record.
    Demonstrates the CREATE (INSERT) DB-API operation with parameterized queries.
    Handles sqlite3.IntegrityError for duplicate email.
    """
    if request.method == 'POST':
        name   = request.form.get('name', '').strip()
        email  = request.form.get('email', '').strip()
        course = request.form.get('course', '').strip()
        age_str = request.form.get('age', '').strip()

        # --- Basic Validation ---
        errors = []
        if not name:
            errors.append('Name cannot be empty.')
        if not email:
            errors.append('Email cannot be empty.')
        if not course:
            errors.append('Course cannot be empty.')
        if not age_str:
            errors.append('Age cannot be empty.')
        else:
            try:
                age = int(age_str)
                if age <= 0 or age > 120:
                    errors.append('Age must be a valid positive integer.')
            except ValueError:
                errors.append('Age must be a valid integer.')
                age = None

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('add_student.html',
                                   name=name, email=email,
                                   course=course, age=age_str)

        conn = None
        cursor = None
        try:
            # DB-API: Connection
            conn = get_connection()
            # DB-API: Cursor
            cursor = conn.cursor()
            # DB-API: Parameterized INSERT query (? placeholders - safe, no SQL injection)
            cursor.execute(
                'INSERT INTO students (name, email, course, age) VALUES (?, ?, ?, ?)',
                (name, email, course, age)
            )
            # DB-API: Commit the transaction
            conn.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            # Handle duplicate email gracefully
            flash('Error: Email already exists. Please use a different email.', 'danger')
            return render_template('add_student.html',
                                   name=name, email=email,
                                   course=course, age=age_str)
        except sqlite3.Error as e:
            flash(f'Database error: {e}', 'danger')
            return render_template('add_student.html',
                                   name=name, email=email,
                                   course=course, age=age_str)
        finally:
            # DB-API: Close cursor and connection
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('add_student.html',
                           name='', email='', course='', age='')

# =============================================================================
# ROUTE: Edit Student - GET shows pre-filled form, POST performs UPDATE
# =============================================================================
@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """
    Edit Student page: Updates an existing student record.
    Demonstrates the UPDATE DB-API operation with parameterized queries.
    """
    if request.method == 'POST':
        name   = request.form.get('name', '').strip()
        email  = request.form.get('email', '').strip()
        course = request.form.get('course', '').strip()
        age_str = request.form.get('age', '').strip()

        # --- Basic Validation ---
        errors = []
        if not name:
            errors.append('Name cannot be empty.')
        if not email:
            errors.append('Email cannot be empty.')
        if not course:
            errors.append('Course cannot be empty.')
        if not age_str:
            errors.append('Age cannot be empty.')
        else:
            try:
                age = int(age_str)
                if age <= 0 or age > 120:
                    errors.append('Age must be a valid positive integer.')
            except ValueError:
                errors.append('Age must be a valid integer.')
                age = None

        if errors:
            for err in errors:
                flash(err, 'danger')
            # Re-fetch student to refill form
            conn2 = get_connection()
            cur2  = conn2.cursor()
            cur2.execute('SELECT * FROM students WHERE id = ?', (student_id,))
            student = cur2.fetchone()
            cur2.close()
            conn2.close()
            return render_template('edit_student.html', student=student)

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # DB-API: Parameterized UPDATE query
            cursor.execute(
                'UPDATE students SET name=?, email=?, course=?, age=? WHERE id=?',
                (name, email, course, age, student_id)
            )
            # DB-API: Commit transaction
            conn.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Error: Email already exists. Please use a different email.', 'danger')
        except sqlite3.Error as e:
            flash(f'Database error: {e}', 'danger')
        finally:
            # DB-API: Close resources
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # GET: Fetch the student record to pre-fill the form
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # DB-API: Parameterized SELECT for specific student
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        if student is None:
            flash('Student not found.', 'danger')
            return redirect(url_for('index'))
        return render_template('edit_student.html', student=student)
    except sqlite3.Error as e:
        flash(f'Database error: {e}', 'danger')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# =============================================================================
# ROUTE: Delete Student - DELETE operation
# =============================================================================
@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    """
    Delete a student record.
    Demonstrates the DELETE DB-API operation with parameterized queries.
    """
    conn = None
    cursor = None
    try:
        # DB-API: Connection
        conn = get_connection()
        # DB-API: Cursor
        cursor = conn.cursor()
        # DB-API: Parameterized DELETE query
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        # DB-API: Commit transaction
        conn.commit()
        flash('Student deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Database error: {e}', 'danger')
    finally:
        # DB-API: Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return redirect(url_for('index'))

# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == '__main__':
    init_db()           # Ensure database and table exist before starting
    app.run(debug=True)
