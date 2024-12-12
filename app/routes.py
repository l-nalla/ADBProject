from flask import *
from werkzeug.security import *
from app import mongo
from .models import *
from bson import ObjectId
from .mongo_queries import *

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'course_material'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ASSIGNMENTS_FOLDER = os.path.join("instructor")
os.makedirs(ASSIGNMENTS_FOLDER, exist_ok=True)

@main.route('/')
def login_register():
    if 'username' in session:
        if session['role'] == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif session['role'] == 'instructors':
            return redirect(url_for('main.instructor_dashboard'))
        elif session['role'] == 'students':
            return redirect(url_for('main.student_dashboard'))
        else:
            flash("Invalid role!", "danger")
            return render_template('login_register.html')
    return render_template('login_register.html')


@main.route('/login', methods=['POST'])
def login():
    role, email, password = request.form['role'], request.form['email'], request.form['password']
    user = find_by_email(role, email)
    if not user or not check_password_hash(user['password'], password):
        flash("Invalid email or password!", "danger")
        return redirect(url_for('main.login_register'))
    session['user'], session['role'], session['username'] = str(user['_id']), role, user['first_name'] + ' ' + user['last_name']

    if role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif role == 'instructors':
        if user['password_changed'] == 0:
            flash("Please change your password!", "warning")
            return redirect(url_for('main.change_password'))
        return redirect(url_for('main.instructor_dashboard'))
    elif role == 'students':
        if user['password_changed'] == 0:
            flash("Please change your password!", "warning")
            return redirect(url_for('main.change_password'))
        return redirect(url_for('main.student_dashboard'))
    else:
        flash("Invalid role!", "danger")
        return redirect(url_for('main.login_register'))
    

@main.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password, new_password, confirm_password = request.form['old_password'], request.form['new_password'], request.form['confirm_password']
        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('main.change_password'))
        user = find_by_id(session['role'], ObjectId(session['user']))
        if not check_password_hash(user['password'], old_password):
            flash("Invalid password!", "danger")
            return redirect(url_for('main.change_password'))
        data = {'password': generate_password_hash(new_password), 'password_changed': 1}
        update_by_id(session['role'], ObjectId(session['user']), data)
        flash("Password changed successfully!", "success")
        return redirect(url_for('main.login_register'))
    return render_template('change_password.html')


@main.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        flash("Check credentials or role", "danger")
        return redirect(url_for('main.login_register'))
    else:
        active_tab = request.args.get('active_tab', 'overview')
        courses = get_all('courses')
        students = get_all('students')
        instructors = get_all('instructors')
        sections = get_all('sections')
        if active_tab == 'student':
            return render_template('admin_dashboard.html', active_tab=active_tab)
        elif active_tab == 'instructor':
            return render_template('admin_dashboard.html', active_tab=active_tab)
        elif active_tab == 'section':
            return render_template('admin_dashboard.html', active_tab=active_tab, courses=courses)
        elif active_tab == 'course':
            return render_template('admin_dashboard.html', active_tab=active_tab)
        return render_template('admin_dashboard.html', active_tab=active_tab, courses=courses, students=students, instructors=instructors, sections=sections)
    
@main.route('/edit_record/<collection>/<record_id>', methods=['GET', 'POST'])
def edit_record(collection, record_id):
    if 'username' not in session or session['role'] != 'admin':
        flash("Check credentials or role", "danger")
        return redirect(url_for('main.login_register'))
    if request.method == 'POST':
        data = request.form.to_dict()
        update_by_id(collection, ObjectId(record_id), data)
        flash("Record updated successfully!", "success")
        return redirect(url_for('main.admin_dashboard'))
    record = find_by_id(collection, ObjectId(record_id))
    return render_template('edit_record.html', record=record, collection=collection)

@main.route('/create_instructor', methods=['GET', 'POST'])
def create_instructor():
    if 'username' not in session or session['role'] != 'admin':
        flash("Check credentials or role", "danger")
        return redirect(url_for('main.login_register'))
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('main.create_instructor'))
        data = request.form.to_dict()
        data.pop('confirm_password')
        data['password'] = generate_password_hash(data['password'])
        data['password_changed'] = 0
        mongo.db['instructors'].insert_one(data)
        flash("Instructor created successfully!", "success")
        return redirect(url_for('main.admin_dashboard', active_tab='overview'))
    return redirect(url_for('main.admin_dashboard', active_tab='overview'))


