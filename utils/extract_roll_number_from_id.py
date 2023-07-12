import re

def remove_number_from_end(input_string):
    """
    Removes any numbers from the end.
    used in extract_roll_number_from_id() func to remove the academic years from the end.
    """
    pattern = r'\d+$'
    result = re.sub(pattern, '', input_string)
    return result

def extract_roll_number_from_id(student_id):
    """
    Function that extracts the roll number from the student id
    """
    id_without_year = remove_number_from_end(student_id)
    pattern = r'\d+'
    match = re.search(pattern, id_without_year)
    if match:
        return match.group()
    else:
        return None