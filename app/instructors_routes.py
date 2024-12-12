from flask import *
from werkzeug.security import *
from app import mongo
from .models import *
from bson import ObjectId
from .mongo_queries import *



main = Blueprint('main', __name__)


@main.route("/instructor_dashboard", methods=['GET', 'POST'])
def instructor_dashboard():
    if request.method == 'POST':
        instructor_id = session['user']
        instructor = find_by_id('instructor', ObjectId(instructor_id))
        if instructor:
            return render_template('instructor.html', instructor=instructor)
        else:
            return "Instructor not found"
    return render_template('instructor.html')

@main.route("/get_courses", methods=['GET'])
def get_courses():
    semester_year = request.args.get('semester_year')
    if not semester_year:
        return jsonify({"error": "Semester year is required"}), 400
    courses = mongo.db.sections.aggregate(sections_query(semester_year))
    return list(courses)

@main.route("/get_sections", methods=['GET'])
def get_sections():
    course_id = request.args.get('course_id')
    semester_year = request.args.get('semester_year')
    if not course_id or not semester_year:
        return jsonify({"error": "Course ID and semester_year is required"}), 400
    sections = mongo.db.sections.find({'course_id': course_id, 'semester_year': semester_year})
    return list(sections)

@main.route('/register_course', methods=['POST'])
def register_course():
    instructor_id = session['user']
    print(request.form.to_dict())
    return jsonify({"message": "Course registered successfully"})