@main.route('/create_student', methods=['GET', 'POST'])
def create_student():
    if 'username' not in session or session['role'] != 'admin':
        flash("Check credentials or role", "danger")
        return redirect(url_for('main.login_register'))
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('main.create_student'))
        data = request.form.to_dict()
        data.pop('confirm_password')
        data['password'] = generate_password_hash(data['password'])
        data['password_changed'] = 0
        mongo.db['students'].insert_one(data)
        flash("Student created successfully!", "success")
        return redirect(url_for('main.admin_dashboard', active_tab='overview'))
    return redirect(url_for('main.admin_dashboard', active_tab='overview'))


@main.route('/create_course', methods=['GET', 'POST'])
def create_course():
    if 'username' not in session or session['role'] != 'admin':
        flash("Check credentials or role", "danger")
        return redirect(url_for('main.login_register'))
    if request.method == 'POST':
        data = request.form.to_dict()
        mongo.db['courses'].insert_one(data)
        flash("Course created successfully!", "success")
        return redirect(url_for('main.admin_dashboard', active_tab='overview'))
    return redirect(url_for('main.admin_dashboard', active_tab='overview'))


@main.route('/create_section', methods=['GET', 'POST'])
def create_section():
    if 'username' not in session or session['role'] != 'admin':
        flash("Check credentials or role", "danger")
        return redirect(url_for('main.login_register'))
    if request.method == 'POST':
        data = request.form.to_dict()
        mongo.db['sections'].insert_one(data)
        flash("Section created successfully!", "success")
        return redirect(url_for('main.admin_dashboard', active_tab='overview'))
    return redirect(url_for('main.admin_dashboard', active_tab='overview'))



@main.route("/instructor_dashboard", methods=['GET', 'POST'])
def instructor_dashboard():
    if 'username' not in session or session['role'] != 'instructors':
        flash("Check credentials or role", "danger")
        return redirect(url_for('main.login_register'))
    instructor_id = session.get('user')
    print("prongin instructor id")
    print("instructor_id:  ", instructor_id)
    collection = session.get('role')
    instructor = find_by_id(collection, ObjectId(instructor_id))
    print("printing instructor")
    print(list(instructor))
    sections = mongo.db[collection].aggregate([
    {
        "$unwind": "$sections"
    },
    {
        "$match": {
            "_id": ObjectId(instructor_id),
            
        }
    },
    {
        "$project": {
            "section": "$sections.section_id",
            "semester_year": "$sections.semester_year",
            "course_id": "$sections.course_id",
        }
    }
    ]
    )
    if instructor:
        return render_template('instructor.html', instructor=instructor, sections=sections)
    else:
        return "Instructor not found"

@main.route("/get_courses", methods=['GET'])
def get_courses():
    semester_year = request.args.get('semester_year')
    if not semester_year:
        return jsonify({"error": "Semester year is required"}), 400
    courses = mongo.db.sections.aggregate(sections_query(semester_year))
    return jsonify({"courses": list(courses)})

@main.route("/get_sections", methods=['GET'])
def get_sections():
    course_id = request.args.get('course_id')
    semester_year = request.args.get('semester_year')
    if not course_id or not semester_year:
        return jsonify({"error": "Course ID and semester_year is required"}), 400

    # Fetch the instructor's current registration for the selected semester_year
    instructor_registration = mongo.db.registrations.find_one({
        "instructor_id": session['user'],
        "semester_year": semester_year
    })

    # Initialize the list of sections
    sections = mongo.db.sections.find({
        "course_id": course_id,
        "semester_year": semester_year  # Filter sections based on the selected course and semester_year
    })


    sections = mongo.db.sections.find({'course_id': course_id, 'semester_year': semester_year},{"_id": {"$toString": "$_id"}, "section_id": 1, "semester_year": 1, "course_id": 1})
    return jsonify({"sections": list(sections)})

