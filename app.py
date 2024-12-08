from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from model.admin import AdminModel
from utils.generate_session_cookie import generate_session_cookie
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
app.config['SESSION_COOKIE_NAME'] = generate_session_cookie()
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 
# initialize the MongoDB connection
admin_model = AdminModel()

@app.route('/')
def login_register():
    if 'username' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('login_register.html')



@app.route('/register', methods=['POST'])
def register():
    data = request.form.to_dict()
    if data['password'] != data['confirm_password']:
        flash("Passwords do not match!", "danger")
        return redirect(url_for('login_register'))
    
    data.pop('confirm_password')  # Remove confirm_password from data
    data['password'] = generate_password_hash(data['password'])  # Hash the password

    admin_model.create_admin_account(data)
    flash("Account created successfully!", "success")
    return redirect(url_for('login_register'))


@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    email = request.form['email']
    password = request.form['password']

    # Fetch user from respective collection
    user = admin_model.find_by_email(role, email)
    if not user or not check_password_hash(user['password'], password):
        flash("Invalid credentials!", "danger")
        return redirect(url_for('login_register'))

    # Save user to session and redirect
    session['user'] = str(user['_id'])
    session['username'] = user['first_name']+ " "+ user['last_name']
    session['role'] = role
    flash(f"Welcome, {user['first_name']}!", "success")
    return redirect(url_for('admin_dashboard') if role == 'admin' else url_for('/login'))


@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login_register'))
    else:
        print(session.get('user'))
        active_tab = request.args.get('active_tab', 'overview')
        if active_tab == 'student':
            courses = admin_model.get_courses()
            course_list = [f"{course['course_id']} - {course['course_title']}" for course in courses]
            return render_template('admin_dashboard.html', active_tab=active_tab, courses = course_list)
        elif active_tab == 'section':
            courses = admin_model.get_courses()
            course_list = [f"{course['course_id']} - {course['course_title']}" for course in courses]
            students = admin_model.get_students()
            student_list = [f"{student['first_name']+" "+ student['last_name']}" for student in students]
            return render_template('admin_dashboard.html', active_tab=active_tab, courses = course_list, students = student_list)
        elif active_tab == 'instructor':
            sections = admin_model.get_sections()
            section_list = [f"{section['section_id']}" for section in sections]
            return render_template('admin_dashboard.html', active_tab=active_tab, sections = section_list)
        
        courses = list(admin_model.get_courses())
        students = list(admin_model.get_students())
        sections = list(admin_model.get_sections())
        instructors = list(admin_model.get_instructors())
        return render_template('admin_dashboard.html', active_tab=active_tab, courses = courses, students = students, sections = sections, instructors = instructors)

@app.route('/create_instructor', methods=['POST'])
def create_instructor():
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('create_instructor'))

        hashed_password = generate_password_hash(request.form['password'])
        data = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "email": request.form['email'],
            "phone_number": request.form['phone_number'],
            "password": hashed_password,
            "sections": request.form.getlist('list_of_sections')
        }
        admin_model.create_instructor(data)
        flash("Instructor created successfully!", "success")
        return redirect(url_for('admin_dashboard', active_tab='overview'))
    return render_template(url_for('admin_dashboard', active_tab='overview'))



@app.route('/create_student', methods=['POST', 'GET'])
def create_student():
    if request.method == 'POST':
        # Validation
        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('create_student'))

        hashed_password = generate_password_hash(request.form['password'])
        data = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "email": request.form['email'],
            "phone_number": request.form['phone_number'],
            "password": hashed_password,
            "enrolled_courses": request.form.getlist('enrolled_courses')
        }
        admin_model.create_student(data)
        flash("Student created successfully!", "success")
        return redirect(url_for('admin_dashboard', active_tab='overview'))
    return render_template(url_for('admin_dashboard', active_tab='overview'))


@app.route('/create_course', methods=['POST'])
def create_course():
    if request.method == 'POST':
        data = {
            "course_id": "C"+request.form['course_id'],
            "course_title": request.form['course_title'],
            "course_description": request.form['course_description'],
        }
        admin_model.create_course(data)
        flash("Course created successfully!", "success")
        return redirect(url_for('admin_dashboard', active_tab='overview'))
    return redirect(url_for('admin_dashboard', active_tab='overview'))



@app.route('/create_section', methods=['POST'])
def create_section():
    if request.method == 'POST':
        data = {
            "section_id": request.form['section_id'],
            "semester_year": request.form['semester_year'],
            "enrollment_start_date": request.form['course_start_date'],
            "enrollment_end_date": request.form['course_end_date'],
            "course_id": request.form['course_id'],
            "students": request.form.getlist('list_of_students')
        }
        admin_model.create_section(data)
        flash("Section created successfully!", "success")
        return redirect(url_for('admin_dashboard', active_tab='overview'))
    return redirect(url_for('admin_dashboard', active_tab='overview'))


@app.route('/edit-record/<collection>/<record_id>', methods=['GET', 'POST'])
def edit_record(collection, record_id):
    if request.method == 'POST':
        # Fetch the updated data from the form
        updated_data = request.form.to_dict()

        # Update the record in the specified collection
        # admin_model.collection.update_one({"_id": ObjectId(record_id)}, {"$set": updated_data})
        admin_model.update_record(collection, ObjectId(record_id), updated_data)
        flash(f"Record updated successfully in {collection}.", "success")
        return redirect(url_for('admin_dashboard', active_tab='overview'))

    # Fetch the record to edit
    record = admin_model.find_one(collection,ObjectId(record_id))
    return render_template('edit_record.html', record=record, collection=collection)



@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('login_register'))

@app.route('/delete-record/<collection>/<record_id>', methods=['POST'])
def delete_record(collection, record_id):
    admin_model.delete_record(collection, ObjectId(record_id))
    flash(f"Record deleted successfully from {collection}.", "success")
    return admin_dashboard()


if __name__ == '__main__':
    app.run(debug=True)
