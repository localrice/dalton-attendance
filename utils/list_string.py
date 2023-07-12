def list_to_string(list):
    return ','.join(map(str, list))

def string_to_list(string):
    return list(map(int, string[0].split(',')))