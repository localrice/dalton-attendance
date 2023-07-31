import ast


def process_result_from_query(input_str):
    '''
    takes in input of the result from fetching table and returns with a list of numbers
    '''
    try:
        parsed_data = ast.literal_eval(input_str)
        if isinstance(parsed_data, list):
            numbers_list = []
            for item in parsed_data:
                if isinstance(item, str) and ',' in item:
                    numbers_list.extend([int(num) for num in item.split(',')])
                else:
                    numbers_list.append(int(item))
            return numbers_list
        else:
            print("Input does not represent a list.")
            return None
    except (SyntaxError, ValueError):
        print("Invalid input format.")
        return None
