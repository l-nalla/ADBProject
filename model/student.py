from utils.dbconnection import MongoDBConnection
from flask import Flask, request, jsonify
from model.mongo_queries.student_aggregations import student_assignments,get_course_material
from bson import ObjectId

class StudentModel:
    def __init__(self):
        self.db = MongoDBConnection().connect()

    def get_student(self, student_id):
        student = self.db.students.find_one({"_id": ObjectId(student_id)})
        return student
    
    def get_assignments(self, course_id):
        assignments = self.db.courses.aggregate(student_assignments(course_id))
        return assignments
    
    def submit_assignment(self, assignment_id, file_name, student_id):
        # print(str({"_id": ObjectId(assignment_id)}, {"$push": {"completed_file": file_name, "student_id": student_id}}))

        result = self.db.assignments.update_one({"_id": ObjectId(assignment_id)}, {"$set": {"completed_file": file_name, "student_id": student_id, "status": "submitted"}})
        return result

    def get_course_material(self, course_id):
        course_material = self.db.courses.aggregate(get_course_material(course_id))
        return course_material