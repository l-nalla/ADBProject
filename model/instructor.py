from utils.dbconnection import MongoDBConnection
from model.mongo_queries.instructor_aggregations import instructor_dashboard_pipeline, get_section_and_courses, get_submitted_assginments
from flask import jsonify
from bson import ObjectId


class InstructorModel:
    def __init__(self):
        self.db = MongoDBConnection().connect()

    def instructor_dashboard(self, instructorId):
        result = self.db.instructors.aggregate(instructor_dashboard_pipeline(instructorId))
        return result
    
    def create_course_material(self, course_material):
        result = self.db.course_materials.insert_one(course_material)
        return result
    
    def get_course_material(self, instructor_id):
        result = self.db.course_materials.find({"instructor_id": instructor_id})
        return result
    
    def get_available_sections_and_courses(self, instructor_id):
        return self.db.instructors.aggregate(get_section_and_courses(instructor_id))
    
    def create_assignment(self, assignment):
        result = self.db.assignments.insert_one(assignment)
        return result
    
    def get_assignments(self, instructor_id):
        result = self.db.assignments.find({"instructor_id": instructor_id})
        return result
    
        
    def get_submitted_assignments(self, instructor_id):
        result = self.db.assignments.aggregate(get_submitted_assginments(instructor_id))
        return result
    
    def grade_assignment(self, assignment_id, studnet_id, grade):
        result = self.db.students.update_one({"_id": ObjectId(studnet_id)}, {"$set": {"gpa": grade}})
        return result