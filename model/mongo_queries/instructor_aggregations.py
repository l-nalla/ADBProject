from bson import ObjectId

instructor_pipeline = [
    {"$unwind": "$sections"},  
    {
        "$addFields": {
            "sections": {"$toString": "$sections"} 
        }
    },
    {
        "$lookup": {
            "from": "sections",  
            "localField": "sections",
            "foreignField": "section_id",
            "as": "sectionDetails"  
        }
    },
    {
        "$unwind": "$sectionDetails"  
    },

    {
        "$project": {
            "_id": 1,
            "first_name": 1,
            "last_name": 1,
            "email": 1,
            "phone_number": 1,
            "section_id": "$sectionDetails.section_id" 
        }
    }
]

def instructor_dashboard_pipeline(instructorId):
    return  [
    {
        "$match": {
          "_id": ObjectId(instructorId)
        }
    },
    {
        "$unwind": "$sections"
    },
    {
        "$addFields": {"sections": { "$toString": "$sections"}}
    },
    {
        "$lookup": {
          "from": "sections",
          "localField": "sections",
          "foreignField": "section_id",
          "as": "sectionDetails"
        }
    },
    {
        "$unwind": "$sectionDetails"
    },
    {
        "$lookup": {
          "from": "courses",
          "localField": "sectionDetails.course_id",
          "foreignField": "course_id",
          "as": "courseDetails"
        }
    },
    {
        "$unwind": "$sectionDetails.students"
    },
    {"$addFields": {"studentId" : {"$toObjectId": "$sectionDetails.students"}}},
    {
        "$lookup": {
          "from": "students",
          "localField": "studentId",
          "foreignField": "_id",
          "as": "studentDetails"
        }
    },

    {
        "$project": {
          "_id": 0,
          "sectionDetails.section_id": 1,
          "courseDetails.course_id": 1,
          "studentDetails.first_name": 1,
          "studentDetails.last_name": 1,
        }
    }

]

def get_section_and_courses(instructor_id):
    return [
    {
        "$match": {
            "_id": ObjectId(instructor_id)
        }
    },
    {
        "$unwind": "$sections"
    },
    {
        "$addFields": {
          "sections": { "$toString": "$sections"}
        }
    },
    {
        "$lookup": {
            "from": "sections",
            "localField": "sections",
            "foreignField": "section_id",
            "as": "sectionDetails"
        }
    },
    {
        "$project": {
            "_id": 0,
            "sectionDetails.section_id": 1,
            "sectionDetails.course_id": 1
        }
    }
]


def get_submitted_assginments(instructor_id):
    return [
        {
            "$match": {
                "instructor_id": instructor_id,
                "status": "submitted"
            }
        }, 
        {
            "$addFields": { "student_id": { "$toObjectId": "$student_id" } }
        },
        {
            "$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "_id",
                "as": "student"
            }
        },
        {
            "$project": {
                "assignment_title": 1,
                "student_name":  { "$arrayElemAt": ["$student.first_name", 0] }, 
                "completed_file": 1,
                "status": 1,
                "student_id": 1,
            }
        }
    ]