@main.route('/register_course', methods=['POST'])
def register_course():
    instructor_id = session['user']
    course_id = request.form['course_id']
    semester_year = request.form['semester_year']
    section_id = request.form['section_id']
    exist_course = mongo.db.instructors.aggregate([
    {
        "$unwind": "$sections"
    },
    {
        "$match": {
            "_id": ObjectId(instructor_id),
            "sections.semester_year": semester_year,
            "sections.course_id": course_id,
            "sections.section_id": section_id
        }
    },
    {
        "$project": {
            "_id": 0,
            "section": "$sections.section_id",
            "semester_year": "$sections.semester_year",
            "course_id": "$sections.course_id",
        }
    }
    ]
    )
    if len(list(exist_course))>0:
        return jsonify({"message": "Course / section already registered"})
    else:
        mongo.db['instructors'].update_one({'_id': ObjectId(instructor_id)}, {'$push': {'sections': request.form.to_dict()}})
    return jsonify({"message": "Course registered successfully"})

@main.route('/get_instructor_registered_section', methods=['GET'])
def get_instructor_registered_section():
    instructor_id = session.get('user')
    sections = mongo.db.instructors.aggregate(
        {
            "$unwind": "$sections"
        },
        {
            "$match": {
                "_id": ObjectId(instructor_id),
                
            }
        },
        {
            "$project": {
                "section": "$sections.section_id",
                "semester_year": "$sections.semester_year",
                "course_id": "$sections.course_id",
            }
        }

        )
    return list(sections)



@main.route('/register_course_student', methods=['POST'])
def register_course_student():    
    student_id = session['user']
    course_id = request.form['course_id']
    semester_year = request.form['semester_year']
    exist_course = mongo.db.students.aggregate([
    {
        "$unwind": "$sections"
    },
    {
        "$match": {
            "_id": ObjectId(student_id),
            "sections.semester_year": semester_year,
            "sections.course_id": course_id
        }
    },
    {
        "$project": {
            "_id": 0,
            "section": "$sections.section_id",
            "semester_year": "$sections.semester_year",
            "course_id": "$sections.course_id",
        }
    }
    ]
    )
    if len(list(exist_course))>0:
        return jsonify({"message": "Course already registered"})
    else:
        mongo.db['students'].update_one({'_id': ObjectId(student_id)}, {'$push': {'sections': request.form.to_dict()}})
    return jsonify({"message": "Course registered successfully"})

@main.route("/student_dashboard", methods=['GET', 'POST'])
def student_dashboard():
    if session.get('role') != 'students' and 'username' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.login_register'))
    else:
        student_id = session.get('user')
        collection = session.get('role')
        student_data = find_by_id(collection, ObjectId(student_id))
        sections =     mongo.db.students.aggregate([
            {
                "$unwind": "$sections"
            },
            {
                "$match": {
                    "_id": ObjectId(student_id),
                    
                }
            },
            {
                "$project": {
                    "section": "$sections.section_id",
                    "semester_year": "$sections.semester_year",
                    "course_id": "$sections.course_id",
                }
            }
            ]
            )
        return render_template('student_dashboard.html', student_data=student_data,sections=sections, username = session.get('username').capitalize())

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@main.route('/create_assignment', methods=['GET', 'POST'])
def create_assignment():
    if 'username' not in session or session.get('role') != 'instructors':
        flash("Check credentials or role", "danger")
        return redirect(url_for('main.login_register'))
    
    else:
        if request.method == 'POST':
            files = request.files.getlist('attachments')
            uploaded_files = []
            for file in files:
                if file:
                    file_path = os.path.join(ASSIGNMENTS_FOLDER, file.filename)
                    file.save(file_path)
                    uploaded_files.append(file.filename)
            section_id = request.form['section_id']
            # Save the assignment details to the database
            assignment = {
                'assignment_title': request.form['assignment_title'],
                'due_date': request.form['due_date'],
                'description': request.form['description'],
                'instructor_id': session.get('user'),
                "status": "open",
                'attachments': uploaded_files
            }
            print(assignment)
            print("section_id: ", section_id)
            insert_assignment(section_id, assignment)
            flash('Assignment created successfully!', 'success')
            return redirect(url_for('main.instructor_dashboard'))
        section_id = request.args.get('section_id')
        completed_assignments = list(mongo.db.sections.aggregate([
                        {"$unwind":"$completed_assignments"},
                        {
                        "$match": {
                        "section_id": section_id
                        }},
                        {
                        "$project": {
                            "_id": 0, 
                            "section_id": 1,
                            "student_name": "$completed_assignments.student_name",
                            "assignment_title": "$completed_assignments.assignment_title",
                            "student_uid": "$completed_assignments.student_id",
                            "description": "$completed_assignments.description",
                            "attachments": "$completed_assignments.attachments",
                        }}]) )
        # Fetch available sections for the instructor
        return render_template('create_assignment.html', section_id=section_id, completed_assignments=completed_assignments)


