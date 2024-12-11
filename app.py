from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from model.admin import AdminModel
from model.instructor import InstructorModel
from model.student import StudentModel
from collections import defaultdict
from utils.generate_session_cookie import generate_session_cookie
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
app.config['SESSION_COOKIE_NAME'] = generate_session_cookie()
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 

# initialize the MongoDB connection
admin_model = AdminModel()
instructor_model = InstructorModel()
student_model = StudentModel()

# Define the directory to store uploaded files
UPLOAD_FOLDER = 'course_material'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ASSIGNMENTS_FOLDER = os.path.join("instructor")
os.makedirs(ASSIGNMENTS_FOLDER, exist_ok=True)


STUDENT_ASSIGNMENTS_FOLDER = os.path.join("student", "completed_assignments")
os.makedirs(STUDENT_ASSIGNMENTS_FOLDER, exist_ok=True)




@app.route('/')
def login_register():
    if 'username' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'instructors':
            return redirect(url_for('instructor_dashboard'))
        elif session['role'] == 'students':
            return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid role!", "danger")
            return render_template('login_register.html')
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
    enrolled_courses = user.get('enrolled_courses')
    if role == 'students' and enrolled_courses:
        session['enrolled_courses'] = enrolled_courses
    
    flash(f"Welcome, {user['first_name']}!", "success")
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'instructors':
        if user['password_changed'] == 0:
            flash("Please change your password!", "warning")
            return redirect(url_for('change_password'))
        return redirect(url_for('instructor_dashboard'))
    elif role == 'students':
        if user['password_changed'] == 0:
            flash("Please change your password!", "warning")
            return redirect(url_for('change_password'))
        return redirect(url_for('student_dashboard'))
    else:
        flash("Invalid role!", "danger")
        return redirect(url_for('login_register'))
    

@app.route('/change_password', methods=['POST', 'GET'])
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        if request.form['new_password'] != request.form['confirm_password']:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('change_password'))
        user = admin_model.find_one(session.get('role'), ObjectId(session.get('user')))
        if not check_password_hash(user['password'], old_password):
            flash("Invalid old password!", "danger")
            return redirect(url_for('change_password'))
        
        hashed_password = generate_password_hash(request.form['new_password'])
        data = {
            "password": hashed_password,
            "password_changed": 1
        }
        admin_model.update_record(session.get('role'), ObjectId(session.get('user')), data)
        flash("Password changed successfully!", "success")
        # login with new password
        return redirect(url_for('login_register'))
    return render_template('change_password.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login_register'))
    else:
        active_tab = request.args.get('active_tab', 'overview')
        if active_tab == 'student':
            courses = list(admin_model.get_courses())
            return render_template('admin_dashboard.html', active_tab=active_tab, courses = courses)
        elif active_tab == 'section':
            courses = list(admin_model.get_courses())
            students = list(admin_model.get_students())
            return render_template('admin_dashboard.html', active_tab=active_tab, courses = courses, students = students)
        elif active_tab == 'instructor':
            sections = list(admin_model.get_sections())
            return render_template('admin_dashboard.html', active_tab=active_tab, sections = sections)
        
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
            "password_changed": 0 # Set password_changed to 0 at registration

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
            "password_changed": 0,  # Set password_changed to 0 at registration
        }
        admin_model.create_student(data)
        flash("Student created successfully!", "success")
        return redirect(url_for('admin_dashboard', active_tab='overview'))
    return render_template(url_for('admin_dashboard', active_tab='overview'))


@app.route('/create_course', methods=['POST'])
def create_course():
    if request.method == 'POST':
        data = {
            "course_id": request.form['course_id'],
            "course_title": request.form['course_title'],
            "course_description": request.form['course_description'],
            "credit_hours": request.form['credit_hours'],
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
            "course_id": request.form['course_id']  
        }
        admin_model.create_section(data)
        flash("Section created successfully!", "success")
        return redirect(url_for('admin_dashboard', active_tab='overview'))
    return redirect(url_for('admin_dashboard', active_tab='overview'))


@app.route('/edit-record/<collection>/<record_id>', methods=['GET', 'POST'])
def edit_record(collection, record_id):
    if request.method == 'POST':
        updated_data = request.form.to_dict()
        admin_model.update_record(collection, ObjectId(record_id), updated_data)
        flash(f"Record updated successfully in {collection}.", "success")
        return redirect(url_for('admin_dashboard', active_tab='overview'))

    # Fetch the record to edit
    record = admin_model.find_one(collection,ObjectId(record_id))
    return render_template('edit_record.html', record=record, collection=collection)

def get_available_courses():
    available_sections = list(instructor_model.get_available_sections_and_courses(session.get('user')))
    couses_sections = []
    for course in available_sections:
        course_details ={}
        course_details['course_id'] = course['sectionDetails'][0]['course_id']
        course_details['section_id'] = course['sectionDetails'][0]['section_id']
        couses_sections.append(course_details)
    return couses_sections

def get_instructor_dashboard(instructor_id):
    instructor_data = instructor_model.instructor_dashboard(instructor_id)
    groupd_data = defaultdict(lambda: {'students': []})
    for result in instructor_data:
        section_id = result['sectionDetails']['section_id']
        course_id = result['courseDetails'][0]['course_id']
        key = (section_id, course_id)
        student_name = f"{result['studentDetails'][0]['first_name']} {result['studentDetails'][0]['last_name']}"
        groupd_data[key]['section_id'] = section_id
        groupd_data[key]['course_id'] = course_id
        groupd_data[key]['students'].append(student_name)
    groupd_data_list = [{'section_id': key[0], 'course_id': key[1], 'students': value['students']} for key, value in groupd_data.items()]
    return groupd_data_list



