from app import mongo
from bson import ObjectId

def find_by_email(role, email):
    return mongo.db[role].find_one({'email': email})

def find_by_id(role, user_id):
    return mongo.db[role].find_one({'_id': user_id})

def update_by_id(role, user_id, updated_data):
    mongo.db[role].update_one({'_id': user_id}, {'$set': updated_data})

def get_all(role):
    return mongo.db[role].find()

def find_by_flname(role, first_name, last_name):
    return mongo.db[role].find_one({'first_name': first_name, 'last_name': last_name},{"email":1, "_id":0})

def insert_assignment(section_id, assignment):
    return mongo.db.sections.update_one({"section_id": section_id}, {"$push": {"assignments": assignment}})

def insert_course_material(section_id, course_material):
    return mongo.db.sections.update_one({"section_id": section_id}, {"$push": {"course_materials": course_material}})

def submit_completed_assignment(section_id, completed_assignment):
    return mongo.db.sections.update_one({"section_id": section_id}, {"$push": {"completed_assignments": completed_assignment}})

def assign_grade( student_id, grade):
    return mongo.db.students.update_one({"_id": ObjectId(student_id)}, {"$set": {"grade": grade}})