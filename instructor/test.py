data = [{'assignmentDetail': [
    {'assignment_title': 'ADB assignment', 'section_id': 'SEC102', 'due_date': '2024-12-14', 'description': 'database assignment', 'attachments': ['Screenshot 2024-11-21 234622.png']},
    {'assignment_title': 'adb', 'section_id': 'SEC102', 'due_date': '2024-12-10', 'description': 'dsfrfretre', 'attachments': ['Online Return Center.pdf']}
]}]

d = [assign['assignmentDetail'] for assign in data][0]

print(d)