@app.route("/instructor_dashboard")
def instructor_dashboard():
    if session.get('role') != 'instructors' and 'username' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login_register'))
    else:
        instructor_id = session.get('user')
        groupd_data_list = get_instructor_dashboard(instructor_id)
        course_material = instructor_model.get_course_material(instructor_id)
        assignments = instructor_model.get_assignments(instructor_id)
        submitted_assignments = instructor_model.get_submitted_assignments(instructor_id)
        return render_template('instructor_dashboard.html', grouped_data=groupd_data_list,course_material=course_material, assignment_material=assignments, submitted_assignments=submitted_assignments, username = session.get('username').capitalize())


@app.route('/upload_course_material', methods=['GET', 'POST'])
def upload_course_material():
    if 'username' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login_register'))
    else:
        if request.method == 'POST':
            files = request.files.getlist('attachments')
            uploaded_files = []
            for file in files:
                if file:
                    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(file_path)
                    uploaded_files.append(file.filename)

            # Save course material info to the database (example only)
            course_material = {
                'course_title': request.form['course_title'],
                'section': request.form['section'],
                'description': request.form['description'],
                'instructor_id': session.get('user'),
                'attachments': uploaded_files,
            }
            # Add to the database here
            instructor_model.create_course_material(course_material)
            flash('Course material uploaded successfully!', 'success')
            return redirect(url_for('instructor_dashboard'))

        # Fetch available sections and courses (replace with database query)
        couses_sections = get_available_courses()
        return render_template('upload_course_material.html', sections=couses_sections)

@app.route('/instructor/create_assignment', methods=['GET', 'POST'])
def instructor_create_assignment():
    if 'username' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login_register'))
    else:
        if request.method == 'POST':
            files = request.files.getlist('attachments')
            uploaded_files = []
            for file in files:
                if file:
                    file_path = os.path.join(ASSIGNMENTS_FOLDER, file.filename)
                    file.save(file_path)
                    uploaded_files.append(file.filename)

            # Save the assignment details to the database
            assignment = {
                'assignment_title': request.form['assignment_title'],
                'section_id': request.form['section_id'],
                'due_date': request.form['due_date'],
                'description': request.form['description'],
                'instructor_id': session.get('user'),
                "status": "open",
                'attachments': uploaded_files
            }
            instructor_model.create_assignment(assignment)
            # Add assignment to database (example only)
            flash('Assignment created successfully!', 'success')
            return redirect(url_for('instructor_dashboard'))

        # Fetch available sections for the instructor
        sections = get_available_courses()
        return render_template('create_assignment.html', sections=sections)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/student_dashboard")
def student_dashboard():
    if session.get('role') != 'students' and 'username' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login_register'))
    else:
        student_id = session.get('user')
        student_data = student_model.get_student(student_id)
        if session.get('enrolled_courses') is not None:
            student_assignments = student_model.get_assignments(session.get('enrolled_courses')[0])
            assignemnts = list(student_assignments)
            assignemnts =  [assign['assignmentDetail'] for assign in assignemnts][0]
            course_material = list(student_model.get_course_material(session.get('enrolled_courses')[0]))
            return render_template('student_dashboard.html', student_data=student_data,course_material=course_material ,assignmemts=assignemnts, username = session.get('username').capitalize())
        else:
            return render_template('student_dashboard.html', student_data=student_data, username = session.get('username').capitalize())

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "jpg", "png"}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/submit_assignment", methods=["POST"])
def submit_assignment():
    # Extract data from the form
    assignment_id = request.form.get("assignment_id")
    file = request.files.get("assignment")

    if file:
        print("submitting assignment")
        filename = secure_filename(file.filename)
        file_path = os.path.join(ASSIGNMENTS_FOLDER, 'completed', filename)
        
        result = student_model.submit_assignment(assignment_id, filename, student_id=session.get('user'))
        file.save(file_path)
        print("Assignment_id: "+ str(assignment_id))
        
        # Provide feedback to the user
        print("insert result: "+str(result))
        if result.modified_count > 0:
    
            flash("Assignment submitted successfully!", "success")
            print("Assignment submitted successfully!")
            return redirect(url_for("student_dashboard"))
        else:

            flash("Failed to submit the assignment. Please try again.", "danger")
            print("Failed to submit the assignment. Please try again.")
            return redirect(url_for("student_dashboard"))
    else:
        flash("Invalid file or no file uploaded. Allowed formats: pdf, docx, txt, jpg, png.", "danger")
        print("Invalid file or no file uploaded. Allowed formats: pdf, docx, txt, jpg, png.")
        return redirect(url_for("student_dashboard"))


# grade_assignment 
@app.route("/grade_assignment", methods=["POST"])
def grade_assignment():
    assignment_id = request.form.get("assignment_id")
    grade = request.form.get("grade")
    student_id = request.form.get("student_id")
    result = instructor_model.grade_assignment(assignment_id, student_id, grade)
    if result.modified_count > 0:
        flash("Assignment graded successfully!", "success")
    else:
        flash("Failed to grade the assignment. Please try again.", "danger")
    return redirect(url_for("instructor_dashboard"))

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
    app.run(debug=True, port=5001)
