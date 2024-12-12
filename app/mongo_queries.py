def sections_query(semester_year):
    return [
    {
        "$match": {"semester_year": semester_year}  # Filter by semester_year
    },
    {
        "$lookup": {
            "from": "courses",
            "localField": "course_id",
            "foreignField": "course_id",
            "as": "courseDetails"
        }
    },
    {
        "$unwind": "$courseDetails"
    },
    {
        "$project": {
            "_id": { "$toString": "$_id" },
            "section_id": 1,
            "semester_year": 1,
            "course_id": 1,
            "course_uid": { "$toString": "$courseDetails._id" },
            "course_title": "$courseDetails.course_title",
            "course_description": "$courseDetails.course_description"
        }
    }
]