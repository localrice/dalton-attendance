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
def extract_student_details(student_id):
    stream = student_id[0]  # First letter represents the stream (C, S, or A)
    # finds the position of the first non-digit character after the stream
    non_digit_index = next((i for i, char in enumerate(student_id[1:]) if not char.isdigit()), None)

    # Extract the roll number based on the position of the first non-digit character
    roll_number = int(student_id[1:non_digit_index + 1])

    # Extract the name initials after the roll number
    name_initials = student_id[non_digit_index + 1:-4]

    # Extract the academic year span (last 4 digits)
    academic_year_span = student_id[-4:]

    return stream, roll_number, name_initials, academic_year_span