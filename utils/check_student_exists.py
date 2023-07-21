from utils import extract_info

def check_student_exists(db,table_name, student_id):
    """
    This function takes table_name and student_id as the parameters
    and checks if the given student_id exists in the table .

    Also checks if the info such as roll no., stream and academic year is already present under a different name.
    """
    cursor = db.cursor()
    sql = f"SELECT 1 FROM {table_name} WHERE student_id = ?"
    cursor.execute(sql, (student_id,))
    row = cursor.fetchone()

    stream_initial, roll_number, name_initials, academic_year_span = extract_info.student_details(student_id)
    stream_dict = {'S': 'science', 'A': 'arts', 'C': 'commerce'}
    if stream_initial in stream_dict:
        stream = stream_dict[stream_initial]
    else:
        return ValueError
    cursor.execute(f'SELECT * FROM {table_name} WHERE stream = ? AND roll_no = ? AND academic_year_to = ?',
                   (stream, roll_number, academic_year_span,))
    count = cursor.fetchone()
    if row is None and count is not None: # if there's a student with the same roll no., stream and academic year, but different name
        return 1
    elif row is not None and count is not None: # if the student info already exists
        return 2
    else:
        return False
