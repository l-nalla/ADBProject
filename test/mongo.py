courses = [{'sectionDetails': [{'section_id': 'SEC102', 'course_id': 'C5510'}]},{'sectionDetails': [{'section_id': 'SEC102', 'course_id': 'C5510'}]}]

couses_sections = []
for course in courses:
    course_details ={}
    course_details['course_id'] = course['sectionDetails'][0]['course_id']
    course_details['section_id'] = course['sectionDetails'][0]['section_id']
    couses_sections.append(course_details)
print(couses_sections)