@main.route('/upload_course_material', methods=['GET', 'POST'])
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

            section_id = request.form['section_id']
            # Save course material info to the database (example only)
            course_material = {
                'course_title': request.form['course_title'],
                'description': request.form['description'],
                'instructor_id': session.get('user'),
                'attachments': uploaded_files,
            }
            # Add to the database here
            insert_course_material(section_id, course_material)
            flash('Course material uploaded successfully!', 'success')
            return redirect(url_for('main.instructor_dashboard'))
        section_id = request.args.get('section_id')
        # Fetch available sections and courses (replace with database query)
        return render_template('create_assignment.html', section_id=section_id)

@main.route('/view_assignments', methods=['GET', 'POST'])
def view_assignments():
    if 'username' not in session and session.get('role') != 'students':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.login_register'))
    else:
        section_id = request.args.get('section_id')
        assignments = mongo.db.sections.aggregate([
            {"$unwind":"$assignments"},
            {
                "$match": {
                    "section_id": section_id
                }
            },
            {
                "$lookup": {
                    "from": 'students',
                    "localField": 'section_id',
                    "foreignField": 'section_id',
                    "as": 'students'
                }
            },
            {
                "$project": {
                    "_id": 0,
                "assignment_title": "$assignments.assignment_title",
                "description": "$assignments.description",
                "due_date": "$assignments.due_date",
                "status": "$assignments.status",
                "attachments": "$assignments.attachments",
            }
            }

        ])
        course_materials = mongo.db.sections.aggregate([
            {"$unwind":"$course_materials"},
            {
                "$match": {
                    "section_id": section_id
                }
            },
            {
                "$lookup": {
                    "from": 'students',
                    "localField": 'section_id',
                    "foreignField": 'section_id',
                    "as": 'students'
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "title": "$course_materials.course_title",
                    "description": "$course_materials.description",
                    "attachments": "$course_materials.attachments",
                }
            }

        ])
        return render_template('view_assignments.html', assignments=list(assignments), course_materials=list(course_materials), section_id=section_id)

@main.route('/grade_assignment', methods=['POST'])
def grade_assignment():
    if 'username' not in session or session.get('role') != 'instructors':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.login_register'))
    else:
        student_id = request.form['student_id']
        grade = request.form['grade']
        assign_grade(student_id, grade)
        flash("Assignment graded successfully!", "success")
        return redirect(url_for('main.instructor_dashboard'))

@main.route('/submit_assignment', methods=['POST', 'GET'])
def submit_assignment():
    if 'username' not in session or session.get('role') != 'students':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.login_register'))
    else:
        files = request.files.getlist('attachments')
        uploaded_files = []
        for file in files:
            if file:
                file_path = os.path.join(ASSIGNMENTS_FOLDER, file.filename)
                file.save(file_path)
                uploaded_files.append(file.filename)
        
        student_id = session.get('user')
        submission = {
            "assignment_title": request.form['title'],
            'description': request.form['description'],
            'student_id': student_id,
            "student_name": session.get('username'),
            'attachments': uploaded_files
        }
        submit_completed_assignment(request.form['section_id'], submission)
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('main.student_dashboard'))


# forgot password functionality
@main.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']
        user = find_by_email(role, email)
        if not user:
            flash("Invalid email or Check role!", "danger")
            return redirect(url_for('main.forgot_password'))
        elif request.form['password'] != request.form['confirm_password']:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('main.forgot_password'))
        data = {'password': generate_password_hash(request.form['password'])}
        update_by_id(role, user['_id'], data)
        flash("Password changed successfully!!", "success")
        return redirect(url_for('main.login_register'))
    return render_template('forgot_password.html')

@main.route('/forgot_username', methods=['GET', 'POST'])
def forgot_username():
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        role = request.form['role']
        user = find_by_flname(role, fname, lname)
        if not user:
            flash("Invalid email or Check role!", "danger")
            return redirect(url_for('main.forgot_username'))
        flash(f"Your username is: {user['email']}", "success")
        return redirect(url_for('main.login_register'))
    return render_template('forgot_username.html')

@main.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('main.login_register'))