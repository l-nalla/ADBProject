
def student_assignments(course):
    return [
    {
        "$match": {
            "course_id": course
        }
    },
    {
        "$lookup": {
          "from": "sections",
          "localField": "course_id",
          "foreignField": "course_id",
          "as": "sectionDetail"
        }
    },
    { "$lookup": {
      "from": "assignments",
      "localField": "sectionDetail.section_id",
      "foreignField": "section_id",
      "as": "assignmentDetail"
    }},
    {
        "$project": {
            "_id"  : 0,
            "assignmentDetail._id": 1,
            "assignmentDetail.assignment_title": 1,
            "assignmentDetail.section_id": 1,
            "assignmentDetail.description": 1,
            "assignmentDetail.due_date": 1,
            "assignmentDetail.attachments": 1,
        }
    }
  
]


def get_course_material(course):
    return [
    {
        "$match": {
            "course_id": course
        }
    },
    {
    "$lookup": {
      "from": "course_materials",
      "localField": "course_id",
      "foreignField": "course_title",
      "as": "courseMaterials"
        }
    },
    { 
        "$unwind": "$courseMaterials"
    },
    {
        "$project": {
            "_id": 0,
            "course_id": 1,
            "course_title": 1,
            "description" : "$courseMaterials.description",
            "attachments" : "$courseMaterials.attachments"
        }
    }
  
]