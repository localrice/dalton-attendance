def sort_dict_by_id(dictionary):
    """
    This function takes a dictionary as the parameter and arranges each key in ascending order 
    according to the number that comes after the initial letter of the stream(A or S or C)
    """
    sorted_dict = dict(sorted(dictionary.items(), key=lambda x: int(''.join(filter(str.isdigit, x[0].lstrip('ASC'))))))
    return sorted_dict