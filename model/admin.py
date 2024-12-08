from utils.dbconnection import MongoDBConnection
from flask import Flask, request, jsonify


class AdminModel:
    def __init__(self):
        self.db = MongoDBConnection().connect()

    # create objects in mongo db collections
    def create_instructor(self, data):
        self.db.instructors.insert_one(data)
        return jsonify({"message": "Instructor created successfully!"})

    def create_student(self, data):
        self.db.students.insert_one(data)
        return jsonify({"message": "Student created successfully!"})
    
    def create_section(self, data):
        self.db.sections.insert_one(data)
        return jsonify({"message": "Section created successfully!"})
    
    def create_course(self, data):
        self.db.courses.insert_one(data)
        return jsonify({"message": "Course created successfully!"})
    
    # get objects from mongo db collections
    def get_instructors(self):
        instructors = self.db.instructors.find()
        return instructors
    
    def get_students(self):
        students = self.db.students.find()
        return students
    
    def get_sections(self):
        sections = self.db.sections.find()
        return sections
    
    def get_courses(self):
        courses = self.db.courses.find()
        return courses
    

    def delete_record(self, collection, record_id):
        self.db[collection].delete_one({"_id": record_id})
        return jsonify({"message": "Record deleted successfully!"})
    

    def find_one(self, collection, record_id):
        record = self.db[collection].find_one({"_id": record_id})
        return record
    
    def update_record(self, collection, record_id, updated_data):
        self.db[collection].update_one({"_id": record_id}, {"$set": updated_data})
        return jsonify({"message": "Record updated successfully!"})