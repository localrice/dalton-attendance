def sort_dict_by_id(dictionary):
    """
    This function takes a dictionary as the parameter and arranges each key in ascending order 
    according to the number that comes after the initial letter of the stream.

    The academic year must be removed from the student_id before passing it as a key
    """
    sorted_dict = dict(sorted(dictionary.items(), key=lambda x: int(''.join(filter(str.isdigit, x[0])))))
    return sorted_dict